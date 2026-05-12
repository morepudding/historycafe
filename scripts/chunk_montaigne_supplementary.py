from __future__ import annotations

import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = "montaigne"


class TextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        classes = attrs_dict.get("class", "")
        if tag in {"script", "style"} or "ws-noexport" in classes or "noprint" in classes:
            self.skip_depth += 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        self.parts.append(data)


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def slug(value: str) -> str:
    value = value.lower()
    replacements = {
        "à": "a",
        "â": "a",
        "ä": "a",
        "ç": "c",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ÿ": "y",
        "œ": "oe",
        "æ": "ae",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-") or "sans-titre"


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def json_html_to_text(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if "parse" not in data:
        raise ValueError(f"No parse payload in {path}")
    html = data["parse"]["text"]
    parser = TextExtractor()
    parser.feed(html)
    text = unescape("".join(parser.parts))
    text = re.sub(r"\[\s*modifier\s*\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraph_chunks(text: str, max_words: int = 650) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for paragraph in paragraphs:
        paragraph_words = word_count(paragraph)
        if current and current_words + paragraph_words > max_words:
            chunks.append("\n\n".join(current))
            current = []
            current_words = 0
        current.append(paragraph)
        current_words += paragraph_words

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def write_chunk_files(
    *,
    text: str,
    output_dir: Path,
    chunk_prefix: str,
    work_id: str,
    source_id: str,
    source_name: str,
    source_url: str,
    source_file: str,
    text_type: str,
    title: str,
    rights: str = "public_domain",
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks = paragraph_chunks(text)
    for index, chunk_text in enumerate(chunks, start=1):
        chunk_id = f"{chunk_prefix}_{index:03d}"
        filename = output_dir / f"{chunk_id}.md"
        frontmatter = [
            "---",
            f"chunk_id: {chunk_id}",
            f"author_id: {AUTHOR_ID}",
            f"work_id: {work_id}",
            f"source_id: {source_id}",
            f"source_name: {yaml_quote(source_name)}",
            f"source_url: {yaml_quote(source_url)}",
            f"source_file: {yaml_quote(source_file)}",
            f"rights: {rights}",
            "language: fr",
            f"text_type: {text_type}",
            f"title: {yaml_quote(title)}",
            f"chunk_index: {index}",
            f"chunk_count: {len(chunks)}",
            f"word_count: {word_count(chunk_text)}",
            "themes: []",
            "---",
            "",
        ]
        filename.write_text("\n".join(frontmatter) + chunk_text + "\n", encoding="utf-8")
    return len(chunks)


def extract_bouillet_montaigne(text: str) -> str:
    start = text.find("MONTAIGNE")
    if start < 0:
        return text
    tail = text[start:]
    next_entry = tail.find("MONTAIGU", 20)
    if next_entry > 0:
        return tail[:next_entry].strip()
    return tail.strip()


def main() -> None:
    imports = [
        {
            "json": ROOT
            / "authors/montaigne/works/journal-de-voyage/raw/wikisource-journal.parse.json",
            "output": ROOT / "authors/montaigne/works/journal-de-voyage/chunks",
            "prefix": "montaigne_journal_voyage",
            "work_id": "journal-de-voyage",
            "source_id": "wikisource_journal_voyage",
            "source_name": "Wikisource",
            "source_url": "https://fr.wikisource.org/wiki/Journal_du_voyage_de_Montaigne/Texte_du_journal",
            "source_file": "wikisource-journal.parse.json",
            "text_type": "primary_text",
            "title": "Journal du voyage de Montaigne",
        },
        {
            "json": ROOT
            / "authors/montaigne/correspondence/raw/wikisource-lettre-montaigne-la-boetie.parse.json",
            "output": ROOT / "authors/montaigne/correspondence/chunks/lettre-mort-la-boetie",
            "prefix": "montaigne_lettre_la_boetie",
            "work_id": "correspondence",
            "source_id": "wikisource_lettre_mort_la_boetie",
            "source_name": "Wikisource",
            "source_url": "https://fr.wikisource.org/wiki/Discours_de_la_servitude_volontaire/%C3%89dition_1922/Lettre_de_Montaigne",
            "source_file": "wikisource-lettre-montaigne-la-boetie.parse.json",
            "text_type": "letter",
            "title": "Lettre de Montaigne sur la mort de La Boetie",
        },
        {
            "json": ROOT / "authors/montaigne/biographies/raw/wikisource-villemain-eloge.parse.json",
            "output": ROOT / "authors/montaigne/biographies/chunks/villemain-eloge",
            "prefix": "montaigne_bio_villemain_eloge",
            "work_id": "biographies",
            "source_id": "wikisource_villemain_eloge_montaigne",
            "source_name": "Wikisource",
            "source_url": "https://fr.wikisource.org/wiki/Discours_et_m%C3%A9langes_litt%C3%A9raires/%C3%89loge_de_Montaigne",
            "source_file": "wikisource-villemain-eloge.parse.json",
            "text_type": "secondary_text",
            "title": "Eloge de Montaigne",
        },
        {
            "json": ROOT
            / "authors/montaigne/biographies/raw/wikisource-hoffding-montaigne-charron.parse.json",
            "output": ROOT / "authors/montaigne/biographies/chunks/hoffding-montaigne-charron",
            "prefix": "montaigne_bio_hoffding_charron",
            "work_id": "biographies",
            "source_id": "wikisource_hoffding_montaigne_charron",
            "source_name": "Wikisource",
            "source_url": "https://fr.wikisource.org/wiki/Histoire_de_la_philosophie_moderne/Livre_1/Chapitre_4",
            "source_file": "wikisource-hoffding-montaigne-charron.parse.json",
            "text_type": "secondary_text",
            "title": "Michel de Montaigne et Pierre Charron",
        },
        {
            "json": ROOT / "authors/montaigne/biographies/raw/wikisource-bouillet-m-page.parse.json",
            "output": ROOT / "authors/montaigne/biographies/chunks/bouillet-notice",
            "prefix": "montaigne_bio_bouillet_notice",
            "work_id": "biographies",
            "source_id": "wikisource_bouillet_montaigne_notice",
            "source_name": "Wikisource",
            "source_url": "https://fr.wikisource.org/wiki/Dictionnaire_universel_d%E2%80%99histoire_et_de_g%C3%A9ographie_Bouillet_Chassang/Lettre_M-MILWAUKEE",
            "source_file": "wikisource-bouillet-m-page.parse.json",
            "text_type": "reference_notice",
            "title": "Notice Montaigne du dictionnaire Bouillet-Chassang",
            "transform": extract_bouillet_montaigne,
        },
    ]

    for item in imports:
        text = json_html_to_text(item["json"])
        transform = item.get("transform")
        if transform:
            text = transform(text)
        count = write_chunk_files(
            text=text,
            output_dir=item["output"],
            chunk_prefix=item["prefix"],
            work_id=item["work_id"],
            source_id=item["source_id"],
            source_name=item["source_name"],
            source_url=item["source_url"],
            source_file=item["source_file"],
            text_type=item["text_type"],
            title=item["title"],
        )
        print(f"{item['title']}: {count} chunks")


if __name__ == "__main__":
    main()
