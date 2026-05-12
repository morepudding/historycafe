from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from vector_common import (
    DEFAULT_INDEX,
    DEFAULT_OPENROUTER_EMBEDDING_MODEL,
    DEFAULT_SENTENCE_TRANSFORMERS_MODEL,
    ROOT,
    load_jsonl,
    local_hash_embedding,
    openai_embed_batch,
    openrouter_embed_batch,
    record_embedding_text,
    sentence_transformers_embed_texts,
    tokenize,
)


def default_output_paths(provider: str) -> tuple[Path, Path]:
    base = ROOT / "authors" / "montaigne" / "indexes" / f"corpus-embeddings-{provider}"
    return base.with_suffix(".npz"), base.with_suffix(".json")


def build_local_idf(records: list[dict]) -> dict[str, float]:
    doc_count: dict[str, int] = {}
    for record in records:
        terms = set(tokenize(record_embedding_text(record)))
        for term in terms:
            doc_count[term] = doc_count.get(term, 0) + 1

    n_docs = max(len(records), 1)
    return {
        term: math.log(1 + (n_docs + 1) / (count + 1))
        for term, count in doc_count.items()
    }


def embed_local(records: list[dict], dimensions: int, idf: dict[str, float]) -> np.ndarray:
    matrix = np.zeros((len(records), dimensions), dtype=np.float32)
    for index, record in enumerate(records):
        matrix[index] = local_hash_embedding(record_embedding_text(record), dimensions=dimensions, idf=idf)
    return matrix


def embed_openai(records: list[dict], model: str, dimensions: int | None, batch_size: int) -> np.ndarray:
    vectors: list[list[float]] = []
    texts = [record_embedding_text(record)[:24000] for record in records]
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        embedded = openai_embed_batch(batch, model=model, dimensions=dimensions)
        vectors.extend(embedded)
        print(f"Embedded {min(start + batch_size, len(texts))}/{len(texts)}")
    return np.array(vectors, dtype=np.float32)


def embed_openrouter(records: list[dict], model: str, batch_size: int) -> np.ndarray:
    vectors: list[list[float]] = []
    texts = [record_embedding_text(record)[:24000] for record in records]
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        embedded = openrouter_embed_batch(batch, model=model)
        vectors.extend(embedded)
        print(f"Embedded {min(start + batch_size, len(texts))}/{len(texts)}")
    return np.array(vectors, dtype=np.float32)


def embed_sentence_transformers(records: list[dict], model: str, batch_size: int) -> np.ndarray:
    texts = [record_embedding_text(record) for record in records]
    return sentence_transformers_embed_texts(texts, model=model, batch_size=batch_size)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed the Montaigne corpus index.")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="Path to corpus-index.jsonl")
    parser.add_argument(
        "--provider",
        choices=["local-hash", "openai", "openrouter", "sentence-transformers"],
        default="local-hash",
    )
    parser.add_argument("--model", default="text-embedding-3-small", help="OpenAI embedding model")
    parser.add_argument("--dimensions", type=int, default=768, help="Embedding dimensions")
    parser.add_argument("--batch-size", type=int, default=64, help="OpenAI batch size")
    parser.add_argument("--out-npz", help="Output .npz path")
    parser.add_argument("--out-meta", help="Output metadata .json path")
    args = parser.parse_args()

    records = load_jsonl(Path(args.index))
    out_npz, out_meta = default_output_paths(args.provider)
    if args.out_npz:
        out_npz = Path(args.out_npz)
    if args.out_meta:
        out_meta = Path(args.out_meta)
    out_npz.parent.mkdir(parents=True, exist_ok=True)

    if args.provider == "openrouter" and args.model == "text-embedding-3-small":
        args.model = DEFAULT_OPENROUTER_EMBEDDING_MODEL
    if args.provider == "sentence-transformers" and args.model == "text-embedding-3-small":
        args.model = DEFAULT_SENTENCE_TRANSFORMERS_MODEL

    if args.provider == "local-hash":
        local_idf = build_local_idf(records)
        matrix = embed_local(records, dimensions=args.dimensions, idf=local_idf)
        model = f"local-hash-{args.dimensions}"
        provider_extra = {"local_idf": local_idf}
    elif args.provider == "openai":
        matrix = embed_openai(records, model=args.model, dimensions=args.dimensions, batch_size=args.batch_size)
        model = args.model
        provider_extra = {}
    elif args.provider == "openrouter":
        matrix = embed_openrouter(records, model=args.model, batch_size=args.batch_size)
        model = args.model
        provider_extra = {}
    else:
        matrix = embed_sentence_transformers(records, model=args.model, batch_size=args.batch_size)
        model = args.model
        provider_extra = {}

    chunk_ids = np.array([record["chunk_id"] for record in records], dtype=object)
    np.savez_compressed(out_npz, embeddings=matrix, chunk_ids=chunk_ids)

    metadata = {
        "provider": args.provider,
        "model": model,
        "dimensions": int(matrix.shape[1]),
        "record_count": int(matrix.shape[0]),
        "index_path": str(Path(args.index).as_posix()),
        "npz_path": str(out_npz.as_posix()),
        **provider_extra,
    }
    out_meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Embedded chunks: {matrix.shape[0]}")
    print(f"Dimensions: {matrix.shape[1]}")
    print(f"Vectors: {out_npz.relative_to(ROOT).as_posix() if out_npz.is_relative_to(ROOT) else out_npz}")
    print(f"Metadata: {out_meta.relative_to(ROOT).as_posix() if out_meta.is_relative_to(ROOT) else out_meta}")


if __name__ == "__main__":
    main()
