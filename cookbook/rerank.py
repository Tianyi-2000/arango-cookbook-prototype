"""Rank narrow (D-033): a cross-encoder reads the question and one candidate article together and scores how well
the article answers it. Unlike the embedding model (a bi-encoder: question and article are embedded separately,
so article vectors can be precomputed), a cross-encoder needs the question, so it runs at query time and only on
the small pool that wide retrieval found.

Model: cross-encoder/ms-marco-MiniLM-L-6-v2 (about 90 MB, local CPU), trained on MS MARCO: real Bing queries with
the passages people marked as answering them. Its score is a logit: only the order matters.
"""
from functools import lru_cache

from cookbook.load import plain

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
BATCH = 32  # fixed, so scores are computed the same way every run


@lru_cache(maxsize=1)
def model():
    import os
    import warnings
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    warnings.filterwarnings("ignore")
    from sentence_transformers import CrossEncoder
    return CrossEncoder(MODEL_NAME, device="cpu")


def passage(c: dict) -> str:
    return f"{c['title']}. {plain(c['text'])}"


def rerank(question: str, cands: list[dict], k: int) -> list[dict]:
    """Score every (question, candidate) pair; best first, ties broken by key; top k."""
    if not cands:
        return []
    scores = model().predict([(question, passage(c)) for c in cands], batch_size=BATCH, show_progress_bar=False)
    ranked = sorted(zip(cands, scores), key=lambda x: (-float(x[1]), x[0]["key"]))
    return [{"key": c["key"], "score": round(float(s), 4), "sources": c.get("sources", [])} for c, s in ranked[:k]]
