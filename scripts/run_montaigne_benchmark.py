from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from answer_montaigne import generate_answer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MARKDOWN = ROOT / "eval" / "montaigne-chatbot-v0-benchmark-results.md"
DEFAULT_JSONL = ROOT / "eval" / "montaigne-chatbot-v0-benchmark-results.jsonl"

QUESTIONS = [
    "Internet est-il dangereux pour les enfants ?",
    "Les reseaux sociaux nous rendent-ils vaniteux ?",
    "Faut-il avoir peur de l'intelligence artificielle ?",
    "Comment prendre une decision difficile sans certitude ?",
    "Comment repondre a un client mecontent sans perdre son calme ?",
    "Comment gerer un collegue toxique au travail ?",
    "Est-ce que l'argent corrompt forcement ?",
    "Comment parler d'un echec sans perdre la face ?",
    "Comment eduquer un enfant sans l'ecraser ?",
    "Pourquoi ai-je peur du regard des autres ?",
    "Comment rester libre face a l'opinion publique ?",
    "La productivite permanente nous rend-elle malades ?",
    "Comment ralentir sans devenir passif ?",
    "Peut-on critiquer une mode sans devenir moraliste ?",
    "Comment reconnaitre un vrai ami ?",
    "Faut-il toujours dire la verite ?",
    "Comment vivre avec la maladie ou la douleur ?",
    "Pourquoi voyage-t-on vraiment ?",
    "Comment conseiller un dirigeant sans flatter le pouvoir ?",
    "Comment ne pas se laisser emporter par la colere ?",
]


def source_line(passage: dict[str, Any]) -> str:
    return (
        f"- [{passage.get('source_index')}] {passage.get('title')} "
        f"score={passage.get('usefulness_score')} role={passage.get('answer_role')} "
        f"chunk={passage.get('chunk_id')}"
    )


def render_result(index: int, result: dict[str, Any], elapsed: float) -> str:
    rewrite = result["rewrite"]
    passages = result["passages"]
    lines = [
        f"## {index}. {result['question']}",
        "",
        f"Temps : {elapsed:.1f}s",
        "",
        "### Rewrite",
        "",
        f"- Explication : {rewrite.get('modern_explanation')}",
        f"- Situation : {rewrite.get('human_situation')}",
        f"- Mots-ponts : {', '.join(str(term) for term in rewrite.get('bridge_terms', []))}",
        "",
        "### Passages",
        "",
    ]
    lines.extend(source_line(passage) for passage in passages)
    lines.extend(
        [
            "",
            "### Reponse",
            "",
            result["answer"],
            "",
            "### Notes evaluation",
            "",
            "| Rewrite | Retrieval | Voice | Usefulness | Sources | Notes |",
            "|---:|---:|---:|---:|---:|---|",
            "|  |  |  |  |  |  |",
            "",
        ]
    )
    return "\n".join(lines)


def render_error(index: int, question: str, error: str, elapsed: float) -> str:
    return "\n".join(
        [
            f"## {index}. {question}",
            "",
            f"Temps : {elapsed:.1f}s",
            "",
            "### Erreur",
            "",
            "```text",
            error,
            "```",
            "",
        ]
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Run the Montaigne chatbot v0 benchmark.")
    parser.add_argument("--markdown", default=str(DEFAULT_MARKDOWN))
    parser.add_argument("--jsonl", default=str(DEFAULT_JSONL))
    parser.add_argument("--limit", type=int, default=len(QUESTIONS))
    parser.add_argument("--passage-limit", type=int, default=5)
    parser.add_argument("--candidate-limit", type=int, default=40)
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    markdown_path = Path(args.markdown)
    jsonl_path = Path(args.jsonl)
    questions = QUESTIONS[: args.limit]
    started = time.strftime("%Y-%m-%d %H:%M:%S")

    markdown_parts = [
        "# Resultats benchmark v0 - Chatbot Montaigne contemporain",
        "",
        f"Debut : {started}",
        f"Questions : {len(questions)}",
        "",
    ]

    with jsonl_path.open("w", encoding="utf-8") as jsonl:
        for index, question in enumerate(questions, start=1):
            print(f"[{index}/{len(questions)}] {question}", flush=True)
            start = time.time()
            try:
                result = generate_answer(
                    question,
                    passage_limit=args.passage_limit,
                    candidate_limit=args.candidate_limit,
                )
                elapsed = time.time() - start
                jsonl.write(json.dumps({"index": index, "elapsed_seconds": elapsed, **result}, ensure_ascii=False) + "\n")
                jsonl.flush()
                markdown_parts.append(render_result(index, result, elapsed))
            except Exception as exc:
                elapsed = time.time() - start
                payload = {"index": index, "question": question, "elapsed_seconds": elapsed, "error": repr(exc)}
                jsonl.write(json.dumps(payload, ensure_ascii=False) + "\n")
                jsonl.flush()
                markdown_parts.append(render_error(index, question, repr(exc), elapsed))
            if args.sleep:
                time.sleep(args.sleep)

    markdown_path.write_text("\n".join(markdown_parts), encoding="utf-8")
    print(f"Wrote {markdown_path}")
    print(f"Wrote {jsonl_path}")


if __name__ == "__main__":
    main()
