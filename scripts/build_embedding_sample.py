from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from vector_common import DEFAULT_INDEX, ROOT, load_jsonl


OUT_PATH = ROOT / "authors" / "montaigne" / "indexes" / "corpus-index-sample.jsonl"

ESSAY_TARGETS = {
    ("essais", 1, 27): "De l'amitie",
    ("essais", 1, 29): "De la moderation",
    ("essais", 2, 31): "De la colere",
    ("essais", 3, 8): "De la conversation",
    ("essais", 3, 13): "De l'experience",
}

MAX_BY_GROUP = {
    "essay_target": 8,
    "journal-de-voyage": 12,
    "correspondence": 999,
    "biographies": 8,
}


def record_key(record: dict[str, Any]) -> tuple[str, int | None, int | None]:
    return (
        str(record.get("work_id")),
        record.get("book") if isinstance(record.get("book"), int) else None,
        record.get("chapter") if isinstance(record.get("chapter"), int) else None,
    )


def main() -> None:
    records = load_jsonl(DEFAULT_INDEX)
    selected: list[dict[str, Any]] = []
    counts: dict[str, int] = defaultdict(int)
    essay_counts: dict[tuple[str, int | None, int | None], int] = defaultdict(int)

    for record in records:
        work_id = str(record.get("work_id"))
        key = record_key(record)

        if key in ESSAY_TARGETS and essay_counts[key] < MAX_BY_GROUP["essay_target"]:
            selected.append(record)
            essay_counts[key] += 1
            continue

        if work_id == "journal-de-voyage" and counts[work_id] < MAX_BY_GROUP[work_id]:
            selected.append(record)
            counts[work_id] += 1
            continue

        if work_id == "correspondence" and counts[work_id] < MAX_BY_GROUP[work_id]:
            selected.append(record)
            counts[work_id] += 1
            continue

        if work_id == "biographies" and counts[work_id] < MAX_BY_GROUP[work_id]:
            selected.append(record)
            counts[work_id] += 1
            continue

    seen: set[str] = set()
    unique = []
    for record in selected:
        chunk_id = str(record["chunk_id"])
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        unique.append(record)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as handle:
        for record in unique:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"Sample records: {len(unique)}")
    print(f"Output: {OUT_PATH.relative_to(ROOT).as_posix()}")
    print("Essay targets:")
    for key, count in sorted(essay_counts.items()):
        print(f"  {key}: {count}")
    print("Other groups:")
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")


if __name__ == "__main__":
    main()
