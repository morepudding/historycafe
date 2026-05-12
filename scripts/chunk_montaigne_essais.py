from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "authors" / "montaigne" / "works" / "essais"
RAW_DIR = WORK_DIR / "raw"
CHUNK_DIR = WORK_DIR / "chunks-michaud-modern"

AUTHOR_ID = "montaigne"
WORK_ID = "essais"
SOURCE_ID = "gutenberg_michaud_essais"
SOURCE_NAME = "Project Gutenberg"

INPUTS = [
    {
        "file": "gutenberg-48529.txt",
        "source_url": "https://www.gutenberg.org/ebooks/48529",
        "start": "CHAPITRE PREMIER.\n\n_Divers moyens mènent à même fin._",
        "initial_book": 1,
    },
    {
        "file": "gutenberg-49168.txt",
        "source_url": "https://www.gutenberg.org/ebooks/49168",
        "start": "CHAPITRE VII.\n\n_Des récompenses honorifiques._",
        "initial_book": 2,
    },
    {
        "file": "gutenberg-58801.txt",
        "source_url": "https://www.gutenberg.org/ebooks/58801",
        "start": "CHAPITRE XXXVI.\n\n_A quels hommes entre tous donner la prééminence._",
        "initial_book": 2,
    },
]

BOOK_LABELS = {
    "PREMIER": 1,
    "I": 1,
    "SECOND": 2,
    "II": 2,
    "TROISIEME": 3,
    "TROISIÈME": 3,
    "III": 3,
}


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_gutenberg_footer(text: str) -> str:
    marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    index = text.find(marker)
    if index >= 0:
        return text[:index]
    return text


def clean_line(line: str) -> str:
    line = line.strip()
    line = line.replace("\ufeff", "")
    return line


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
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "sans-titre"


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def find_translation_slice(text: str, start_marker: str) -> str:
    text = strip_gutenberg_footer(normalize_newlines(text))
    index = text.find(start_marker)
    if index < 0:
        raise ValueError(f"Start marker not found: {start_marker}")
    return text[index:]


def parse_book_number(line: str) -> int | None:
    cleaned = line.upper()
    cleaned = cleaned.replace("(TRADUCTION)", "")
    cleaned = cleaned.replace("(_SUITE_)", "")
    cleaned = cleaned.replace(".", "")
    parts = cleaned.split()
    if len(parts) < 2 or parts[0] != "LIVRE":
        return None
    return BOOK_LABELS.get(parts[1])


def is_chapter_heading(line: str) -> bool:
    return bool(re.fullmatch(r"CHAPITRE\s+[A-ZÉÈÎIVXLCDM]+\.?", line.upper()))


def parse_documents() -> list[dict[str, object]]:
    chapters: list[dict[str, object]] = []
    current_book: int | None = None
    chapter_counts = {1: 0, 2: 0, 3: 0}

    for item in INPUTS:
        raw_path = RAW_DIR / item["file"]
        text = raw_path.read_text(encoding="utf-8")
        sliced = find_translation_slice(text, item["start"])
        lines = [clean_line(line) for line in sliced.splitlines()]
        current_book = int(item["initial_book"])
        i = 0
        while i < len(lines):
            line = lines[i]
            book_number = parse_book_number(line)
            if book_number:
                current_book = book_number
                i += 1
                continue

            if current_book and is_chapter_heading(line):
                chapter_counts[current_book] += 1
                chapter_number = chapter_counts[current_book]
                chapter_heading_raw = line

                j = i + 1
                title = ""
                while j < len(lines):
                    candidate = lines[j].strip()
                    if candidate:
                        title = candidate.strip("_")
                        break
                    j += 1

                content_start = j + 1 if title else i + 1
                k = content_start
                body: list[str] = []
                while k < len(lines):
                    next_line = lines[k]
                    if parse_book_number(next_line) or is_chapter_heading(next_line):
                        break
                    body.append(next_line)
                    k += 1

                text_body = "\n".join(body).strip()
                if text_body:
                    chapters.append(
                        {
                            "book": current_book,
                            "chapter": chapter_number,
                            "chapter_heading_raw": chapter_heading_raw,
                            "chapter_title": title,
                            "text": text_body,
                            "source_file": item["file"],
                            "source_url": item["source_url"],
                        }
                    )
                i = k
                continue

            i += 1

    return chapters


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


def write_chunks(chapters: list[dict[str, object]]) -> int:
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    for chapter in chapters:
        book = int(chapter["book"])
        chapter_number = int(chapter["chapter"])
        title = str(chapter["chapter_title"])
        title_slug = slug(title)
        chapter_dir = CHUNK_DIR / f"livre-{book:02d}" / f"chapitre-{chapter_number:02d}-{title_slug}"
        chapter_dir.mkdir(parents=True, exist_ok=True)

        chunks = paragraph_chunks(str(chapter["text"]))
        for index, chunk_text in enumerate(chunks, start=1):
            chunk_id = f"{AUTHOR_ID}_{WORK_ID}_{book:02d}_{chapter_number:02d}_{index:03d}"
            filename = chapter_dir / f"{chunk_id}.md"
            frontmatter = [
                "---",
                f"chunk_id: {chunk_id}",
                f"author_id: {AUTHOR_ID}",
                f"work_id: {WORK_ID}",
                f"source_id: {SOURCE_ID}",
                f"source_name: {yaml_quote(SOURCE_NAME)}",
                f"source_url: {yaml_quote(str(chapter['source_url']))}",
                f"source_file: {yaml_quote(str(chapter['source_file']))}",
                "rights: public_domain",
                "language: fr",
                "text_layer: modern_french_translation",
                f"book: {book}",
                f"chapter: {chapter_number}",
                f"chapter_heading_raw: {yaml_quote(str(chapter['chapter_heading_raw']))}",
                f"chapter_title: {yaml_quote(title)}",
                f"chunk_index: {index}",
                f"chunk_count_in_chapter: {len(chunks)}",
                f"word_count: {word_count(chunk_text)}",
                "themes: []",
                "certainty: primary_source_translation",
                "---",
                "",
            ]
            filename.write_text("\n".join(frontmatter) + chunk_text + "\n", encoding="utf-8")
            written += 1
    return written


def main() -> None:
    chapters = parse_documents()
    count = write_chunks(chapters)
    by_book: dict[int, int] = {}
    for chapter in chapters:
        book = int(chapter["book"])
        by_book[book] = by_book.get(book, 0) + 1

    print(f"Parsed chapters: {len(chapters)}")
    for book in sorted(by_book):
        print(f"Book {book}: {by_book[book]} chapters")
    print(f"Written chunks: {count}")


if __name__ == "__main__":
    main()
