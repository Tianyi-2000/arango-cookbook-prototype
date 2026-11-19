"""Freshness demo: a policy changes, and the next query already answers from the new version (D-027).

Runs in its own database, northwind_kb_demo, rebuilt from data/ each time, so the eval database is
never touched. Steps:
  1. ask a question with all four methods
  2. in ONE stream transaction: insert the new version of the policy (with its embedding and parsed
     edges), close the old version, add a `supersedes` edge, and point existing links at the new version
  3. ask the same question again, right after the commit: no re-indexing, no re-embedding of anything else
  4. walk `supersedes` to show what the answer replaced, and when

Run: python scripts/fresh_demo.py   (or: make fresh). Writes the transcript to data/eval/fresh_demo.md.
"""
import contextlib
import io
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cookbook import retrieve as R  # noqa: E402
from cookbook.build import article_edges, build  # noqa: E402
from cookbook.db import get_db, run  # noqa: E402
from cookbook.embed import article_text, embed_one  # noqa: E402
from cookbook.load import CODE_RE, LINK_RE, TODAY, load_kb  # noqa: E402

DEMO_DB = "northwind_kb_demo"
OLD_KEY = "getting_paid__2026"
# Chosen once, before this version of the demo ran, to match the article's own subject ("When and how
# you get paid"); a first wording ("how fast does the money get to my bank account?") didn't reach it
# with the vector methods at all (progress.md, 2026-11-17).
QUESTION = {"question": "How will you pay me for my car, and how long does it take?",
            "as_of": TODAY, "state": None}
NEW_KEY, NEW_VERSION_LABEL = "getting_paid__2026-11", "2026-11"
NEW_TEXT = ("Once the paperwork is signed, we pay you by bank draft or by instant transfer to your bank account, "
            "which arrives within minutes on any day of the week. Direct deposit no longer takes 1 to 3 business days. "
            "We no longer mail checks. If you used [home pickup](kb:home_pickup), the $99 fee is taken out of your payment. "
            "If there's a loan, we send the payoff to your lender within 2 business days, or the same day for lenders in our "
            "[e-payoff network](kb:epayoff_network), and you receive the amount left over. Keep making payments until your "
            "lender confirms the payoff ([Should I keep making loan payments?](kb:keep_paying_until_confirmed)). "
            "An extra payment comes back from your lender ([Getting back an extra loan payment](kb:lender_overpayment_refund)).")
CLOSE_OLD_ON = "2026-10-31"  # the day before TODAY

INSERT_NEW = "INSERT @doc INTO articles RETURN NEW._key"
CLOSE_OLD = "UPDATE @key WITH { effective_to: @closed } IN articles RETURN { key: NEW._key, effective_to: NEW.effective_to }"
ADD_SUPERSEDES = 'INSERT { _from: @new, _to: @old, on: @on } INTO supersedes RETURN CONCAT(NEW._from, " supersedes ", NEW._to)'
ADD_OWN_EDGES = "FOR e IN @edges INSERT e INTO @@col RETURN NEW._to"
RELINK = """
FOR e IN links_to
  FILTER e._to == @old
  INSERT { _from: e._from, _to: @new, doc_id: e.doc_id } INTO links_to
  RETURN NEW._from
"""
HISTORY = """
FOR v, e IN 0..5 OUTBOUND @start supersedes
  RETURN { version: v._key, in_effect: CONCAT(v.effective_from, " to ", v.effective_to || "now"), replaced_it_on: e.on }
"""


def show_results(db, label: str) -> None:
    """Each method's top 5, and where every version of the changed policy ranks."""
    print(f"\n{label}")
    print("| method | #1 | getting_paid versions in the top 5 |\n|---|---|---|")
    for m, (name, _) in R.METHODS.items():
        rows = R.retrieve(db, m, QUESTION, k=5)
        docs = {d["_key"]: d for d in run(db, "FOR d IN articles FILTER d._key IN @keys RETURN d",
                                           {"keys": [r["key"] for r in rows]}, show=False)}

        def tag(key):
            d = docs[key]
            ok = d["effective_from"] <= TODAY and (d["effective_to"] is None or TODAY <= d["effective_to"])
            return f"`{key}` {'current' if ok else '**STALE**'}"
        ranks = [f"#{i + 1} {tag(r['key'])}" for i, r in enumerate(rows) if r["key"].startswith("getting_paid__")]
        print(f"| {m} {name} | {tag(rows[0]['key'])} | {' · '.join(ranks) or 'none'} |")


def main() -> int:
    print(f"Building {DEMO_DB} from data/ (a copy; the eval database is not touched)")
    build(DEMO_DB, verbose=False)
    db = get_db(DEMO_DB)
    view = db.view("kb_view")
    print(f"kb_view commitIntervalMsec = {view.get('commitIntervalMsec', view.get('commit_interval_msec'))} "
          "(BM25 queries below use waitForSync, so they see a commit immediately)")
    print(f"\nQuestion (asked {TODAY}): \"{QUESTION['question']}\"")
    show_results(db, "### 1. Before the policy change")

    kb = load_kb()
    old = next(a for a in kb["articles"] if a["_key"] == OLD_KEY)
    new = {**{k: v for k, v in old.items() if k not in {"codes", "links"}},  # same doc, section, side, states
           "_key": NEW_KEY, "version": NEW_VERSION_LABEL, "effective_from": TODAY, "effective_to": None, "text": NEW_TEXT}
    new["codes"] = sorted(set(CODE_RE.findall(new["text"])))
    new["links"] = [doc_id for _l, doc_id in LINK_RE.findall(new["text"])]
    by_doc = defaultdict(list)
    for a in kb["articles"]:
        by_doc[a["doc_id"]].append(a)
    edges = article_edges(new, kb, by_doc)
    new.pop("links")
    t0 = time.perf_counter()
    new["embedding"] = embed_one(article_text(new))  # only the new version is embedded
    t_embed = time.perf_counter() - t0

    print("\n### 2. The policy changes: one stream transaction")
    txn = db.begin_transaction(write=["articles", "supersedes", "links_to", "uses_form", "applies_in",
                                      "about_lender", "about_lessor"])
    t0 = time.perf_counter()
    try:
        print("inserted:", run(txn, INSERT_NEW, {"doc": new}))
        print("closed:  ", run(txn, CLOSE_OLD, {"key": OLD_KEY, "closed": CLOSE_OLD_ON}))
        print("edge:    ", run(txn, ADD_SUPERSEDES, {"new": f"articles/{new['_key']}", "old": f"articles/{OLD_KEY}", "on": TODAY}))
        for col, rows in edges.items():
            print(f"{col}:", run(txn, ADD_OWN_EDGES, {"edges": rows, "@col": col}, show=False), "(parsed from the new text)")
        print("re-linked:", run(txn, RELINK, {"old": f"articles/{OLD_KEY}", "new": f"articles/{new['_key']}"}))
        txn.commit_transaction()
    except Exception:
        txn.abort_transaction()
        raise
    t_txn = time.perf_counter() - t0
    print(f"\nembedding the new version: {t_embed * 1000:.0f} ms · transaction: {t_txn * 1000:.0f} ms · nothing re-indexed")

    t0 = time.perf_counter()
    show_results(db, "### 3. The same question, right after the commit")
    print(f"\n(every method after the commit: {(time.perf_counter() - t0) * 1000:.0f} ms)")

    print("\n### 4. What the current answer replaced: walk `supersedes`")
    for r in run(db, HISTORY, {"start": f"articles/{new['_key']}"}):
        print("  ", r)
    return 0


if __name__ == "__main__":
    buf = io.StringIO()

    class Tee(io.TextIOBase):
        def write(self, s):
            sys.__stdout__.write(s)
            buf.write(s)
            return len(s)

    with contextlib.redirect_stdout(Tee()):
        code = main()
    (ROOT / "data" / "eval" / "fresh_demo.md").write_text("# Freshness demo transcript (`make fresh`)\n\n```text\n" + buf.getvalue() + "```\n")
    sys.exit(code)
