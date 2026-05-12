from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "authors" / "montaigne" / "indexes" / "corpus-index.jsonl"

STOPWORDS = {
    "a",
    "afin",
    "ai",
    "ainsi",
    "alors",
    "au",
    "aucun",
    "aussi",
    "aux",
    "avec",
    "ce",
    "ces",
    "cet",
    "cette",
    "comme",
    "comment",
    "dans",
    "de",
    "des",
    "du",
    "elle",
    "en",
    "est",
    "et",
    "etre",
    "faire",
    "il",
    "ils",
    "je",
    "la",
    "le",
    "les",
    "leur",
    "lui",
    "mais",
    "me",
    "mes",
    "mon",
    "ne",
    "nos",
    "notre",
    "nous",
    "on",
    "ou",
    "par",
    "pas",
    "plus",
    "pour",
    "qu",
    "que",
    "qui",
    "sa",
    "se",
    "ses",
    "son",
    "sur",
    "the",
    "to",
    "of",
    "and",
    "in",
    "is",
    "it",
    "that",
    "you",
}

QUALITY_BOOST = {
    "public_domain_primary": 1.25,
    "public_domain_modern_french_translation": 1.18,
    "public_domain_english_translation": 0.82,
    "ai_draft_back_translation": 0.95,
    "public_domain_secondary": 0.62,
    "public_domain_editorial_notes": 0.35,
}

ROLE_BOOST = {
    "primary": 1.18,
    "supporting_translation": 0.92,
    "context": 0.68,
    "editorial_context": 0.38,
}


def normalize(text: str) -> str:
    text = text.replace("ſ", "s").lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)
    tokens = re.findall(r"[a-z0-9]{2,}", normalized)
    return [token for token in tokens if token not in STOPWORDS]


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def searchable_text(record: dict[str, Any]) -> str:
    fields = [
        record.get("title", ""),
        record.get("chapter_title", ""),
        record.get("letter_title_fr", ""),
        record.get("work_id", ""),
        record.get("text_type", ""),
        record.get("text", ""),
    ]
    return "\n".join(str(field) for field in fields if field)


def build_bm25(records: list[dict[str, Any]]) -> tuple[list[Counter[str]], dict[str, int], float]:
    doc_terms: list[Counter[str]] = []
    df: dict[str, int] = defaultdict(int)
    total_len = 0

    for record in records:
        terms = Counter(tokenize(searchable_text(record)))
        doc_terms.append(terms)
        total_len += sum(terms.values())
        for term in terms:
            df[term] += 1

    avg_len = total_len / max(len(records), 1)
    return doc_terms, dict(df), avg_len


def bm25_search(records: list[dict[str, Any]], query: str, limit: int) -> list[tuple[float, dict[str, Any]]]:
    doc_terms, df, avg_len = build_bm25(records)
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return []

    n_docs = len(records)
    k1 = 1.4
    b = 0.72
    scored: list[tuple[float, dict[str, Any]]] = []
    normalized_query = normalize(query)

    for record, terms in zip(records, doc_terms):
        doc_len = sum(terms.values()) or 1
        score = 0.0
        for term, qtf in query_terms.items():
            tf = terms.get(term, 0)
            if not tf:
                continue
            idf = math.log(1 + (n_docs - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5))
            denom = tf + k1 * (1 - b + b * doc_len / avg_len)
            score += idf * ((tf * (k1 + 1)) / denom) * qtf

        haystack = normalize(searchable_text(record))
        if normalized_query and normalized_query in haystack:
            score += 3.0

        score *= QUALITY_BOOST.get(str(record.get("source_quality")), 1.0)
        score *= ROLE_BOOST.get(str(record.get("corpus_role")), 1.0)

        if score > 0:
            scored.append((score, record))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:limit]


def snippet(text: str, query: str, width: int = 360) -> str:
    normalized = normalize(text)
    query_tokens = tokenize(query)
    positions = [normalized.find(token) for token in query_tokens if normalized.find(token) >= 0]
    start = max(min(positions) - width // 3, 0) if positions else 0
    excerpt = text[start : start + width].replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()


def format_result(score: float, record: dict[str, Any], query: str, index: int) -> str:
    label = record.get("chapter_title") or record.get("letter_title_fr") or record.get("title") or record.get("work_id")
    parts = [
        f"{index}. {record['chunk_id']}  score={score:.2f}",
        f"   work={record.get('work_id')} role={record.get('corpus_role')} quality={record.get('source_quality')}",
        f"   title={label}",
        f"   path={record.get('path')}",
        f"   {snippet(record.get('text', ''), query)}",
    ]
    return "\n".join(parts)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Search the local Montaigne corpus index.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="Path to corpus-index.jsonl")
    parser.add_argument("--limit", type=int, default=8, help="Number of results")
    parser.add_argument("--json", action="store_true", help="Print JSON records with scores")
    args = parser.parse_args()

    records = load_records(Path(args.index))
    results = bm25_search(records, args.query, args.limit)

    if args.json:
        payload = [{"score": score, **record} for score, record in results]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    for index, (score, record) in enumerate(results, start=1):
        print(format_result(score, record, args.query, index))
        print()


if __name__ == "__main__":
    main()
