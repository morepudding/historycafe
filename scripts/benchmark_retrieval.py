from __future__ import annotations

import argparse
from pathlib import Path

from search_corpus import bm25_search
from search_hybrid import reciprocal_rank_fusion
from search_vector import load_vector_index, vector_search
from vector_common import DEFAULT_INDEX, load_jsonl


QUESTIONS = [
    "répondre à un client mécontent avec tact et fermeté",
    "écrire une campagne honnête sans promesse exagérée",
    "critiquer une mode actuelle sans faire le moraliste",
    "prendre une décision difficile sans certitude artificielle",
    "parler au pouvoir avec prudence et indépendance",
    "amitié La Boétie",
    "colère conversation jugement",
    "expérience corps maladie",
    "voyage observation coutumes",
    "Mademoiselle de Montaigne femme consolation Plutarque",
]


def compact_result(record: dict) -> str:
    label = record.get("chapter_title") or record.get("letter_title_fr") or record.get("title") or record.get("work_id")
    return f"{record['chunk_id']} | {record.get('work_id')} | {record.get('source_quality')} | {label}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare BM25, vector, and hybrid retrieval.")
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--vectors", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    records = load_jsonl(Path(args.index))
    matrix, chunk_ids, metadata = load_vector_index(Path(args.vectors), Path(args.meta))

    print(f"records={len(records)} provider={metadata['provider']} model={metadata['model']}")
    print()

    for question in QUESTIONS:
        print("=" * 100)
        print(f"QUESTION: {question}")
        print()

        bm25 = bm25_search(records, question, args.limit)
        vector = vector_search(records, matrix, chunk_ids, question, metadata, args.limit)
        hybrid = reciprocal_rank_fusion(
            bm25_search(records, question, 30),
            vector_search(records, matrix, chunk_ids, question, metadata, 30),
        )[: args.limit]

        print("BM25")
        for rank, (_, record) in enumerate(bm25, start=1):
            print(f"  {rank}. {compact_result(record)}")

        print("VECTOR")
        for rank, (_, raw, record) in enumerate(vector, start=1):
            print(f"  {rank}. raw={raw:.4f} {compact_result(record)}")

        print("HYBRID")
        for rank, (_, record, detail) in enumerate(hybrid, start=1):
            print(
                f"  {rank}. bm25={detail.get('bm25_rank')} vector={detail.get('vector_rank')} "
                f"{compact_result(record)}"
            )
        print()


if __name__ == "__main__":
    main()
