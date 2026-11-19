"""Retrieval eval: run M1-M4 on the frozen gold set and print the tables (eval.md, D-026).

  python scripts/run_eval.py               # the frozen gold set; writes data/eval/scores/latest.{json,md}
  python scripts/run_eval.py --reserve     # the reserve questions, for debugging; writes nothing

The gold run refuses to start unless data/eval/gold.json matches the sha256 in data/eval/FROZEN.
After a gold run, every headline number is compared with the previous run (D-018): if one got worse,
the script says so and exits with code 2, and the work stops until Tianyi has looked.
Unanswerable questions have no retrieval metrics; they are scored in the answer eval.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cookbook import retrieve as R  # noqa: E402
from cookbook.db import get_db  # noqa: E402
from cookbook.embed import MODEL_NAME  # noqa: E402
from cookbook.load import DATA, load_articles, load_gold, load_reserve  # noqa: E402
from cookbook.metrics import LOWER_IS_BETTER, METRICS, score_question  # noqa: E402

SCORES = DATA / "eval" / "scores"
TYPES = ["exact", "semantic", "multi_hop", "temporal", "conditional", "checklist"]
SLICES = {"all": TYPES, "multi_hop + checklist": ["multi_hop", "checklist"],
          "temporal + conditional": ["temporal", "conditional"]}
HEADLINE = [("all", "recall@5"), ("all", "recall@10"), ("multi_hop + checklist", "recall@5"), ("multi_hop + checklist", "all_gold@5"),
            ("all", "mrr@10"), ("all", "ndcg@5"), ("all", "stale@5"), ("all", "trap@5")]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_ok() -> tuple[bool, str]:
    f = DATA / "eval" / "FROZEN"
    if not f.exists():
        return False, "data/eval/FROZEN not found: the gold set isn't frozen yet (make freeze)"
    want = json.loads(f.read_text())["sha256"]
    got = sha256(DATA / "eval" / "gold.json")
    return (got == want, f"gold.json sha256 {got[:12]} != FROZEN {want[:12]}") if got != want else (True, "")


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def run_all(db, questions: list[dict], arts: dict) -> dict:
    """{qid: {method: {"ranked": [...], "via": {...}, "scores": {...}}}}"""
    out = {}
    for q in questions:
        out[q["id"]] = {}
        for m in R.METHODS:
            rows = R.retrieve(db, m, q)
            ranked = [r["key"] for r in rows]
            out[q["id"]][m] = {"ranked": ranked, "via": {r["key"]: r["via"] for r in rows if r.get("via")},
                               "scores": score_question(ranked, q, arts)}
    return out


def aggregate(results: dict, questions: list[dict]) -> dict:
    """{slice or type: {"n": n, method: {metric: mean}}}"""
    by_id = {q["id"]: q for q in questions}
    groups = {**SLICES, **{t: [t] for t in TYPES}}
    agg = {}
    for name, types in groups.items():
        ids = [i for i in results if by_id[i]["type"] in types]
        agg[name] = {"n": len(ids), **{m: {k: mean([results[i][m]["scores"][k] for i in ids]) for k in METRICS}
                                        for m in R.METHODS}}
    return agg


def tables(agg: dict, results: dict, questions: list[dict]) -> str:
    by_id = {q["id"]: q for q in questions}
    L = ["### Headline (higher is better, except stale and trap)", ""]
    head = ["method"] + [f"{k} · {s} (n={agg[s]['n']})" for s, k in HEADLINE]
    L += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for m, (name, _) in R.METHODS.items():
        L.append(f"| {m} {name} | " + " | ".join(f"{agg[s][m][k]:.2f}" for s, k in HEADLINE) + " |")
    L += ["", "### Recall@5 by question type", ""]
    L += ["| type | n | " + " | ".join(R.METHODS) + " |", "|---|---|" + "---|" * len(R.METHODS)]
    for t in TYPES:
        L.append(f"| {t} | {agg[t]['n']} | " + " | ".join(f"{agg[t][m]['recall@5']:.2f}" for m in R.METHODS) + " |")
    L += ["", "### Per question: where each step changed Recall@5", ""]
    steps = [("M1", "M2"), ("M2", "M3")] + [("M3", g) for g in R.METHODS if g not in {"M1", "M2", "M3"}]
    for a, b in steps:
        wins, losses = [], []
        for i, r in results.items():
            d = r[b]["scores"]["recall@5"] - r[a]["scores"]["recall@5"]
            if d:
                g = set(by_id[i]["gold_keys"])
                gained = sorted((set(r[b]["ranked"][:5]) - set(r[a]["ranked"][:5])) & g)
                lost = sorted((set(r[a]["ranked"][:5]) - set(r[b]["ranked"][:5])) & g)
                via = [f"{k} via {r[b]['via'][k]}" for k in gained if k in r[b]["via"]]
                line = f"- {i} ({by_id[i]['type']}) {d:+.2f}: " + "; ".join(
                    ([f"gained {', '.join(gained)}"] if gained else []) + ([f"lost {', '.join(lost)}"] if lost else [])
                    + ([f"path: {', '.join(via)}"] if via else []))
                (wins if d > 0 else losses).append(line)
        L += [f"**{a} → {b}:** {len(wins)} better, {len(losses)} worse, {len(results) - len(wins) - len(losses)} unchanged", ""]
        L += wins + losses + [""]
    return "\n".join(L)


def compare_with_previous(new: dict, old: dict) -> list[str]:
    drops = []
    for m in R.METHODS:
        for s, k in HEADLINE:
            a, b = old["aggregate"][s][m][k], new["aggregate"][s][m][k]
            worse = b > a + 1e-9 if k in LOWER_IS_BETTER else b < a - 1e-9
            if worse:
                drops.append(f"{m} {k} ({s}): {a:.3f} -> {b:.3f}")
    return drops


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reserve", action="store_true", help="run on the reserve questions (debugging, writes nothing)")
    args = ap.parse_args()
    if not args.reserve:
        ok, why = frozen_ok()
        if not ok:
            print("refusing to run on the gold set:", why)
            return 1
    questions = [q for q in (load_reserve() if args.reserve else load_gold()) if q["type"] != "unanswerable"]
    arts = {a["_key"]: a for a in load_articles()}
    db = get_db()
    print(f"{'reserve' if args.reserve else 'gold'}: {len(questions)} answerable questions x {len(R.METHODS)} methods\n")
    print("The four queries:\n")
    for m, (name, aql) in R.METHODS.items():
        print(f"-- {m} {name}{aql}")
    results = run_all(db, questions, arts)
    agg = aggregate(results, questions)
    md = tables(agg, results, questions)
    print(md)
    if args.reserve:
        return 0

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    out = {"ran_at": datetime.now().isoformat(timespec="seconds"), "commit": commit,
           "gold_sha256": sha256(DATA / "eval" / "gold.json"),
           "params": {"k": R.K, "n_entry": R.N_ENTRY, "decay": R.DECAY, "graph_edges": R.GRAPH_EDGES, "embedding": MODEL_NAME},
           "aggregate": agg, "per_question": results}
    SCORES.mkdir(parents=True, exist_ok=True)
    latest = SCORES / "latest.json"
    drops = []
    if latest.exists():
        old = json.loads(latest.read_text())
        drops = compare_with_previous(out, old)
        (SCORES / "history").mkdir(exist_ok=True)
        latest.rename(SCORES / "history" / f"{old['ran_at'].replace(':', '')}.json")
    latest.write_text(json.dumps(out, indent=1) + "\n")
    (SCORES / "latest.md").write_text(f"# Retrieval scores\n\nRun {out['ran_at']} · commit {commit} · gold sha256 {out['gold_sha256'][:12]} · "
                                      f"k={R.K}, entries={R.N_ENTRY}, decay={R.DECAY}\n\n{md}\n")
    print(f"wrote {latest.relative_to(ROOT)} and latest.md")
    if drops:
        print("\nSCORE DROPPED since the previous run (D-018: stop unless progress.md names a change meant to cause it):")
        print("\n".join("  " + d for d in drops))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
