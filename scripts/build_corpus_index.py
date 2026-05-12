from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTHOR_DIR = ROOT / "authors" / "montaigne"
OUT_DIR = AUTHOR_DIR / "indexes"
INDEX_PATH = OUT_DIR / "corpus-index.jsonl"
STATS_PATH = OUT_DIR / "corpus-stats.json"


VALID_CHUNK_ROOTS = [
    AUTHOR_DIR / "works" / "essais" / "chunks-michaud-modern",
    AUTHOR_DIR / "works" / "journal-de-voyage" / "chunks",
    AUTHOR_DIR / "correspondence" / "chunks" / "lettre-mort-la-boetie",
    AUTHOR_DIR / "correspondence" / "chunks-en",
    AUTHOR_DIR / "correspondence" / "chunks-fr-ai-draft",
    AUTHOR_DIR / "biographies" / "chunks",
]


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown

    try:
        _, frontmatter, body = markdown.split("---", 2)
    except ValueError:
        return {}, markdown

    metadata: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key:
            metadata.setdefault(current_key, [])
            if isinstance(metadata[current_key], list):
                metadata[current_key].append(parse_scalar(line[4:]))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        metadata[key] = [] if value == "" else parse_scalar(value)

    return metadata, body.lstrip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def infer_corpus_role(metadata: dict[str, Any]) -> str:
    text_type = str(metadata.get("text_type", ""))
    work_id = str(metadata.get("work_id", ""))
    if metadata.get("_looks_like_editorial_notes"):
        return "editorial_context"
    if text_type in {"secondary_text", "reference_notice"} or work_id == "biographies":
        return "context"
    if text_type in {"letter_translation", "letter_translation_fr_draft"}:
        return "supporting_translation"
    return "primary"


def infer_source_quality(metadata: dict[str, Any]) -> str:
    text_type = str(metadata.get("text_type", ""))
    text_layer = str(metadata.get("text_layer", ""))
    if metadata.get("_looks_like_editorial_notes"):
        return "public_domain_editorial_notes"
    if text_type == "letter_translation_fr_draft":
        return "ai_draft_back_translation"
    if text_type == "letter_translation":
        return "public_domain_english_translation"
    if text_type in {"secondary_text", "reference_notice"}:
        return "public_domain_secondary"
    if text_layer == "modern_french_translation":
        return "public_domain_modern_french_translation"
    return "public_domain_primary"


def iter_chunk_paths() -> list[Path]:
    paths: list[Path] = []
    for root in VALID_CHUNK_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            paths.append(path)
    return paths


def build_record(path: Path) -> dict[str, Any]:
    markdown = path.read_text(encoding="utf-8")
    metadata, text = parse_frontmatter(markdown)
    if "chunk_id" not in metadata:
        raise ValueError(f"Missing chunk_id in {path}")
    stripped_text = text.strip()
    metadata["_looks_like_editorial_notes"] = stripped_text.startswith("NOTES") or stripped_text.startswith("Notes")

    rel_path = path.relative_to(ROOT).as_posix()
    record = {
        "chunk_id": metadata.get("chunk_id"),
        "author_id": metadata.get("author_id", "montaigne"),
        "work_id": metadata.get("work_id"),
        "text_type": metadata.get("text_type"),
        "text_layer": metadata.get("text_layer"),
        "language": metadata.get("language"),
        "source_id": metadata.get("source_id"),
        "source_name": metadata.get("source_name"),
        "source_url": metadata.get("source_url"),
        "rights": metadata.get("rights"),
        "title": metadata.get("title"),
        "chapter_title": metadata.get("chapter_title"),
        "book": metadata.get("book"),
        "chapter": metadata.get("chapter"),
        "letter_number": metadata.get("letter_number"),
        "letter_title_fr": metadata.get("letter_title_fr"),
        "translation_status": metadata.get("translation_status"),
        "source_quality": infer_source_quality(metadata),
        "corpus_role": infer_corpus_role(metadata),
        "path": rel_path,
        "word_count": metadata.get("word_count") or word_count(text),
        "text": stripped_text,
    }
    return {key: value for key, value in record.items() if value not in (None, "", [])}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = [build_record(path) for path in iter_chunk_paths()]

    seen: set[str] = set()
    duplicates: list[str] = []
    for record in records:
        chunk_id = str(record["chunk_id"])
        if chunk_id in seen:
            duplicates.append(chunk_id)
        seen.add(chunk_id)
    if duplicates:
        raise ValueError(f"Duplicate chunk ids: {duplicates[:10]}")

    with INDEX_PATH.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    stats = {
        "record_count": len(records),
        "total_words": sum(int(record.get("word_count", 0)) for record in records),
        "by_work_id": dict(Counter(str(record.get("work_id", "unknown")) for record in records)),
        "by_corpus_role": dict(Counter(str(record.get("corpus_role", "unknown")) for record in records)),
        "by_source_quality": dict(Counter(str(record.get("source_quality", "unknown")) for record in records)),
        "index_path": INDEX_PATH.relative_to(ROOT).as_posix(),
    }
    STATS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Indexed chunks: {stats['record_count']}")
    print(f"Total words: {stats['total_words']}")
    print(f"Index: {stats['index_path']}")


if __name__ == "__main__":
    main()
