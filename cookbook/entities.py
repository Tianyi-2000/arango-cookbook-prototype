"""Find the forms, lenders and leasing companies a question names (D-032). No LLM: a dictionary built from the KB.

  form codes        NW-XXX-n, exact (the same regex the KB parser uses)
  lenders, lessors  the full name, or the name without trailing generic words ("Pinewood Federal Credit Union"
                    -> "Pinewood"); case-insensitive, whole words, longest match first. An alias shared by two
                    companies ("Harbor": Harbor Leasing and Harbor Trust Bank) matches both. An alias that appears
                    in more than MAX_DF article versions is dropped (today only "Northwind", 16).

The same dictionary maps an answer's list items back to keys when list questions are scored (D-035).
States are not entry points (every question has one, and the filter already uses it), but are in the item map.
"""
import re
from functools import lru_cache

from cookbook.load import CODE_RE, load_kb

GENERIC = {"bank", "credit", "union", "federal", "leasing", "lease", "co", "auto", "motor", "finance", "loans", "trust"}
MAX_DF = 10  # same document-frequency limit as the semantic layer (D-030)


def short_name(name: str) -> str:
    words = name.split()
    while len(words) > 1 and words[-1].lower() in GENERIC:
        words.pop()
    return " ".join(words)


def _has(alias: str, text: str) -> bool:
    return re.search(r"\b" + re.escape(alias) + r"\b", text, re.I) is not None


@lru_cache(maxsize=1)
def aliases() -> list[tuple[str, str]]:
    """[(alias, node id)], longest alias first. Node ids are ArangoDB _ids: lenders/..., lessors/..."""
    kb = load_kb()
    texts = [a["title"] + " " + a["text"] for a in kb["articles"]]
    out = []
    for coll in ["lenders", "lessors"]:
        for e in kb[coll]:
            for alias in sorted({e["name"], short_name(e["name"])}):
                df = sum(_has(alias, t) for t in texts)
                if alias == e["name"] or df <= MAX_DF:  # a full name is always kept
                    out.append((alias, f"{coll}/{e['_key']}"))
    return sorted(out, key=lambda x: (-len(x[0]), x[0], x[1]))


def link_entities(text: str) -> list[str]:
    """Node ids named in `text`: forms, lenders, lessors. Sorted, no duplicates."""
    found = {f"forms/{c}" for c in CODE_RE.findall(text.upper())}
    taken = []  # character spans already matched by a longer alias
    for alias, node in aliases():
        for m in re.finditer(r"\b" + re.escape(alias) + r"\b", text, re.I):
            span = m.span()
            if any(s <= span[0] and span[1] <= e and (s, e) != span for s, e in taken):
                continue  # inside a longer match ("Summit" inside "Summit Peak Bank")
            taken.append(span)
            found.add(node)
    known = {f"forms/{f['_key']}" for f in load_kb()["forms"]}
    return sorted(n for n in found if not n.startswith("forms/") or n in known)


@lru_cache(maxsize=1)
def _item_names() -> dict[str, dict[str, str]]:
    """For scoring list answers: {kind: {lowercased name or alias: key}}."""
    kb = load_kb()
    names = {"form": {}, "lender": {}, "lessor": {}, "state": {}, "article": {}}
    for f in kb["forms"]:
        names["form"][f["_key"].lower()] = f["_key"]
        names["form"][f["name"].lower()] = f["_key"]
    for kind, coll in [("lender", "lenders"), ("lessor", "lessors")]:
        for e in kb[coll]:
            for alias in {e["name"], short_name(e["name"])}:
                names[kind][alias.lower()] = e["_key"]
    for s in kb["states"]:
        names["state"][s["name"].lower()] = s["_key"]
        names["state"][s["_key"]] = s["_key"]
    for a in kb["articles"]:
        names["article"][a["title"].lower()] = a["doc_id"]
        names["article"][a["doc_id"]] = a["doc_id"]
        names["article"][a["_key"]] = a["doc_id"]
    return names


def item_key(kind: str, item: str) -> str | None:
    """Map one list item from an answer ("Harbor Trust Bank", "NW-POA-1 (power of attorney)", an article title)
    to its key, or None. Exact name first, then a form code or a known name inside the item."""
    names = _item_names()[kind]
    s = item.strip().strip("'\"“”").lower()
    if s in names:
        return names[s]
    if kind == "form":
        codes = CODE_RE.findall(item.upper())
        return codes[0] if codes else None
    hits = {key for name, key in names.items() if len(name) > 3 and _has(name, s)}
    return hits.pop() if len(hits) == 1 else None
