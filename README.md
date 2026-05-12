# HistoryCafe

HistoryCafe is a corpus and retrieval prototype for building contemporary assistants lightly colored by classic authors.

The current implementation focuses on Michel de Montaigne. It imports public-domain source material, builds a chunk index, retrieves relevant passages, and generates sourced answers as a modern assistant inspired by Montaigne without impersonating him.

## Current Status

- Montaigne corpus: `authors/montaigne`
- Corpus index: `authors/montaigne/indexes/corpus-index.jsonl`
- Indexed records: see `authors/montaigne/indexes/corpus-stats.json`
- Retrieval modes: BM25, vector, hybrid, contextual BM25 + reranker
- Answer generation: OpenAI-compatible chat API through OpenAI or OpenRouter

This is a V0 prototype, not a packaged application.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env.local
```

Fill `.env.local` only with the API keys you need. The file is intentionally ignored by Git.

## Rebuild The Corpus Index

```powershell
python scripts\build_corpus_index.py
```

## Local Search

BM25 lexical search:

```powershell
python scripts\search_corpus.py "amitie la boetie" --limit 8
```

Contextual search and reranking:

```powershell
python scripts\rerank_contextual.py "internet est-il dangereux pour les enfants" --limit 5
```

## Semantic Embeddings

Fast deterministic baseline, no model download:

```powershell
python scripts\embed_corpus.py --provider local-hash --dimensions 768
python scripts\search_hybrid.py "internet enfants education jugement" --limit 8
```

Stable local semantic embeddings with Sentence Transformers:

```powershell
python scripts\embed_corpus.py --provider sentence-transformers --model intfloat/multilingual-e5-small --batch-size 32
python scripts\search_hybrid.py "repondre a un client mecontent avec tact" --vectors authors\montaigne\indexes\corpus-embeddings-sentence-transformers.npz --meta authors\montaigne\indexes\corpus-embeddings-sentence-transformers.json
```

OpenAI embeddings, if `OPENAI_API_KEY` is set:

```powershell
python scripts\embed_corpus.py --provider openai --model text-embedding-3-small --dimensions 1536 --out-npz authors\montaigne\indexes\corpus-embeddings-openai.npz --out-meta authors\montaigne\indexes\corpus-embeddings-openai.json
```

## Generate An Answer

```powershell
python scripts\answer_montaigne.py "Comment prendre une decision difficile sans certitude ?"
```

The assistant should cite retrieved passages and stay explicit about modern transpositions.

## Benchmark

```powershell
python scripts\run_montaigne_benchmark.py --limit 20
```

The benchmark rubric and current manual V0 evaluation live in `eval/montaigne-chatbot-v0-benchmark.md`.

## Project Hygiene

- Do not commit `.env.local` or API keys.
- Generated `.npz` embedding matrices are ignored and should be rebuilt locally.
- Public-domain corpus chunks and JSONL indexes are intended to be versioned.
- AI draft translations are marked as working material and should not be cited as original French sources.

