from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from rewrite_query_montaigne import rewrite_query
from search_corpus import bm25_search, format_result
from vector_common import DEFAULT_INDEX, load_jsonl


def contextual_bm25_search(
    records: list[dict[str, Any]],
    question: str,
    *,
    limit: int = 8,
    pool_per_query: int = 20,
    query_limit: int = 7,
    rewrite_provider: str = "deterministic",
    rewrite_model: str | None = None,
) -> tuple[dict[str, Any], list[tuple[float, dict[str, Any], dict[str, Any]]]]:
    rewrite = rewrite_query(question, provider=rewrite_provider, query_limit=query_limit, model=rewrite_model)
    scores: dict[str, float] = {}
    records_by_id: dict[str, dict[str, Any]] = {}
    details: dict[str, dict[str, Any]] = {}

    for query_index, query in enumerate(rewrite.queries, start=1):
        query_weight = 1.0 / query_index
        for rank, (bm25_score, record) in enumerate(bm25_search(records, query, pool_per_query), start=1):
            chunk_id = str(record["chunk_id"])
            contribution = query_weight * (1.0 / (rank + 8)) * max(bm25_score, 0.01)
            scores[chunk_id] = scores.get(chunk_id, 0.0) + contribution
            records_by_id[chunk_id] = record
            detail = details.setdefault(chunk_id, {"matched_queries": []})
            detail["matched_queries"].append(
                {
                    "query": query,
                    "query_index": query_index,
                    "rank": rank,
                    "bm25_score": bm25_score,
                }
            )

    fused = [(score, records_by_id[chunk_id], details[chunk_id]) for chunk_id, score in scores.items()]
    fused.sort(key=lambda item: item[0], reverse=True)
    return rewrite.to_dict(), fused[:limit]


def compact_detail(detail: dict[str, Any]) -> str:
    matches = detail.get("matched_queries", [])
    parts = [f"q{match['query_index']}#{match['rank']}" for match in matches[:4]]
    return " ".join(parts)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Contextual BM25 search using Montaigne-compatible query rewriting.")
    parser.add_argument("question", help="Modern user question")
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--pool-per-query", type=int, default=20)
    parser.add_argument("--query-limit", type=int, default=7)
    parser.add_argument("--rewrite-provider", choices=["deterministic", "llm"], default="deterministic")
    parser.add_argument("--rewrite-model", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = load_jsonl(Path(args.index))
    rewrite, results = contextual_bm25_search(
        records,
        args.question,
        limit=args.limit,
        pool_per_query=args.pool_per_query,
        query_limit=args.query_limit,
        rewrite_provider=args.rewrite_provider,
        rewrite_model=args.rewrite_model,
    )

    if args.json:
        payload = {
            "rewrite": rewrite,
            "results": [
                {"contextual_score": score, "detail": detail, **record}
                for score, record, detail in results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("REWRITE")
    print(json.dumps(rewrite, ensure_ascii=False, indent=2))
    print()
    print("RESULTS")
    for index, (score, record, detail) in enumerate(results, start=1):
        print(f"contextual_score={score:.4f} matches={compact_detail(detail)}")
        print(format_result(score, record, " ".join(rewrite["bridge_terms"]), index))
        print()


if __name__ == "__main__":
    main()
