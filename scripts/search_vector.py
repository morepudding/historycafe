from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from vector_common import (
    DEFAULT_INDEX,
    DEFAULT_VECTOR_META,
    DEFAULT_VECTOR_NPZ,
    adjusted_score,
    load_jsonl,
    local_hash_embedding,
    openrouter_embed_batch,
    openai_embed_batch,
    record_embedding_text,
    sentence_transformers_embed_texts,
    snippet,
)


def load_vector_index(npz_path: Path, meta_path: Path) -> tuple[np.ndarray, list[str], dict]:
    payload = np.load(npz_path, allow_pickle=True)
    matrix = payload["embeddings"].astype(np.float32)
    chunk_ids = [str(value) for value in payload["chunk_ids"].tolist()]
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    return matrix, chunk_ids, metadata


def embed_query(query: str, metadata: dict) -> np.ndarray:
    provider = metadata["provider"]
    dimensions = int(metadata["dimensions"])
    if provider == "local-hash":
        return local_hash_embedding(query, dimensions=dimensions, idf=metadata.get("local_idf", {}))
    if provider == "openai":
        vector = openai_embed_batch([query], model=metadata["model"], dimensions=dimensions)[0]
        return np.array(vector, dtype=np.float32)
    if provider == "openrouter":
        vector = openrouter_embed_batch([query], model=metadata["model"])[0]
        return np.array(vector, dtype=np.float32)
    if provider == "sentence-transformers":
        return sentence_transformers_embed_texts([query], model=metadata["model"], batch_size=1)[0]
    raise ValueError(f"Unsupported provider: {provider}")


def vector_search(
    records: list[dict],
    matrix: np.ndarray,
    chunk_ids: list[str],
    query: str,
    metadata: dict,
    limit: int,
) -> list[tuple[float, float, dict]]:
    record_by_id = {str(record["chunk_id"]): record for record in records}
    query_vector = embed_query(query, metadata)
    query_norm = float(np.linalg.norm(query_vector))
    if query_norm:
        query_vector = query_vector / query_norm

    similarities = matrix @ query_vector
    results: list[tuple[float, float, dict]] = []
    for raw_score, chunk_id in zip(similarities.tolist(), chunk_ids):
        record = record_by_id.get(chunk_id)
        if not record:
            continue
        score = adjusted_score(float(raw_score), record)
        results.append((score, float(raw_score), record))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:limit]


def format_result(score: float, raw_score: float, record: dict, query: str, index: int) -> str:
    label = record.get("chapter_title") or record.get("letter_title_fr") or record.get("title") or record.get("work_id")
    return "\n".join(
        [
            f"{index}. {record['chunk_id']}  score={score:.4f} raw={raw_score:.4f}",
            f"   work={record.get('work_id')} role={record.get('corpus_role')} quality={record.get('source_quality')}",
            f"   title={label}",
            f"   path={record.get('path')}",
            f"   {snippet(record.get('text', ''), query)}",
        ]
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Vector-search the local Montaigne corpus.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="Path to corpus-index.jsonl")
    parser.add_argument("--vectors", default=str(DEFAULT_VECTOR_NPZ), help="Path to embeddings .npz")
    parser.add_argument("--meta", default=str(DEFAULT_VECTOR_META), help="Path to embeddings metadata .json")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = load_jsonl(Path(args.index))
    matrix, chunk_ids, metadata = load_vector_index(Path(args.vectors), Path(args.meta))
    results = vector_search(records, matrix, chunk_ids, args.query, metadata, args.limit)

    if args.json:
        payload = [{"score": score, "raw_score": raw_score, **record} for score, raw_score, record in results]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"provider={metadata['provider']} model={metadata['model']}")
    for index, (score, raw_score, record) in enumerate(results, start=1):
        print(format_result(score, raw_score, record, args.query, index))
        print()


if __name__ == "__main__":
    main()
