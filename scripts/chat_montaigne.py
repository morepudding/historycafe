from __future__ import annotations

import argparse
import sys

from answer_montaigne import generate_answer


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Interactive chat with the HistoryCafe Montaigne agent.")
    parser.add_argument("--rewrite-provider", choices=["deterministic", "llm"], default="llm")
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

