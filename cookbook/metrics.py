"""Retrieval metrics for one ranked list of article version keys (D-026). All return a float in [0, 1].

`ranked` is best first. `gold` is the question's gold_keys; when `require_all` is False, finding any
one gold article counts as full recall (ambiguous questions, eval.md case B).
"""
from math import log2

from cookbook.load import in_effect


def recall_at(ranked: list[str], gold: list[str], k: int, require_all: bool = True) -> float:
    found = set(ranked[:k]) & set(gold)
    if not require_all:
        return float(bool(found))
    return len(found) / len(gold)


def all_gold_at(ranked: list[str], gold: list[str], k: int) -> float:
    return float(set(gold) <= set(ranked[:k]))


def mrr_at(ranked: list[str], gold: list[str], k: int) -> float:
    for i, key in enumerate(ranked[:k]):
        if key in gold:
            return 1 / (i + 1)
    return 0.0


def ndcg_at(ranked: list[str], gold: list[str], k: int) -> float:
    """Binary relevance: a gold article at rank i (0-based) adds 1/log2(i+2); divided by the best possible."""
    dcg = sum(1 / log2(i + 2) for i, key in enumerate(ranked[:k]) if key in gold)
    ideal = sum(1 / log2(i + 2) for i in range(min(len(gold), k)))
    return dcg / ideal


def stale_at(ranked: list[str], arts: dict, as_of: str, k: int) -> float:
    """1 if any of the top k is a version that wasn't in effect on as_of (an outdated or not-yet-valid copy)."""
    return float(any(not in_effect(arts[key], as_of) for key in ranked[:k]))


def trap_at(ranked: list[str], traps: list[str], k: int) -> float:
    return float(bool(set(ranked[:k]) & set(traps)))


def score_question(ranked: list[str], q: dict, arts: dict) -> dict:
    """Every metric for one question and one method."""
    g, ra = q["gold_keys"], q.get("require_all", True)
    return {
        "recall@5": recall_at(ranked, g, 5, ra),
        "recall@10": recall_at(ranked, g, 10, ra),
        "all_gold@5": all_gold_at(ranked, g, 5) if ra else recall_at(ranked, g, 5, ra),
        "mrr@10": mrr_at(ranked, g, 10),
        "ndcg@5": ndcg_at(ranked, g, 5),
        "stale@5": stale_at(ranked, arts, q["as_of"], 5),
        "trap@5": trap_at(ranked, q["trap_keys"], 5),
    }


METRICS = ["recall@5", "recall@10", "all_gold@5", "mrr@10", "ndcg@5", "stale@5", "trap@5"]
LOWER_IS_BETTER = {"stale@5", "trap@5"}
