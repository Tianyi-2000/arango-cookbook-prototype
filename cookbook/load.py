"""Load the knowledge base from data/ and parse the structure that lives inside article text.

The structural graph is built from what this module parses: `[label](kb:<doc_id>)` links and
`NW-XXX-n` form codes. Nothing about the graph is written by hand.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
KB = DATA / "kb"

TODAY = "2026-11-01"           # fixed "today" so results don't depend on the day you run this (D-008)
REWRITE_DATE = "2026-02-01"    # the help center was rewritten on this date

LINK_RE = re.compile(r"\[([^\]]+)\]\(kb:([a-z0-9_]+)\)")
CODE_RE = re.compile(r"\bNW-[A-Z]{2,3}-\d+\b")


def plain(text: str) -> str:
    """Article text with `[label](kb:doc_id)` links reduced to their label (what a reader sees)."""
    return LINK_RE.sub(lambda m: m.group(1), text)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_articles() -> list[dict]:
    """All article versions, from every file in data/kb/articles/, with `codes` and `links` parsed from the text."""
    articles = []
    for path in sorted((KB / "articles").glob("*.json")):
        articles.extend(load_json(path))
    for a in articles:
        a["codes"] = sorted(set(CODE_RE.findall(a["text"])))
        a["links"] = [doc_id for _label, doc_id in LINK_RE.findall(a["text"])]
    return articles


def load_kb() -> dict:
    """Everything in data/kb/ as one dict of lists."""
    kb = {"articles": load_articles()}
    for name in ["forms", "states", "lenders", "lessors", "stores", "known_issues"]:
        kb[name] = load_json(KB / f"{name}.json")
    return kb


def load_gold() -> list[dict]:
    path = DATA / "eval" / "gold.json"
    return load_json(path)["questions"] if path.exists() else []


def load_reserve() -> list[dict]:
    """Questions not in the frozen 30 (D-024). Retrieval code is debugged on these, never on the gold set."""
    path = DATA / "eval" / "gold_reserve.json"
    return load_json(path)["questions"] if path.exists() else []


def load_gold_v2(dev: bool = False) -> list[dict]:
    """Gold v2 (D-031): chain and structural questions. dev=True gives the 8 debugging questions."""
    path = DATA / "eval" / ("gold_v2_dev.json" if dev else "gold_v2.json")
    return load_json(path)["questions"] if path.exists() else []


def load_candidates() -> dict:
    """Draft questions not yet in the gold set (messy variants, off-topic, vague); empty if none."""
    path = DATA / "eval" / "candidates.json"
    return load_json(path) if path.exists() else {}


def load_tickets() -> list[dict]:
    path = DATA / "tickets" / "tickets.json"
    return load_json(path) if path.exists() else []


def in_effect(article: dict, date: str) -> bool:
    """True if this article version was in effect on `date` (ISO strings compare correctly)."""
    return article["effective_from"] <= date and (article["effective_to"] is None or date <= article["effective_to"])


def version_on(articles: list[dict], doc_id: str, date: str) -> dict | None:
    """The version of `doc_id` in effect on `date`, or None if the article didn't exist then."""
    for a in articles:
        if a["doc_id"] == doc_id and in_effect(a, date):
            return a
    return None
