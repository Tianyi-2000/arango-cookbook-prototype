"""Sentence embeddings for articles and questions: all-MiniLM-L6-v2, 384 dimensions, runs on a laptop CPU.

Vectors are L2-normalised, so cosine similarity is a dot product; ArangoDB's cosine metric gives the same order.
"""
from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIM = 384


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer  # slow import, so only when needed
    return SentenceTransformer(MODEL_NAME, device="cpu")


def article_text(a: dict) -> str:
    """What gets embedded for an article version: its title, then its text."""
    return f"{a['title']}\n{a['text']}"


def embed(texts: list[str]) -> list[list[float]]:
    vecs = _model().encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    return [[round(float(x), 6) for x in v] for v in vecs]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
