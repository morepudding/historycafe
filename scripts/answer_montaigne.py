from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from rerank_contextual import rerank_results
from rewrite_query_montaigne import (
    ROOT,
    load_dotenv_if_present,
    rewrite_query,
)
from search_contextual import contextual_bm25_search
from search_corpus import bm25_search
from search_corpus import snippet
from search_hybrid import reciprocal_rank_fusion
from search_vector import load_vector_index, vector_search
from vector_common import DEFAULT_INDEX, DEFAULT_VECTOR_META, DEFAULT_VECTOR_NPZ, load_jsonl


DEFAULT_AGENT_PROFILE = ROOT / "authors" / "montaigne" / "style" / "agent-profile.md"


ANSWER_SYSTEM_PROMPT = """Tu es une IA de Montaigne a notre epoque.

Position:
- Tu sais que tu es une IA inspiree par Montaigne, pas Michel de Montaigne historique.
- Tu peux parler du monde contemporain: Internet, IA, reseaux sociaux, entreprise, ecole, politique actuelle.
- Tu ne pretends jamais que Montaigne historique connaissait ces objets modernes.
- Tu reponds en francais moderne, avec une voix sobre, sceptique, concrete, proche de l'esprit des Essais sans pastiche lourd.

Usage du corpus:
- Appuie ta reponse sur les passages fournis.
- Ne fabrique pas de citation.
- Tu peux citer une tres courte expression seulement si elle est copiee exactement depuis les extraits fournis.
- Utilise les references [1], [2], etc. quand un passage appuie une idee.
- Ne cree pas ta propre section Sources: elle sera ajoutee automatiquement.

Style:
- Reponse utile, directe, nuancee.
- Pas de vieux francais artificiel.
- Pas de "Montaigne aurait dit" comme certitude historique.
- Tu peux dire "Comme IA de Montaigne, je regarderais..." si l'identite doit etre clarifiee.
- Ne t'excuse pas de transposer un sujet moderne.
- Maximum 5 paragraphes courts.
"""


def load_agent_profile(path: Path = DEFAULT_AGENT_PROFILE) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def compact_passage(record: dict[str, Any], ranking: dict[str, Any], index: int, query: str) -> dict[str, Any]:
    label = record.get("chapter_title") or record.get("letter_title_fr") or record.get("title") or record.get("work_id")
    book = record.get("book")
    chapter = record.get("chapter")
    return {
        "source_index": index,
        "chunk_id": record.get("chunk_id"),
        "title": label,
        "book": book,
        "chapter": chapter,
        "work_id": record.get("work_id"),
        "path": record.get("path"),
        "source_quality": record.get("source_quality"),
        "corpus_role": record.get("corpus_role"),
        "answer_role": ranking.get("answer_role"),
        "usefulness_score": round(float(ranking.get("usefulness_score", 0.0)), 4),
        "excerpt": snippet(str(record.get("text", "")), query, width=900),
    }


def roman(value: Any) -> str:
    if not isinstance(value, int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return ""
    numerals = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    result = ""
    remaining = value
    for number, symbol in numerals:
        while remaining >= number:
            result += symbol
            remaining -= number
    return result


def source_label(passage: dict[str, Any]) -> str:
    work = str(passage.get("work_id") or "")
    title = str(passage.get("title") or work or "source")
    chunk_id = str(passage.get("chunk_id") or "")
    if work == "essais":
        book = roman(passage.get("book"))
        chapter = passage.get("chapter")
        location = f"Essais, {book}, {chapter}" if book and chapter else "Essais"
        return f"[{passage['source_index']}] {location}, {title} ({chunk_id})"
    if work == "correspondence":
        return f"[{passage['source_index']}] Correspondance, {title} ({chunk_id})"
    return f"[{passage['source_index']}] {title} ({chunk_id})"


def append_sources(answer: str, passages: list[dict[str, Any]]) -> str:
    used_indexes = {
        int(match)
        for match in re.findall(r"\[(\d+)\]", answer)
        if match.isdigit()
    }
    if not used_indexes:
        used_indexes = {int(passage["source_index"]) for passage in passages[:3]}
    selected = [passage for passage in passages if int(passage["source_index"]) in used_indexes]
    if not selected:
        return answer.strip()
    lines = ["Sources"]
    lines.extend(source_label(passage) for passage in selected)
    return answer.strip() + "\n\n" + "\n".join(lines)


def build_answer_prompt(question: str, rewrite: dict[str, Any], passages: list[dict[str, Any]]) -> str:
    payload = {
        "question_utilisateur": question,
        "profil_agent": load_agent_profile(),
        "interpretation_moderne": {
            "modern_explanation": rewrite.get("modern_explanation"),
            "human_situation": rewrite.get("human_situation"),
            "bridge_terms": rewrite.get("bridge_terms"),
        },
        "passages": passages,
        "consigne": (
            "Reponds a la question comme une IA de Montaigne contemporaine. "
            "Utilise les passages comme appuis. Mentionne les sources par numero, par exemple [1]. "
            "N'ajoute pas de section Sources."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def contextual_hybrid_search(
    records: list[dict[str, Any]],
    question: str,
    *,
    vectors_path: Path = DEFAULT_VECTOR_NPZ,
    meta_path: Path = DEFAULT_VECTOR_META,
    limit: int = 40,
    pool_per_query: int = 24,
    query_limit: int = 7,
    rewrite_provider: str = "deterministic",
    rewrite_model: str | None = None,
    bm25_weight: float = 1.25,
    vector_weight: float = 1.0,
) -> tuple[dict[str, Any], list[tuple[float, dict[str, Any], dict[str, Any]]]]:
    rewrite = rewrite_query(question, provider=rewrite_provider, query_limit=query_limit, model=rewrite_model)
    matrix, chunk_ids, metadata = load_vector_index(vectors_path, meta_path)

    scores: dict[str, float] = {}
    records_by_id: dict[str, dict[str, Any]] = {}
    details: dict[str, dict[str, Any]] = {}

    for query_index, query in enumerate(rewrite.queries, start=1):
        query_weight = 1.0 / query_index
        bm25_results = bm25_search(records, query, pool_per_query)
        vector_results = vector_search(records, matrix, chunk_ids, query, metadata, pool_per_query)
        fused = reciprocal_rank_fusion(
            bm25_results,
            vector_results,
            bm25_weight=bm25_weight,
            vector_weight=vector_weight,
        )

        for rank, (fused_score, record, fused_detail) in enumerate(fused[:pool_per_query], start=1):
            chunk_id = str(record["chunk_id"])
            contribution = query_weight * (1.0 / (rank + 8)) * max(fused_score * 100.0, 0.01)
            scores[chunk_id] = scores.get(chunk_id, 0.0) + contribution
            records_by_id[chunk_id] = record
            detail = details.setdefault(chunk_id, {"matched_queries": [], "retrieval_mode": "contextual-hybrid"})
            detail["vector_provider"] = metadata.get("provider")
            detail["vector_model"] = metadata.get("model")
            detail["matched_queries"].append(
                {
                    "query": query,
                    "query_index": query_index,
                    "rank": rank,
                    "bm25_rank": fused_detail.get("bm25_rank"),
                    "bm25_score": fused_detail.get("bm25_score", 0.0),
                    "vector_rank": fused_detail.get("vector_rank"),
                    "vector_score": fused_detail.get("vector_score", 0.0),
                    "vector_raw_score": fused_detail.get("vector_raw_score", 0.0),
                    "fused_score": fused_score,
                }
            )

    results = [(score, records_by_id[chunk_id], details[chunk_id]) for chunk_id, score in scores.items()]
    results.sort(key=lambda item: item[0], reverse=True)

    payload = rewrite.to_dict()
    payload["retrieval_mode"] = "contextual-hybrid"
    payload["vector_provider"] = metadata.get("provider")
    payload["vector_model"] = metadata.get("model")
    return payload, results[:limit]


def call_answer_llm(prompt: str, *, model: str | None = None) -> str:
    load_dotenv_if_present(ROOT / ".env.local")
    import os

    if os.environ.get("OPENAI_API_KEY"):
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        api_key = os.environ["OPENAI_API_KEY"]
        chosen_model = model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    elif os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPEN_ROUTER_API_KEY"):
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ["OPEN_ROUTER_API_KEY"]
        chosen_model = model or os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
    else:
        raise RuntimeError("No LLM API key found. Set OPENAI_API_KEY or OPENROUTER_API_KEY.")

    url = f"{base_url.rstrip('/')}/chat/completions"
    body = json.dumps(
        {
            "model": chosen_model,
            "temperature": 0.35,
            "messages": [
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        response_payload = json.loads(response.read().decode("utf-8"))
    return str(response_payload["choices"][0]["message"]["content"]).strip()


def prepare_answer_context(
    question: str,
    *,
    index_path: Path = DEFAULT_INDEX,
    rewrite_provider: str = "llm",
    rewrite_model: str | None = None,
    retrieval_mode: str = "contextual-hybrid",
    vectors_path: Path = DEFAULT_VECTOR_NPZ,
    meta_path: Path = DEFAULT_VECTOR_META,
    passage_limit: int = 5,
    candidate_limit: int = 40,
    pool_per_query: int = 24,
) -> dict[str, Any]:
    records = load_jsonl(index_path)
    if retrieval_mode == "contextual-hybrid":
        rewrite, contextual_results = contextual_hybrid_search(
            records,
            question,
            vectors_path=vectors_path,
            meta_path=meta_path,
            limit=candidate_limit,
            pool_per_query=pool_per_query,
            rewrite_provider=rewrite_provider,
            rewrite_model=rewrite_model,
        )
    else:
        rewrite, contextual_results = contextual_bm25_search(
            records,
            question,
            limit=candidate_limit,
            pool_per_query=pool_per_query,
            rewrite_provider=rewrite_provider,
            rewrite_model=rewrite_model,
        )
    reranked = rerank_results(rewrite, contextual_results, limit=passage_limit)
    passage_query = " ".join(str(term) for term in rewrite.get("bridge_terms", []))
    passages = [
        compact_passage(record, ranking, index, passage_query)
        for index, (score, record, ranking) in enumerate(reranked, start=1)
    ]
    prompt = build_answer_prompt(question, rewrite, passages)
    return {
        "question": question,
        "rewrite": rewrite,
        "passages": passages,
        "prompt": prompt,
    }


def generate_answer(
    question: str,
    *,
    index_path: Path = DEFAULT_INDEX,
    rewrite_provider: str = "llm",
    rewrite_model: str | None = None,
    answer_model: str | None = None,
    retrieval_mode: str = "contextual-hybrid",
    vectors_path: Path = DEFAULT_VECTOR_NPZ,
    meta_path: Path = DEFAULT_VECTOR_META,
    passage_limit: int = 5,
    candidate_limit: int = 40,
    pool_per_query: int = 24,
) -> dict[str, Any]:
    context = prepare_answer_context(
        question,
        index_path=index_path,
        rewrite_provider=rewrite_provider,
        rewrite_model=rewrite_model,
        retrieval_mode=retrieval_mode,
        vectors_path=vectors_path,
        meta_path=meta_path,
        passage_limit=passage_limit,
        candidate_limit=candidate_limit,
        pool_per_query=pool_per_query,
    )
    passages = context["passages"]
    prompt = context["prompt"]
    raw_answer = call_answer_llm(prompt, model=answer_model)
    answer = append_sources(raw_answer, passages)
    return {
        "question": context["question"],
        "rewrite": context["rewrite"],
        "passages": context["passages"],
        "answer": answer,
        "raw_answer": raw_answer,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Generate a sourced answer as a contemporary Montaigne AI.")
    parser.add_argument("question", help="Modern user question")
    parser.add_argument("--index", default=str(DEFAULT_INDEX))
    parser.add_argument("--rewrite-provider", choices=["deterministic", "llm"], default="llm")
    parser.add_argument("--rewrite-model", default=None)
    parser.add_argument("--answer-model", default=None)
    parser.add_argument("--retrieval-mode", choices=["contextual-hybrid", "contextual-bm25"], default="contextual-hybrid")
    parser.add_argument("--vectors", default=str(DEFAULT_VECTOR_NPZ))
    parser.add_argument("--meta", default=str(DEFAULT_VECTOR_META))
    parser.add_argument("--passage-limit", type=int, default=5)
    parser.add_argument("--candidate-limit", type=int, default=40)
    parser.add_argument("--pool-per-query", type=int, default=24)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--context-json", action="store_true", help="Print retrieval context and prompt without calling an LLM.")
    args = parser.parse_args()

    if args.context_json:
        context = prepare_answer_context(
            args.question,
            index_path=Path(args.index),
            rewrite_provider=args.rewrite_provider,
            rewrite_model=args.rewrite_model,
            retrieval_mode=args.retrieval_mode,
            vectors_path=Path(args.vectors),
            meta_path=Path(args.meta),
            passage_limit=args.passage_limit,
            candidate_limit=args.candidate_limit,
            pool_per_query=args.pool_per_query,
        )
        print(json.dumps(context, ensure_ascii=False, indent=2))
        return

    result = generate_answer(
        args.question,
        index_path=Path(args.index),
        rewrite_provider=args.rewrite_provider,
        rewrite_model=args.rewrite_model,
        answer_model=args.answer_model,
        retrieval_mode=args.retrieval_mode,
        vectors_path=Path(args.vectors),
        meta_path=Path(args.meta),
        passage_limit=args.passage_limit,
        candidate_limit=args.candidate_limit,
        pool_per_query=args.pool_per_query,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(result["answer"])


if __name__ == "__main__":
    main()
