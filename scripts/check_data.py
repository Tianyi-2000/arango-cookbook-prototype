"""Check that the knowledge base, gold set and tickets are consistent with each other and with the outline.

Run: python scripts/check_data.py   (or: make check)
Prints one line per check, then a summary. Exit code 0 = every check passed.
What each check means is listed in eval.md ("What `make check` covers").
"""
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.load import REWRITE_DATE, TODAY, in_effect, load_gold, load_kb, load_tickets  # noqa: E402

EXPECTED = {"articles": 68, "doc_ids": 51, "forms": 15, "states": 5, "lenders": 12, "lessors": 6, "stores": 25}
GOLD_TYPES = ["exact", "semantic", "multi_hop", "temporal", "conditional", "checklist", "unanswerable"]
GOLD_PER_TYPE = 8
TRICKY = {"time_boundary", "rule_conflict", "messy_input", "messy_kb"}
KINDS = {
    # kind: list of (version, effective_from, effective_to) the doc must have, in order
    "unchanged": [("2022", "2022-01-01", None)],
    "rewritten": [("2022", "2022-01-01", "2026-01-31"), ("2026", REWRITE_DATE, None)],
    "new":       [("2026", REWRITE_DATE, None)],
    "retired":   [("2022", "2022-01-01", "2026-01-31")],
}
SERVICES = {"appraisal", "lease_buyout", "home_pickup", "towing_non_running"}
MAX_TICKET_OVERLAP = 0.5
NUMBER_RE = re.compile(r"NW-[A-Z]{2,3}-\d+|\$?\d[\d,]*\d|\$?\d")  # form codes, dollar amounts, plain numbers

failures: list[str] = []


def check(name: str, problems: list[str]) -> None:
    """Print one result line; remember failures."""
    if problems:
        failures.append(name)
        print(f"FAIL  {name}")
        for p in problems[:15]:
            print(f"        - {p}")
        if len(problems) > 15:
            print(f"        ... and {len(problems) - 15} more")
    else:
        print(f"ok    {name}")


def valid_date(s) -> bool:
    try:
        date.fromisoformat(s)
        return True
    except (TypeError, ValueError):
        return False


def main() -> int:
    kb = load_kb()
    arts = kb["articles"]
    by_key = {a["_key"]: a for a in arts}
    by_doc = defaultdict(list)
    for a in arts:
        by_doc[a["doc_id"]].append(a)
    forms = {f["_key"]: f for f in kb["forms"]}
    states = {s["_key"] for s in kb["states"]}
    known = kb["known_issues"]
    known_broken = {(k["article"], k["target"]) for k in known if k["type"] == "broken_link"}
    known_retired = {(k["article"], k["code"]) for k in known if k["type"] == "retired_form_cited"}

    # --- counts --------------------------------------------------------------------------------
    got = {"articles": len(arts), "doc_ids": len(by_doc), **{k: len(kb[k]) for k in ["forms", "states", "lenders", "lessors", "stores"]}}
    check("counts match stage.md", [f"{k}: expected {v}, got {got[k]}" for k, v in EXPECTED.items() if got[k] != v])

    # --- article schema and version rules --------------------------------------------------------
    probs = []
    keys = Counter(a["_key"] for a in arts)
    probs += [f"duplicate _key {k}" for k, n in keys.items() if n > 1]
    for a in arts:
        if a["_key"] != f"{a['doc_id']}__{a['version']}":
            probs.append(f"{a['_key']}: _key should be {a['doc_id']}__{a['version']}")
        if a["kind"] not in KINDS:
            probs.append(f"{a['_key']}: unknown kind {a['kind']}")
        if a["side"] not in {"sell", "buy"}:
            probs.append(f"{a['_key']}: side must be sell or buy")
        if not valid_date(a["effective_from"]) or (a["effective_to"] is not None and not valid_date(a["effective_to"])):
            probs.append(f"{a['_key']}: bad dates")
        probs += [f"{a['_key']}: unknown state {s}" for s in a["states"] if s not in states]
        if not a["title"].strip() or len(a["text"].split()) < 25:
            probs.append(f"{a['_key']}: title missing or text under 25 words")
    check("article fields", probs)

    probs = []
    for doc_id, versions in by_doc.items():
        kinds = {v["kind"] for v in versions}
        if len(kinds) != 1:
            probs.append(f"{doc_id}: versions disagree on kind {kinds}")
            continue
        want = KINDS[kinds.pop()]
        have = sorted((v["version"], v["effective_from"], v["effective_to"]) for v in versions)
        if have != want:
            probs.append(f"{doc_id}: versions {have} don't match its kind, expected {want}")
    check("version chains follow their kind (no overlaps, no gaps)", probs)

    # --- links -----------------------------------------------------------------------------------
    probs = []
    for a in arts:
        for target in a["links"]:
            if target not in by_doc:
                if (a["_key"], target) not in known_broken:
                    probs.append(f"{a['_key']} links to missing article {target}")
                continue
            # no time travel: a version's text was written when it took effect, so everything it
            # links to must already exist on that day (an unchanged 2022 article can't link to a 2026 one)
            if not any(in_effect(t, a["effective_from"]) for t in by_doc[target]):
                probs.append(f"{a['_key']} links to {target}, which didn't exist on {a['effective_from']} when it was written")
    check("kb: links resolve, and no version links to an article from another time", probs)

    # --- form codes ------------------------------------------------------------------------------
    probs = []
    for a in arts:
        for code in a["codes"]:
            f = forms.get(code)
            if f is None:
                probs.append(f"{a['_key']} cites unknown form {code}")
                continue
            # no time travel: the form must be in use on the day the version took effect, unless the
            # text is explaining a replacement (it names the replacing form too, e.g. "NW-ODO-2 replaced NW-ODO-1")
            written = a["effective_from"]
            in_use_when_written = f["effective_from"] <= written and (f["retired_on"] is None or written < f["retired_on"])
            if not in_use_when_written and f["replaced_by"] not in a["codes"]:
                probs.append(f"{a['_key']} cites {code}, which wasn't in use on {written} when it was written")
            is_current_article = a["effective_to"] is None
            if is_current_article and f["status"] == "retired":
                mentions_replacement = f["replaced_by"] in a["codes"]
                if not mentions_replacement and (a["_key"], code) not in known_retired:
                    probs.append(f"current {a['_key']} cites retired {code} without naming {f['replaced_by']}, and it isn't a known issue")
    for f in forms.values():
        if f["replaced_by"] and f["replaced_by"] not in forms:
            probs.append(f"{f['_key']} replaced_by unknown form {f['replaced_by']}")
    check("form codes exist and fit the article's dates; retired forms only where expected", probs)

    # --- known issues are really there -------------------------------------------------------------
    probs = []
    for k in known:
        a = by_key.get(k["article"])
        if a is None:
            probs.append(f"{k['id']}: article {k['article']} doesn't exist")
        elif k["type"] == "broken_link" and k["target"] not in a["links"]:
            probs.append(f"{k['id']}: {k['article']} doesn't link to {k['target']}")
        elif k["type"] == "retired_form_cited" and k["code"] not in a["codes"]:
            probs.append(f"{k['id']}: {k['article']} doesn't cite {k['code']}")
    check("known KB issues are present as listed", probs)

    # --- structured records agree with the text ----------------------------------------------------
    probs = []
    ep = by_key["epayoff_network__2026"]["text"]
    for l in kb["lenders"]:
        if l["epayoff_network"] and l["name"] not in ep:
            probs.append(f"network lender {l['name']} not named in epayoff_network__2026")
        if not l["epayoff_network"] and l["name"] in ep:
            probs.append(f"non-network lender {l['name']} named in epayoff_network__2026")
    for version in ["lessor_buyouts__2022", "lessor_buyouts__2026"]:
        probs += [f"{l['name']} missing from {version}" for l in kb["lessors"] if l["name"] not in by_key[version]["text"]]
    for s in kb["states"]:
        if s["name"] not in by_key[f"duplicate_title_{s['_key']}__2022"]["text"]:
            probs.append(f"{s['name']} not named in its duplicate-title article")
    check("lenders, lessors and states agree with the articles", probs)

    # --- stores ------------------------------------------------------------------------------------
    probs = []
    for s in kb["stores"]:
        if s["state"] not in states:
            probs.append(f"{s['_key']}: unknown state {s['state']}")
        loc = s.get("location", {})
        if loc.get("type") != "Point" or len(loc.get("coordinates", [])) != 2:
            probs.append(f"{s['_key']}: location must be a GeoJSON Point [lon, lat]")
        if not set(s["services"]) <= SERVICES or "appraisal" not in s["services"]:
            probs.append(f"{s['_key']}: bad services {s['services']}")
        if s["state"] == "dunmore" and "home_pickup" in s["services"]:
            probs.append(f"{s['_key']}: Dunmore has no home pickup")
    check("stores", probs)

    # --- gold set ----------------------------------------------------------------------------------
    gold = load_gold()
    if not gold:
        print("skip  gold set (data/eval/gold.json not found)")
    else:
        probs = []
        ids = Counter(q["id"] for q in gold)
        probs += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
        per_type = Counter(q["type"] for q in gold)
        probs += [f"type {t}: {per_type.get(t, 0)} questions, expected {GOLD_PER_TYPE}" for t in GOLD_TYPES if per_type.get(t, 0) != GOLD_PER_TYPE]
        for q in gold:
            qid = q["id"]
            if q["type"] not in GOLD_TYPES:
                probs.append(f"{qid}: unknown type {q['type']}")
            for field in ["asked_on", "as_of"]:
                if not valid_date(q.get(field)):
                    probs.append(f"{qid}: {field} is not a date")
            if q.get("state") is not None and q["state"] not in states:
                probs.append(f"{qid}: unknown state {q['state']}")
            probs += [f"{qid}: unknown tricky tag {t}" for t in q.get("tricky", []) if t not in TRICKY]
            for k in q["gold_keys"] + q["trap_keys"]:
                if k not in by_key:
                    probs.append(f"{qid}: unknown article {k}")
            if set(q["gold_keys"]) & set(q["trap_keys"]):
                probs.append(f"{qid}: an article is both gold and trap")
            for k in q["gold_keys"]:
                if k in by_key and valid_date(q.get("as_of")) and not in_effect(by_key[k], q["as_of"]):
                    probs.append(f"{qid}: gold {k} isn't in effect on as_of {q['as_of']}")
            if q["answerable"] not in {"yes", "no", "partial"}:
                probs.append(f"{qid}: answerable must be yes, no or partial")
            if q["answerable"] == "no" and q["gold_keys"]:
                probs.append(f"{qid}: unanswerable question has gold articles")
            if q["answerable"] in {"yes", "partial"} and (not q["gold_keys"] or not q["answer_facts"]):
                probs.append(f"{qid}: answerable question needs gold_keys and answer_facts")
            if (q["type"] == "unanswerable") != (q["answerable"] in {"no", "partial"}):
                probs.append(f"{qid}: type unanswerable must go with answerable no/partial, and only then")
            for field in ["question", "perfect_answer", "what_makes_it_hard", "author", "status"]:
                if not q.get(field):
                    probs.append(f"{qid}: missing {field}")
        check(f"gold set ({len(gold)} questions)", probs)

    # --- candidates (drafts not yet in the gold set) --------------------------------------------------
    cand_path = Path(__file__).resolve().parents[1] / "data" / "eval" / "candidates.json"
    if cand_path.exists():
        import json
        cand = json.loads(cand_path.read_text())
        gold_by_id = {q["id"]: q for q in gold}
        probs = []
        for m in cand.get("messy_variants", []):
            orig = gold_by_id.get(m["variant_of"])
            if orig is None:
                probs.append(f"{m['id']}: variant_of unknown question {m['variant_of']}")
            elif m["question"].strip().lower() == orig["question"].strip().lower():
                probs.append(f"{m['id']}: wording is the same as {m['variant_of']}")
        for o in cand.get("off_topic", []):
            if o["gold_keys"] or o["answerable"] != "skip":
                probs.append(f"{o['id']}: off-topic messages have no gold articles and answerable 'skip'")
        for v in cand.get("vague", []):
            if v["vague_case"] not in {"A", "B", "C"}:
                probs.append(f"{v['id']}: vague_case must be A, B or C")
            if v["vague_case"] == "B" and (len(v["gold_keys"]) < 2 or v["require_all"]):
                probs.append(f"{v['id']}: an ambiguous (B) question lists 2+ readings with require_all false")
            for k in v["gold_keys"] + v["trap_keys"]:
                if k not in by_key:
                    probs.append(f"{v['id']}: unknown article {k}")
                elif k in v["gold_keys"] and not in_effect(by_key[k], v["as_of"]):
                    probs.append(f"{v['id']}: gold {k} isn't in effect on {v['as_of']}")
        n = sum(len(cand.get(g, [])) for g in ["messy_variants", "off_topic", "vague"])
        check(f"candidates ({n} drafts, not yet in the gold set)", probs)

    # --- tickets -----------------------------------------------------------------------------------
    tickets = load_tickets()
    if not tickets:
        print("skip  tickets (data/tickets/tickets.json not found)")
    else:
        probs = []
        for t in tickets:
            for k in t["cites"]:
                a = by_key.get(k)
                if a is None:
                    probs.append(f"{t['_key']}: cites unknown {k}")
                    continue
                if in_effect(a, t["created_at"]) == t["agent_error"]:
                    probs.append(f"{t['_key']}: cites {k}; in effect on {t['created_at']} must be the opposite of agent_error")
                if t["outdated"] != (not in_effect(a, TODAY)):
                    probs.append(f"{t['_key']}: outdated flag disagrees with {k}'s dates")
            if not t.get("customer") or not t.get("agent"):
                probs.append(f"{t['_key']}: missing text")
        check(f"tickets ({len(tickets)})", probs)

        # Faithfulness: every number and form code the agent states must appear in the article it used.
        # The agent saw only that one article, so anything else was invented (a hallucination).
        probs = []
        for t in tickets:
            # the agent may repeat numbers the customer said ("around 80 miles"), so the customer's text counts too
            source = " ".join(by_key[k]["text"] for k in t["cites"] if k in by_key) + " " + t.get("customer", "")
            for token in sorted(set(NUMBER_RE.findall(t.get("agent", "")))):
                # whole-number match: "1" must stand alone in the source, not hide inside "2026" or "NW-ODO-1"
                if not re.search(rf"(?<![\w$,-]){re.escape(token)}(?!\w|,\d)", source):
                    probs.append(f"{t['_key']} ({t['cites'][0]}): agent says '{token}', not in the cited article")
        check("ticket agents state only numbers and form codes from their cited article", probs)

        # Variety: near-duplicate customer messages make retrieval look easier or harder than it is (I-015).
        # Threshold fixed before the regenerated tickets were checked: no pair may share half its word 4-grams.
        def grams(text, n=4):
            w = re.findall(r"[a-z']+", text.lower())
            return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
        g = {t["_key"]: grams(t.get("customer", "")) for t in tickets}
        keys = list(g)
        probs = []
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if g[a] and g[b]:
                    overlap = len(g[a] & g[b]) / len(g[a] | g[b])
                    if overlap >= MAX_TICKET_OVERLAP:
                        probs.append(f"{a} and {b}: customer messages share {overlap:.0%} of their 4-grams")
        check(f"ticket customer messages aren't near-duplicates (under {MAX_TICKET_OVERLAP:.0%} 4-gram overlap)", probs)

    print()
    print("FAILED: " + ", ".join(failures) if failures else "All checks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
