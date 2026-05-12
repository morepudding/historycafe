from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

MONTAIGNE_VOCABULARY = [
    "jugement",
    "experience",
    "prudence",
    "coutume",
    "fortune",
    "raison",
    "conseil",
    "opinion",
    "humeur",
    "parole",
    "discours",
    "civilite",
    "constance",
    "moderation",
    "passion",
    "colere",
    "conversation",
    "usage",
    "nature",
    "exemple",
    "maitre",
    "enfant",
    "education",
    "corps",
    "ame",
    "mort",
    "amitie",
    "honneur",
    "verite",
]

DIRECT_TERM_ALIASES = {
    "adolescent": ["enfant", "education", "jugement"],
    "ados": ["enfant", "education", "jugement"],
    "argent": ["richesse", "fortune", "ambition"],
    "apprendre": ["education", "experience", "jugement"],
    "danger": ["prudence", "crainte", "jugement"],
    "dangereux": ["prudence", "crainte", "jugement"],
    "calme": ["moderation", "constance", "raison", "jugement"],
    "colere": ["colere", "passion", "moderation", "constance", "raison"],
    "decision": ["jugement", "prudence", "conseil"],
    "decider": ["jugement", "prudence", "conseil"],
    "dignite": ["honneur", "constance"],
    "ecran": ["discours", "opinion", "coutume"],
    "ecrans": ["discours", "opinion", "coutume"],
    "education": ["education", "enfant", "jugement"],
    "enfant": ["enfant", "education", "jugement"],
    "enfants": ["enfant", "education", "jugement"],
    "fermete": ["constance", "jugement"],
    "hasard": ["fortune"],
    "internet": ["discours", "opinion", "coutume", "parole"],
    "mourir": ["mort"],
    "respect": ["civilite", "honneur"],
    "reseaux": ["opinion", "parole", "honneur", "coutume"],
    "social": ["cite", "coutume"],
    "societe": ["cite", "coutume"],
    "stress": ["corps", "ame", "moderation", "prudence"],
    "travail": ["usage", "occupation", "moderation", "corps"],
    "verite": ["verite", "jugement"],
}

STOPWORDS = {
    "a",
    "au",
    "aux",
    "avec",
    "ce",
    "ces",
    "cet",
    "cette",
    "comment",
    "d",
    "dans",
    "de",
    "des",
    "du",
    "en",
    "est",
    "et",
    "faire",
    "il",
    "j",
    "je",
    "la",
    "le",
    "les",
    "leur",
    "lui",
    "ma",
    "mais",
    "me",
    "mes",
    "mon",
    "ne",
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
    "te",
    "tu",
    "un",
    "une",
}

SYSTEM_PROMPT = """Tu es une brique de retrieval pour un corpus Montaigne.

Ta tache n'est pas de repondre a l'utilisateur.
Ta tache est d'expliquer une question moderne a un auteur ancien, en termes humains intemporels, puis de produire des requetes courtes pour chercher dans le corpus.

Contraintes:
- N'imite pas le style de Montaigne.
- Ne traduis pas en vieux francais.
- Explique les phenomenes modernes par leurs effets humains: jugement, experience, coutume, opinion, parole, education, corps, ame, fortune, honneur, passions, usage, moderation.
- Evite les termes trop contemporains dans les requetes finales.
- Les requetes doivent etre courtes: 2 a 5 mots.
- Retourne seulement un JSON valide.

Schema JSON:
{
  "modern_intent": "question originale reformulee brievement",
  "modern_explanation": "explication du phenomene moderne en termes humains intemporels",
  "human_situation": "situation morale/pratique que Montaigne pourrait reconnaitre",
  "bridge_terms": ["..."],
  "queries": ["..."]
}
"""


@dataclass(frozen=True)
class Rewrite:
    modern_intent: str
    modern_explanation: str
    human_situation: str
    bridge_terms: list[str]
    queries: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "modern_intent": self.modern_intent,
            "modern_explanation": self.modern_explanation,
            "human_situation": self.human_situation,
            "matched_groups": [],
            "bridge_terms": self.bridge_terms,
            "queries": self.queries,
        }


def load_dotenv_if_present(path: Path | None = None) -> None:
    dotenv_path = path or (ROOT / ".env.local")
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def normalize(text: str) -> str:
    text = text.lower().replace("oe", "oe").replace("ae", "ae")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]{2,}", normalize(text)) if token not in STOPWORDS]


def unique(items: list[str], limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for item in items:
        normalized = normalize(str(item)).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        values.append(normalized)
        if limit and len(values) >= limit:
            break
    return values


def build_queries(bridge_terms: list[str], *, limit: int) -> list[str]:
    terms = bridge_terms + MONTAIGNE_VOCABULARY
    queries = [
        " ".join(terms[0:4]),
        " ".join(terms[1:5]),
        " ".join(terms[4:8]),
        "jugement experience prudence",
        "opinion parole coutume",
        "education enfant jugement",
        "usage moderation raison",
    ]
    return unique(queries, limit)


def deterministic_explain(question: str, *, term_limit: int, query_limit: int) -> Rewrite:
    tokens = tokenize(question)
    alias_terms: list[str] = []
    for token in tokens:
        alias_terms.extend(DIRECT_TERM_ALIASES.get(token, []))

    retained_terms = [
        token
        for token in tokens
        if token in MONTAIGNE_VOCABULARY or any(token in values for values in DIRECT_TERM_ALIASES.values())
    ]
    bridge_terms = unique(alias_terms + retained_terms + MONTAIGNE_VOCABULARY, term_limit)
    topic = ", ".join(tokens[:8]) or "question moderne"
    return Rewrite(
        modern_intent=question.strip(),
        modern_explanation=(
            "Fallback sans LLM: la question est ramenee a ses effets humains probables "
            f"autour de: {topic}."
        ),
        human_situation=(
            "Examiner une situation moderne comme une question de jugement, d'usage, "
            "de coutume, d'experience et de prudence."
        ),
        bridge_terms=bridge_terms,
        queries=build_queries(bridge_terms, limit=query_limit),
    )


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            return json.loads(stripped[start : end + 1])
        raise


def openai_compatible_chat(
    question: str,
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout: int = 90,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response_payload = json.loads(response.read().decode("utf-8"))
    content = response_payload["choices"][0]["message"]["content"]
    return extract_json_object(content)


def llm_explain(question: str, *, term_limit: int, query_limit: int, model: str | None = None) -> Rewrite:
    load_dotenv_if_present()

    if os.environ.get("OPENAI_API_KEY"):
        payload = openai_compatible_chat(
            question,
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ["OPENAI_API_KEY"],
            model=model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        )
    elif os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPEN_ROUTER_API_KEY"):
        payload = openai_compatible_chat(
            question,
            base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.environ.get("OPENROUTER_API_KEY") or os.environ["OPEN_ROUTER_API_KEY"],
            model=model or os.environ.get("OPENROUTER_MODEL", "openai/gpt-4.1-mini"),
        )
    else:
        raise RuntimeError("No LLM API key found. Set OPENAI_API_KEY or OPENROUTER_API_KEY.")

    bridge_terms = unique(list(payload.get("bridge_terms", [])) + MONTAIGNE_VOCABULARY, term_limit)
    raw_queries = [str(query) for query in payload.get("queries", []) if str(query).strip()]
    queries = unique(raw_queries + build_queries(bridge_terms, limit=query_limit), query_limit)
    return Rewrite(
        modern_intent=str(payload.get("modern_intent") or question).strip(),
        modern_explanation=str(payload.get("modern_explanation") or "").strip(),
        human_situation=str(payload.get("human_situation") or "").strip(),
        bridge_terms=bridge_terms,
        queries=queries,
    )


def rewrite_query(
    question: str,
    *,
    provider: str = "deterministic",
    term_limit: int = 16,
    query_limit: int = 7,
    model: str | None = None,
) -> Rewrite:
    if provider == "deterministic":
        return deterministic_explain(question, term_limit=term_limit, query_limit=query_limit)
    if provider == "llm":
        return llm_explain(question, term_limit=term_limit, query_limit=query_limit, model=model)
    raise ValueError(f"Unsupported provider: {provider}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Explain a modern question, then rewrite it into Montaigne-compatible corpus queries.")
    parser.add_argument("question", help="Modern user question")
    parser.add_argument("--provider", choices=["deterministic", "llm"], default="deterministic")
    parser.add_argument("--model", default=None)
    parser.add_argument("--term-limit", type=int, default=16)
    parser.add_argument("--query-limit", type=int, default=7)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rewrite = rewrite_query(
        args.question,
        provider=args.provider,
        term_limit=args.term_limit,
        query_limit=args.query_limit,
        model=args.model,
    )
    if args.json:
        print(json.dumps(rewrite.to_dict(), ensure_ascii=False, indent=2))
        return

    print(f"modern_intent: {rewrite.modern_intent}")
    print(f"modern_explanation: {rewrite.modern_explanation}")
    print(f"human_situation: {rewrite.human_situation}")
    print("matched_groups: (none)")
    print(f"bridge_terms: {', '.join(rewrite.bridge_terms)}")
    print("queries:")
    for query in rewrite.queries:
        print(f"- {query}")


if __name__ == "__main__":
    main()
