from __future__ import annotations

import argparse
import sys
from pathlib import Path

from answer_montaigne import generate_answer
from vector_common import DEFAULT_VECTOR_META, DEFAULT_VECTOR_NPZ


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Interactive chat with the HistoryCafe Montaigne agent.")
    parser.add_argument("--rewrite-provider", choices=["deterministic", "llm"], default="llm")
    parser.add_argument("--retrieval-mode", choices=["contextual-hybrid", "contextual-bm25"], default="contextual-hybrid")
    parser.add_argument("--vectors", default=str(DEFAULT_VECTOR_NPZ))
    parser.add_argument("--meta", default=str(DEFAULT_VECTOR_META))
    parser.add_argument("--passage-limit", type=int, default=5)
    parser.add_argument("--candidate-limit", type=int, default=40)
    args = parser.parse_args()

    print("HistoryCafe Montaigne. Tape 'exit' ou 'quit' pour sortir.")
    print()

    while True:
        try:
            question = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            return

        try:
            result = generate_answer(
                question,
                rewrite_provider=args.rewrite_provider,
                retrieval_mode=args.retrieval_mode,
                vectors_path=Path(args.vectors),
                meta_path=Path(args.meta),
                passage_limit=args.passage_limit,
                candidate_limit=args.candidate_limit,
            )
        except RuntimeError as error:
            print()
            print(f"Erreur: {error}")
            print("Configure OPENAI_API_KEY ou OPENROUTER_API_KEY dans .env.local pour generer les reponses.")
            print()
            continue

        print()
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
