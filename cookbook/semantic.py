"""The semantic graph layer: concepts and relations extracted by Claude from each article version.

Claude only proposes names and links per article (scripts/extract_semantic.py, cached in data/kb/semantic/).
Everything after that is our own code: name normalisation (entity resolution), merging into one
`concepts` collection, and the `mentions` / `relates` edges loaded by cookbook/build.py.
"""
import json
import re

from cookbook.load import KB

SEM_DIR = KB / "semantic"
KINDS = ["situation", "document", "party", "requirement", "action", "service"]
REL_TYPES = ["requires", "issued_by", "applies_when", "alternative_to", "part_of"]
_DET = re.compile(r"^(a|an|the|your|our)\s+")


def normalize(name: str) -> str:
    """Entity resolution, rule-based and fixed before any output was seen (data/kb/semantic_gold.json note).
    lowercase; '-' and punctuation become spaces; leading a/an/the/your/our dropped; the last word loses a
    trailing 's' if it is longer than 3 letters and doesn't end in 'ss' ("payoff letters" = "payoff letter")."""
    s = re.sub(r"[^a-z0-9' ]+", " ", name.lower().replace("-", " ")).replace("'", "")
    s = _DET.sub("", re.sub(r"\s+", " ", s).strip())
    words = s.split()
    if words and len(words[-1]) > 3 and words[-1].endswith("s") and not words[-1].endswith("ss"):
        words[-1] = words[-1][:-1]
    return " ".join(words)


def concept_key(name: str) -> str:
    return normalize(name).replace(" ", "_")


def load_semantic() -> dict[str, dict]:
    """{article version key: {"concepts": [...], "relations": [...]}} for every cached extraction."""
    out = {}
    for p in sorted(SEM_DIR.glob("*.json")):
        body = json.loads(p.read_text())
        out[body["key"]] = body
    return out


def matches(extracted: str, names: list[str]) -> bool:
    """The match rule from data/kb/semantic_gold.json: equal after normalising, or whole-word containment
    where the contained name has at least 2 words."""
    e = normalize(extracted)
    for n in map(normalize, names):
        if e == n:
            return True
        short, long_ = (e, n) if len(e) <= len(n) else (n, e)
        if len(short.split()) >= 2 and re.search(rf"\b{re.escape(short)}\b", long_):
            return True
    return False
