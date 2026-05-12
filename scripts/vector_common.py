from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "authors" / "montaigne" / "indexes" / "corpus-index.jsonl"
DEFAULT_VECTOR_NPZ = ROOT / "authors" / "montaigne" / "indexes" / "corpus-embeddings-local-hash.npz"
DEFAULT_VECTOR_META = ROOT / "authors" / "montaigne" / "indexes" / "corpus-embeddings-local-hash.json"
DEFAULT_OPENROUTER_EMBEDDING_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
DEFAULT_SENTENCE_TRANSFORMERS_MODEL = "intfloat/multilingual-e5-small"

STOPWORDS = {
    "a",
    "afin",
    "ai",
    "ainsi",
    "alors",
    "au",
    "aux",
    "avec",
    "ce",
    "ces",
    "cet",
    "cette",
    "comme",
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
    "michel",
    "mon",
    "monsieur",
    "monseigneur",
    "montaigne",
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


def normalize_text(text: str) -> str:
    text = text.replace("ſ", "s").lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = re.findall(r"[a-z0-9]{2,}", normalized)
    return [token for token in tokens if token not in STOPWORDS]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def record_embedding_text(record: dict[str, Any]) -> str:
    fields = [
        record.get("work_id", ""),
        record.get("text_type", ""),
        record.get("title", ""),
        record.get("chapter_title", ""),
        record.get("letter_title_fr", ""),
        record.get("text", ""),
    ]
    return "\n".join(str(field) for field in fields if field)


def l2_normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        return vector
    return vector / norm


def stable_feature_hash(feature: str) -> tuple[int, int, float]:
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=16).digest()
    primary = int.from_bytes(digest[:8], "little", signed=False)
    secondary = int.from_bytes(digest[8:], "little", signed=False)
    sign = 1 if primary & 1 else -1
    weight = 0.75 + ((secondary % 1000) / 2000.0)
    return primary, sign, weight


def local_hash_embedding(text: str, dimensions: int = 768, idf: dict[str, float] | None = None) -> np.ndarray:
    vector = np.zeros(dimensions, dtype=np.float32)
    normalized = normalize_text(text)
    words = tokenize(normalized)

    features: list[tuple[str, float]] = []
    features.extend((f"w:{word}", idf.get(word, 1.0) if idf else 1.0) for word in words)
    for i in range(len(words) - 1):
        bigram = f"{words[i]}_{words[i + 1]}"
        bigram_weight = max(idf.get(words[i], 1.0), idf.get(words[i + 1], 1.0)) if idf else 1.0
        features.append((f"b:{bigram}", 1.15 * bigram_weight))

    term_counts: dict[str, float] = {}
    for feature, weight in features:
        term_counts[feature] = term_counts.get(feature, 0.0) + weight

    for feature, count in term_counts.items():
        primary, sign, feature_weight = stable_feature_hash(feature)
        index = primary % dimensions
        vector[index] += sign * math.sqrt(count) * feature_weight

    return l2_normalize(vector)


def openai_embed_batch(
    texts: list[str],
    *,
    model: str,
    dimensions: int | None = None,
    timeout: int = 120,
    max_retries: int = 4,
) -> list[list[float]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    url = f"{base_url}/embeddings"
    payload: dict[str, Any] = {
        "model": model,
        "input": texts,
        "encoding_format": "float",
    }
    if dimensions:
        payload["dimensions"] = dimensions

    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(max_retries + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [item["embedding"] for item in sorted(data["data"], key=lambda item: item["index"])]
        except urllib.error.HTTPError as error:
            retryable = error.code in {408, 409, 429, 500, 502, 503, 504}
            if not retryable or attempt >= max_retries:
                detail = error.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenAI embeddings request failed: HTTP {error.code} {detail}") from error
        except urllib.error.URLError as error:
            if attempt >= max_retries:
                raise RuntimeError(f"OpenAI embeddings request failed: {error}") from error
        time.sleep(2**attempt)

    raise RuntimeError("OpenAI embeddings request failed after retries.")


def openrouter_embed_batch(
    texts: list[str],
    *,
    model: str = DEFAULT_OPENROUTER_EMBEDDING_MODEL,
    timeout: int = 120,
    max_retries: int = 4,
) -> list[list[float]]:
    load_dotenv_if_present()
    api_key = (
        os.environ.get("OPENROUTER_API_KEY")
        or os.environ.get("OPEN_ROUTER_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY or OPEN_ROUTER_API_KEY is not set.")

    url = os.environ.get("OPENROUTER_EMBEDDINGS_URL", "https://openrouter.ai/api/v1/embeddings")
    payload: dict[str, Any] = {
        "model": model,
        "input": texts,
        "encoding_format": "float",
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "http://localhost/historycafe"),
        "X-OpenRouter-Title": os.environ.get("OPENROUTER_TITLE", "HistoryCafe"),
    }

    for attempt in range(max_retries + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [item["embedding"] for item in sorted(data["data"], key=lambda item: item["index"])]
        except urllib.error.HTTPError as error:
            retryable = error.code in {408, 409, 429, 500, 502, 503, 504, 529}
            if not retryable or attempt >= max_retries:
                detail = error.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenRouter embeddings request failed: HTTP {error.code} {detail}") from error
        except urllib.error.URLError as error:
            if attempt >= max_retries:
                raise RuntimeError(f"OpenRouter embeddings request failed: {error}") from error
        time.sleep(2**attempt)

    raise RuntimeError("OpenRouter embeddings request failed after retries.")


def sentence_transformers_embed_texts(
    texts: list[str],
    *,
    model: str = DEFAULT_SENTENCE_TRANSFORMERS_MODEL,
    batch_size: int = 32,
) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise RuntimeError(
            "sentence-transformers is not installed. Run: pip install -r requirements.txt"
        ) from error

    encoder = SentenceTransformer(model)
    embeddings = encoder.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return np.asarray(embeddings, dtype=np.float32)


def adjusted_score(score: float, record: dict[str, Any]) -> float:
    score *= QUALITY_BOOST.get(str(record.get("source_quality")), 1.0)
    score *= ROLE_BOOST.get(str(record.get("corpus_role")), 1.0)
    return score


def snippet(text: str, query: str, width: int = 360) -> str:
    normalized = normalize_text(text)
    query_tokens = tokenize(query)
    positions = [normalized.find(token) for token in query_tokens if normalized.find(token) >= 0]
    start = max(min(positions) - width // 3, 0) if positions else 0
    excerpt = text[start : start + width].replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()
