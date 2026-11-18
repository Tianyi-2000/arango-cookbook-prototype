"""Answer eval (stage 4, D-028): retrieve with M2 and M4, answer with Claude from the top 5, judge each answer.

  python scripts/run_answers.py                 # dry run: prompts and cost estimate, no API calls
  python scripts/run_answers.py --run           # call the API; stops before the spend cap is crossed
  python scripts/run_answers.py --report        # tables from the cached answers only

Every answer and judgement is cached in data/eval/answers/<method>/<qid>.json, so a rerun never pays twice.
Needs the frozen gold set and `make load`. Signs in with the `ant auth login` profile (I-014).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from cookbook import answer as A  # noqa: E402
from cookbook import retrieve as R  # noqa: E402
from cookbook.db import get_db  # noqa: E402
from cookbook.load import DATA, in_effect, load_articles, load_gold  # noqa: E402
from run_eval import frozen_ok  # noqa: E402

METHODS = ["M2", "M4"]
SPEND_CAP = 6.00          # $ for this script in total (D-028); with the $3.10 spent on tickets, under $10
EST_OUT = {"answer": 700, "judge": 350}  # output tokens per call, thinking included (estimate)
OUT = DATA / "eval" / "answers"


def cached(method: str, qid: str) -> dict:
    p = OUT / method / f"{qid}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def save(method: str, qid: str, row: dict) -> None:
    (OUT / method).mkdir(parents=True, exist_ok=True)
    (OUT / method / f"{qid}.json").write_text(json.dumps(row, indent=1, ensure_ascii=False) + "\n")


def spent() -> float:
    return sum(json.loads(p.read_text()).get("cost", 0) for p in OUT.rglob("*.json")) if OUT.exists() else 0.0


def report(gold: list[dict], arts: dict) -> str:
    L = ["| method | facts found (answerable, n) | all facts (n) | cites a stale version | cites a trap | declines when not covered (n) | cost |",
         "|---|---|---|---|---|---|---|"]
    for m in METHODS:
        rows = [(q, cached(m, q["id"])) for q in gold]
        rows = [(q, r) for q, r in rows if r.get("judge")]
        ans = [(q, r) for q, r in rows if q["answerable"] == "yes"]
        unans = [(q, r) for q, r in rows if q["answerable"] in {"no", "partial"}]
        facts = [sum(f["present"] for f in r["judge"]["facts"]) / max(1, len(r["judge"]["facts"])) for q, r in ans]
        allf = [all(f["present"] for f in r["judge"]["facts"]) for q, r in ans]
        stale = [any(k in arts and not in_effect(arts[k], q["as_of"]) for k in r["cited_keys"]) for q, r in rows]
        trap = [bool(set(r["cited_keys"]) & set(q["trap_keys"])) for q, r in rows]
        decl = [r["judge"]["declines_uncovered"] for q, r in unans]
        c = sum(r.get("cost", 0) for _, r in rows)

        def pct(xs):
            return f"{sum(xs) / len(xs):.2f}" if xs else "—"
        L.append(f"| {m} {R.METHODS[m][0]} | {pct(facts)} ({len(ans)}) | {pct(allf)} ({len(ans)}) | {pct(stale)} | {pct(trap)} | {pct(decl)} ({len(unans)}) | ${c:.2f} |")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    ok, why = frozen_ok()
    if not ok:
        print("refusing to run on the gold set:", why)
        return 1
    gold = load_gold()
    arts = {a["_key"]: a for a in load_articles()}
    if args.report:
        md = report(gold, arts)
        print(md)
        (DATA / "eval" / "scores" / "answers.md").write_text(f"# Answer eval ({A.MODEL})\n\n{md}\n")
        return 0
    db = get_db()
    todo = [(m, q) for m in METHODS for q in gold if not cached(m, q["id"]).get("judge")]
    prompts = {}
    for m, q in todo:
        keys = [r["key"] for r in R.retrieve(db, m, q, k=A.CONTEXT_K)]
        prompts[(m, q["id"])] = (keys, A.answer_prompt(q, [arts[k] for k in keys]))
    est_in = sum(len(A.ANSWER_SYSTEM + p) / 4 + 400 for _, p in prompts.values())  # + judge input, roughly
    est = est_in / 1e6 * A.PRICE_IN + len(todo) * (EST_OUT["answer"] + EST_OUT["judge"]) / 1e6 * A.PRICE_OUT
    print(f"{len(todo)} answers to make ({', '.join(METHODS)} x {len(gold)} questions, minus cached), each judged once")
    print(f"estimated cost ${est:.2f} · already spent ${spent():.2f} · cap ${SPEND_CAP:.2f} · model {A.MODEL}")
    if not args.run:
        if prompts:
            (m, qid), (keys, p) = next(iter(prompts.items()))
            print(f"\nexample prompt ({m}, {qid}):\n--- system ---\n{A.ANSWER_SYSTEM}\n--- user ---\n{p}")
        print("\ndry run only; add --run to call the API")
        return 0

    import anthropic
    client = anthropic.Anthropic()
    for i, (m, q) in enumerate(todo, 1):
        per_call = (len(prompts[(m, q['id'])][1]) / 4 + 400) / 1e6 * A.PRICE_IN + sum(EST_OUT.values()) / 1e6 * A.PRICE_OUT
        if spent() + 2 * per_call > SPEND_CAP:
            print(f"stopping: spent ${spent():.2f}, the next answer could cross the ${SPEND_CAP:.2f} cap")
            break
        keys, prompt = prompts[(m, q["id"])]
        body, meta = A.call(client, A.ANSWER_SYSTEM, prompt, A.ANSWER_SCHEMA, effort="medium")
        jbody, jmeta = A.call(client, A.JUDGE_SYSTEM, A.judge_prompt(q, body["answer"]), A.JUDGE_SCHEMA, effort="low")
        row = {"qid": q["id"], "method": m, "retrieved": keys, **body, "answer_meta": meta,
               "judge": jbody, "judge_meta": jmeta, "cost": round(meta["cost"] + jmeta["cost"], 5)}
        save(m, q["id"], row)
        found = sum(f["present"] for f in jbody["facts"])
        print(f"[{i}/{len(todo)}] {m} {q['id']}: facts {found}/{len(jbody['facts'])} · cites {body['cited_keys']} · ${row['cost']:.3f} (total ${spent():.2f})")
    print("\n" + report(gold, arts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
