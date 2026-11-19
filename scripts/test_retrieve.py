"""Checks on the retrieval methods, run on the reserve questions only (never the frozen gold set).

1. every method runs on every reserve question and returns k rows
2. M2, M3 and M4 use the vector index, also when a state filter is set (I-020)
3. M3 and M4 never return a version that isn't in effect on as_of, or an article for another state
4. M4-M6 never drop the article M3 ranks first (the graph can raise scores, never lower them)
5. M4-M6 give the same list twice in a row (ties are broken by key, I-021)

Needs `make load` first. Run: python scripts/test_retrieve.py   (or: make test-retrieve)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.db import get_db  # noqa: E402
from cookbook.load import in_effect, load_articles, load_reserve  # noqa: E402
from cookbook.retrieve import K, METHODS, bind_vars, retrieve  # noqa: E402


def main() -> int:
    db = get_db()
    arts = {a["_key"]: a for a in load_articles()}
    qs = load_reserve()
    probs = []
    stated = next(q for q in qs if q["state"])
    for m in ["M2", "M3", "M4", "M5", "M6"]:
        plan = str(db.aql.explain(METHODS[m][1], bind_vars=bind_vars(m, stated)))
        if "EnumerateNearVectorNode" not in plan:
            probs.append(f"{m}: does not use the vector index ({stated['id']}, state {stated['state']})")
    for q in qs:
        rows = {}
        for m in METHODS:
            try:
                rows[m] = retrieve(db, m, q)
            except Exception as e:  # noqa: BLE001 - report every failure, keep going
                probs.append(f"{q['id']} {m}: {str(e)[:100]}")
                continue
            if len(rows[m]) != K and m != "M1":  # BM25 may match fewer than k documents
                probs.append(f"{q['id']} {m}: {len(rows[m])} rows, expected {K}")
            if m in {"M3", "M4", "M5", "M6"}:
                for r in rows[m]:
                    a = arts[r["key"]]
                    if not in_effect(a, q["as_of"]):
                        probs.append(f"{q['id']} {m}: {r['key']} not in effect on {q['as_of']}")
                    if q["state"] and a["states"] and q["state"] not in a["states"]:
                        probs.append(f"{q['id']} {m}: {r['key']} is for {a['states']}, question is {q['state']}")
        for g in ["M4", "M5", "M6"]:
            if "M3" in rows and g in rows and rows["M3"]:
                if rows["M3"][0]["key"] not in {r["key"] for r in rows[g]}:
                    probs.append(f"{q['id']}: {g} dropped M3's first hit {rows['M3'][0]['key']}")
                again = retrieve(db, g, q)
                if [(r["key"], r["score"]) for r in again] != [(r["key"], r["score"]) for r in rows[g]]:
                    probs.append(f"{q['id']}: {g} is not deterministic")
    for p in probs:
        print("FAIL ", p)
    print(f"{len(qs)} reserve questions x {len(METHODS)} methods: {'OK' if not probs else f'{len(probs)} problems'}")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
