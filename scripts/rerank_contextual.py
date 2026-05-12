from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from rewrite_query_montaigne import normalize, tokenize
from search_contextual import contextual_bm25_search
from search_corpus import format_result, searchable_text
from vector_common import DEFAULT_INDEX, load_jsonl


PRIMARY_QUALITY = {
    "public_domain_primary",
    "public_domain_modern_french_translation",
}

SUPPORTING_QUALITY = {
    "public_domain_english_translation",
    "ai_draft_back_translation",
}

POETIC_TITLE_HINTS = {
    "sonnet",
    "sonnets",
    "vers",
}


def count_matches(terms: list[str], text: str) -> int:
    haystack = normalize(text)
    return sum(1 for term in terms if normalize(term) in haystack)


def lexical_density(terms: list[str], text: str) -> float:
    if not terms:
        return 0.0
    return count_matches(terms, text) / len(terms)


def matched_query_count(detail: dict[str, Any]) -> int:
    return len({match["query"] for match in detail.get("matched_queries", [])})


def best_query_rank(detail: dict[str, Any]) -> int:
    ranks = [int(match["rank"]) for match in detail.get("matched_queries", [])]
    return min(ranks) if ranks else 999


def title_text(record: dict[str, Any]) -> str:
    return " ".join(
        str(value)
        for value in [
            record.get("title", ""),
            record.get("chapter_title", ""),
            record.get("letter_title_fr", ""),
        ]
        if value
    )


def infer_answer_role(usefulness_score: float, detail: dict[str, Any], record: dict[str, Any]) -> str:
    role = str(record.get("corpus_role", ""))
    if usefulness_score >= 0.72 and role == "primary":
        return "main_evidence"
    if usefulness_score >= 0.48 and role in {"primary", "supporting_translation"}:
        return "supporting_evidence"
    if usefulness_score >= 0.32:
        return "context"
    return "discard"


def rerank_candidate(
    rewrite: dict[str, Any],
    contextual_score: float,
    record: dict[str, Any],
    detail: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    bridge_terms = list(rewrite.get("bridge_terms", []))
    groups = set(rewrite.get("matched_groups", []))
    text = searchable_text(record)
    title = title_text(record)

    bridge_density = lexical_density(bridge_terms, text)
    title_density = lexical_density(bridge_terms, title)
    query_coverage = min(matched_query_count(detail) / 3.0, 1.0)
    rank_signal = 1.0 / math.sqrt(best_query_rank(detail))
    retrieval_signal = min(math.log1p(max(contextual_score, 0.0)) / 2.0, 1.0)

    score = 0.0
    score += 0.34 * retrieval_signal
    score += 0.24 * bridge_density
    score += 0.18 * query_coverage
    score += 0.14 * rank_signal
    score += 0.10 * min(title_density * 2.0, 1.0)

    source_quality = str(record.get("source_quality", ""))
    corpus_role = str(record.get("corpus_role", ""))
    normalized_title = normalize(title)

    if corpus_role == "primary":
        score += 0.08
    elif corpus_role == "supporting_translation":
        score += 0.02
    elif corpus_role in {"context", "editorial_context"}:
        score -= 0.14

    if source_quality in PRIMARY_QUALITY:
        score += 0.06
    elif source_quality in SUPPORTING_QUALITY:
        score -= 0.03
    else:
        score -= 0.12

    if "conflict" in groups and any(term in normalized_title for term in ["colere", "conversation", "dementis"]):
        score += 0.12
    if "decision" in groups and any(term in normalized_title for term in ["jugement", "experience", "repentir"]):
        score += 0.12
    if "health_body" in groups and any(term in normalized_title for term in ["experience", "enfants", "corps"]):
        score += 0.08
    if "friendship_trust" in groups and any(term in normalized_title for term in ["amitie", "boetie"]):
        score += 0.12

    if any(hint in normalized_title for hint in POETIC_TITLE_HINTS):
        score -= 0.18

    score = max(0.0, min(score, 1.0))
    signals = {
        "retrieval_signal": round(retrieval_signal, 4),
        "bridge_density": round(bridge_density, 4),
        "title_density": round(title_density, 4),
        "query_coverage": round(query_coverage, 4),
        "rank_signal": round(rank_signal, 4),
        "matched_bridge_terms": [
            term for term in bridge_terms if re.search(rf"\b{re.escape(normalize(term))}\b", normalize(text))
        ][:10],
    }
    ranking = {
        "usefulness_score": score,
        "answer_role": infer_answer_role(score, detail, record),
        "signals": signals,
        "retrieval_detail": detail,
    }
    return score, ranking


def rerank_results(
    rewrite: dict[str, Any],
    contextual_results: list[tuple[float, dict[str, Any], dict[str, Any]]],
    *,
    limit: int,
) -> list[tuple[float, dict[str, Any], dict[str, Any]]]:
    reranked: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
    for contextual_score, record, detail in contextual_results:
        score, ranking = rerank_candidate(rewrite, contextual_score, record, detail)
        reranked.append((score, record, ranking))
    reranked.sort(key=lambda item: item[0], reverse=True)
    return reranked[:limit]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Rerank contextual Montaigne search results by answer usefulness.")
    parser.add_argument("question", help="Modern user question")
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--candidate-limit", type=int, default=40)
    parser.add_argument("--pool-per-query", type=int, default=24)
    parser.add_argument("--query-limit", type=int, default=7)
    parser.add_argument("--rewrite-provider", choices=["deterministic", "llm"], default="deterministic")
    parser.add_argument("--rewrite-model", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = load_jsonl(Path(args.index))
    rewrite, contextual_results = contextual_bm25_search(
        records,
        args.question,
        limit=args.candidate_limit,
        pool_per_query=args.pool_per_query,
        query_limit=args.query_limit,
        rewrite_provider=args.rewrite_provider,
        rewrite_model=args.rewrite_model,
    )
    reranked = rerank_results(rewrite, contextual_results, limit=args.limit)

    if args.json:
        payload = {
            "rewrite": rewrite,
            "results": [
                {"usefulness_score": score, "rerank": ranking, **record}
                for score, record, ranking in reranked
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("REWRITE")
    print(json.dumps(rewrite, ensure_ascii=False, indent=2))
    print()
    print("RERANKED RESULTS")
    for index, (score, record, ranking) in enumerate(reranked, start=1):
        print(f"usefulness_score={score:.4f} role={ranking['answer_role']}")
        print(f"signals={json.dumps(ranking['signals'], ensure_ascii=False)}")
        print(format_result(score, record, " ".join(rewrite["bridge_terms"]), index))
        print()


if __name__ == "__main__":
    main()
