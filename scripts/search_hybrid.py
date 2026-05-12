from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from search_corpus import bm25_search
from search_vector import load_vector_index, vector_search
from vector_common import DEFAULT_INDEX, DEFAULT_VECTOR_META, DEFAULT_VECTOR_NPZ, load_jsonl, snippet


def reciprocal_rank_fusion(
    bm25_results: list[tuple[float, dict]],
    vector_results: list[tuple[float, float, dict]],
    *,
    k: int = 60,
    bm25_weight: float = 1.25,
    vector_weight: float = 1.0,
) -> list[tuple[float, dict, dict]]:
    scores: dict[str, float] = {}
    records: dict[str, dict] = {}
    details: dict[str, dict] = {}

    for rank, (score, record) in enumerate(bm25_results, start=1):
        chunk_id = str(record["chunk_id"])
        scores[chunk_id] = scores.get(chunk_id, 0.0) + bm25_weight / (k + rank)
        records[chunk_id] = record
        details.setdefault(chunk_id, {})["bm25_rank"] = rank
        details[chunk_id]["bm25_score"] = score

    for rank, (score, raw_score, record) in enumerate(vector_results, start=1):
        chunk_id = str(record["chunk_id"])
        scores[chunk_id] = scores.get(chunk_id, 0.0) + vector_weight / (k + rank)
        records[chunk_id] = record
        details.setdefault(chunk_id, {})["vector_rank"] = rank
        details[chunk_id]["vector_score"] = score
        details[chunk_id]["vector_raw_score"] = raw_score

    fused = [(score, records[chunk_id], details[chunk_id]) for chunk_id, score in scores.items()]
    fused.sort(key=lambda item: item[0], reverse=True)
    return fused


def format_result(score: float, record: dict, detail: dict, query: str, index: int) -> str:
    label = record.get("chapter_title") or record.get("letter_title_fr") or record.get("title") or record.get("work_id")
    return "\n".join(
        [
            f"{index}. {record['chunk_id']}  fused={score:.4f}",
            f"   bm25_rank={detail.get('bm25_rank')} vector_rank={detail.get('vector_rank')}",
            f"   work={record.get('work_id')} role={record.get('corpus_role')} quality={record.get('source_quality')}",
            f"   title={label}",
            f"   path={record.get('path')}",
            f"   {snippet(record.get('text', ''), query)}",
        ]
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Hybrid BM25 + vector search over the Montaigne corpus.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--vectors", default=str(DEFAULT_VECTOR_NPZ))
    parser.add_argument("--meta", default=str(DEFAULT_VECTOR_META))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--pool", type=int, default=40)
    parser.add_argument("--bm25-weight", type=float, default=1.25)
    parser.add_argument("--vector-weight", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = load_jsonl(Path(args.index))
    matrix, chunk_ids, metadata = load_vector_index(Path(args.vectors), Path(args.meta))
    bm25_results = bm25_search(records, args.query, args.pool)
    vector_results = vector_search(records, matrix, chunk_ids, args.query, metadata, args.pool)
    fused = reciprocal_rank_fusion(
        bm25_results,
        vector_results,
        bm25_weight=args.bm25_weight,
        vector_weight=args.vector_weight,
    )[: args.limit]

    if args.json:
        payload = [{"fused_score": score, "detail": detail, **record} for score, record, detail in fused]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"vector_provider={metadata['provider']} model={metadata['model']}")
    for index, (score, record, detail) in enumerate(fused, start=1):
        print(format_result(score, record, detail, args.query, index))
        print()


if __name__ == "__main__":
    main()
