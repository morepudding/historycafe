from __future__ import annotations

import re
from pathlib import Path

from chunk_montaigne_supplementary import json_html_to_text, paragraph_chunks, word_count, yaml_quote


ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "authors" / "montaigne" / "correspondence" / "raw" / "wikisource-en-letters.parse.json"
OUT_DIR = ROOT / "authors" / "montaigne" / "correspondence" / "chunks-en"

AUTHOR_ID = "montaigne"
WORK_ID = "correspondence"
SOURCE_ID = "wikisource_en_letters_1877"
SOURCE_NAME = "Wikisource EN"
SOURCE_URL = "https://en.wikisource.org/wiki/The_Essays_of_Montaigne/The_Letters_of_Montaigne"

ROMAN_RE = re.compile(r"^\s*([IVXLCDM]+)\.\s*$", re.MULTILINE)


LETTER_TITLES_FR = {
    "I": "A Monsieur de Montaigne, son pere, sur la mort de La Boetie",
    "II": "A Monsieur de Montaigne, son pere, dedicace de Raymond Sebond",
    "III": "A Monsieur de Lansac",
    "IV": "A Monsieur de Mesmes",
    "V": "A Monsieur de L'Hospital",
    "VI": "A Monsieur de Foix",
    "VII": "A sa femme",
    "VIII": "A Monsieur Dupuy",
    "IX": "Aux jurats de Bordeaux",
    "X": "Aux jurats de Bordeaux",
    "XI": "Aux jurats de Bordeaux",
    "XII": "Lettre politique attribuee a Montaigne",
    "XIII": "A Mademoiselle Paulmier",
    "XIV": "A Henri IV",
    "XV": "A Henri IV",
    "XVI": "Au gouverneur de Guyenne",
}


def extract_letters(text: str) -> list[dict[str, str]]:
    start = text.find("I.\n")
    if start < 0:
        raise ValueError("Could not find first letter marker")
    text = text[start:]
    matches = list(ROMAN_RE.finditer(text))
    letters: list[dict[str, str]] = []

    for index, match in enumerate(matches):
        roman = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end].strip()
        body = re.sub(r"^\[edit\]\s*", "", body)
        body = re.sub(r"\n\[edit\]\n", "\n", body)
        body = re.sub(r"\n{3,}", "\n\n", body)
        if body:
            letters.append({"roman": roman, "body": body})
    return letters


def main() -> None:
    text = json_html_to_text(RAW_FILE)
    letters = extract_letters(text)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total_chunks = 0
    for letter_index, letter in enumerate(letters, start=1):
        roman = letter["roman"]
        letter_dir = OUT_DIR / f"letter-{letter_index:02d}-{roman.lower()}"
        letter_dir.mkdir(parents=True, exist_ok=True)
        chunks = paragraph_chunks(letter["body"], max_words=650)
        total_chunks += len(chunks)

        for chunk_index, chunk_text in enumerate(chunks, start=1):
            chunk_id = f"montaigne_letters_en_{letter_index:02d}_{chunk_index:03d}"
            path = letter_dir / f"{chunk_id}.md"
            frontmatter = [
                "---",
                f"chunk_id: {chunk_id}",
                f"author_id: {AUTHOR_ID}",
                f"work_id: {WORK_ID}",
                f"source_id: {SOURCE_ID}",
                f"source_name: {yaml_quote(SOURCE_NAME)}",
                f"source_url: {yaml_quote(SOURCE_URL)}",
                f"source_file: {yaml_quote(RAW_FILE.name)}",
                "rights: public_domain",
                "language: en",
                "original_language: fr",
                "translation_language: en",
                "translation_publication_year: 1877",
                "text_type: letter_translation",
                f"letter_number: {letter_index}",
                f"letter_roman: {yaml_quote(roman)}",
                f"letter_title_fr: {yaml_quote(LETTER_TITLES_FR.get(roman, 'Lettre de Montaigne'))}",
                f"chunk_index: {chunk_index}",
                f"chunk_count_in_letter: {len(chunks)}",
                f"word_count: {word_count(chunk_text)}",
                "use_for_voice: true",
                "use_for_exact_french_style: false",
                "themes: []",
                "---",
                "",
            ]
            path.write_text("\n".join(frontmatter) + chunk_text + "\n", encoding="utf-8")

    print(f"Parsed letters: {len(letters)}")
    print(f"Written chunks: {total_chunks}")


if __name__ == "__main__":
    main()

