"""Answer eval (stage 4, D-028/D-029): for every method, answer each gold question from its top 5 with Claude,
then have a different model judge the answer. Three runs, to see run-to-run noise.

  python scripts/run_answers.py                  # dry run: cost estimate and one prompt, no API calls
  python scripts/run_answers.py --one            # one answer + one judgement (checks both models work)
  python scripts/run_answers.py --run            # everything not cached yet; stops at the $50 ledger cap
  python scripts/run_answers.py --report         # tables from the cache -> data/eval/scores/answers.md
  python scripts/run_answers.py --v2 [--one | --run | --report]   # gold v2 (D-034, D-035): M3, M4, M7, M8, M8n
                                                  # from their top 5, and the agents M9s / M9; cache data/eval/answers_v2/
  python scripts/run_answers.py --v2 --dev-one     # one M9 agent answer on a dev question (smoke test, not cached)

Cache: data/eval/answers/run<N>/<method>/<qid>.json. Within one run, methods that retrieved exactly the same
top 5 share one answer and one judgement (same prompt; the second copy is marked `shared_from` and costs $0).
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from cookbook import answer as A  # noqa: E402
from cookbook import retrieve as R  # noqa: E402
from cookbook import spend  # noqa: E402
from cookbook.db import get_db  # noqa: E402
from cookbook.load import DATA, in_effect, load_articles, load_gold, load_gold_v2  # noqa: E402
from run_eval import frozen_ok  # noqa: E402

METHODS = list(R.METHODS)
RUNS = 3
OUT = DATA / "eval" / "answers"
EST_TOKENS = {"answer": (1000, 700), "judge": (600, 400)}  # (input, output) per call, thinking included


def path(run: int, method: str, qid: str) -> Path:
    return OUT / f"run{run}" / method / f"{qid}.json"


def cached(run: int, method: str, qid: str) -> dict:
    p = path(run, method, qid)
    return json.loads(p.read_text()) if p.exists() else {}


def save(run: int, method: str, qid: str, row: dict) -> None:
    p = path(run, method, qid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(row, indent=1, ensure_ascii=False) + "\n")


def per_question_estimate() -> float:
    a, j = EST_TOKENS["answer"], EST_TOKENS["judge"]
    return spend.cost(A.MODEL, *a) + spend.cost(A.JUDGE_MODEL, *j)


def judge(client, q: dict, answer: str, state: dict):
    """Judge with Fable 5.2; if the org can't use it (400), switch to Opus 5.5 for the rest and say so."""
    import anthropic
    model = state.get("judge_model", A.JUDGE_MODEL)
    try:
        return A.call(client, A.JUDGE_SYSTEM, A.judge_prompt(q, answer), A.JUDGE_SCHEMA, effort="low",
                      model=model, script="judge", estimate=spend.cost(model, *EST_TOKENS["judge"]) * 2)
    except anthropic.BadRequestError as e:
        if model == A.MODEL:
            raise
        print(f"judge model {model} refused ({str(e)[:120]}); using {A.MODEL} as judge from now on")
        state["judge_model"] = A.MODEL
        return judge(client, q, answer, state)


def method_scores(rows: list[tuple[dict, dict]], arts: dict) -> dict:
    ans = [(q, r) for q, r in rows if q["answerable"] == "yes"]
    unans = [(q, r) for q, r in rows if q["answerable"] in {"no", "partial"}]
    return {
        "facts": mean(sum(f["present"] for f in r["judge"]["facts"]) / max(1, len(r["judge"]["facts"])) for _, r in ans) if ans else None,
        "all_facts": mean(all(f["present"] for f in r["judge"]["facts"]) for _, r in ans) if ans else None,
        "cites_stale": mean(any(k in arts and not in_effect(arts[k], q["as_of"]) for k in r["cited_keys"]) for q, r in rows),
        "cites_trap": mean(bool(set(r["cited_keys"]) & set(q["trap_keys"])) for q, r in rows),
        "declines": mean(r["judge"]["declines_uncovered"] for _, r in unans) if unans else None,
        "gap": mean(r["not_covered"] for _, r in ans) if ans else None,
        "n_ans": len(ans), "n_unans": len(unans),
    }


def report(gold: list[dict], arts: dict) -> str:
    keys = ["facts", "all_facts", "gap", "cites_stale", "cites_trap", "declines"]
    L = ["Mean over the runs, with the lowest and highest run in brackets. facts and all facts: the 27 answerable "
         "questions. cites stale / cites trap: share of answers citing an outdated version or a trap article (lower is better). "
         "says not covered: answerable questions where the answer said the help center doesn't cover (part of) it, "
         "usually because retrieval missed an article (lower is better). "
         "declines: the 3 questions the help center doesn't fully cover.", "",
         "| method | runs | facts found | all facts | says not covered | cites stale | cites trap | declines when not covered |",
         "|---|---|---|---|---|---|---|---|"]
    judges = set()
    for m in METHODS:
        per_run = []
        for run in range(1, RUNS + 1):
            rows = [(q, cached(run, m, q["id"])) for q in gold]
            if all(r.get("judge") for _, r in rows):
                per_run.append(method_scores(rows, arts))
                judges |= {r["judge_meta"]["model"] for _, r in rows}
        if not per_run:
            continue

        def cell(k):
            xs = [s[k] for s in per_run if s[k] is not None]
            return f"{mean(xs):.2f} [{min(xs):.2f}–{max(xs):.2f}]" if len(xs) > 1 else f"{xs[0]:.2f}"
        L.append(f"| {m} {R.METHODS[m][0]} | {len(per_run)} | " + " | ".join(cell(k) for k in keys) + " |")
    L += ["", f"Answers: {A.MODEL} (effort medium), top {A.CONTEXT_K} articles, text only. Judge: {', '.join(sorted(judges))} (effort low).",
          "", "Spend (ledger, from 2026-11-18):", "```", spend.summary(), "```"]
    return "\n".join(L)


def spotcheck(gold: list[dict], n: int = 5) -> str:
    rng = random.Random(18)
    picks = rng.sample([(m, q) for m in METHODS for q in gold if cached(1, m, q["id"]).get("judge")], n)
    L = ["# Judge spot-check (5 random judgements from run 1)", "",
         "For each: does the judge's verdict match what the answer says? Mark agree / disagree.", ""]
    for m, q in picks:
        r = cached(1, m, q["id"])
        L += [f"## {q['id']} · {m} · {q['type']}", f"**Question:** {q['question']}", "",
              f"**Answer:** {r['answer']}", "", "**Judge:**"]
        L += [f"- {'✅' if f['present'] else '❌'} {f['fact']}" for f in r["judge"]["facts"]]
        L += [f"- declines uncovered parts: {r['judge']['declines_uncovered']}", "", "Your call: agree / disagree", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--one", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--v2", action="store_true")
    ap.add_argument("--dev-one", action="store_true")
    args = ap.parse_args()
    if args.v2:
        import answers_v2
        return answers_v2.main(args)
    ok, why = frozen_ok()
    if not ok:
        print("refusing to run on the gold set:", why)
        return 1
    gold = load_gold()
    arts = {a["_key"]: a for a in load_articles()}
    if args.report:
        md = report(gold, arts)
        print(md)
        (DATA / "eval" / "scores" / "answers.md").write_text(f"# Answer eval\n\n{md}\n")
        if all(cached(1, m, q["id"]).get("judge") for m in METHODS for q in gold):
            (DATA / "eval" / "scores" / "judge_spotcheck.md").write_text(spotcheck(gold))
        return 0

    db = get_db()
    retrieved = {(m, q["id"]): [r["key"] for r in R.retrieve(db, m, q, k=A.CONTEXT_K)] for m in METHODS for q in gold}
    todo = [(run, m, q) for run in range(1, RUNS + 1) for m in METHODS for q in gold if not cached(run, m, q["id"]).get("judge")]
    distinct = {(run, q["id"], tuple(retrieved[(m, q["id"])])) for run, m, q in todo}
    est = len(distinct) * per_question_estimate()
    print(f"{len(todo)} answers to fill ({len(METHODS)} methods x {len(gold)} questions x {RUNS} runs, minus cached); "
          f"{len(distinct)} distinct prompts to pay for")
    print(f"estimated ${est:.2f} · ledger ${spend.total():.2f} of ${spend.CAP:.2f} · answers {A.MODEL}, judge {A.JUDGE_MODEL}")
    if not (args.one or args.run):
        m, q = METHODS[0], gold[0]
        print(f"\nexample ({m}, {q['id']}):\n--- system ---\n{A.ANSWER_SYSTEM}\n--- user ---\n"
              f"{A.answer_prompt(q, [arts[k] for k in retrieved[(m, q['id'])]])}")
        print("\ndry run only; --one or --run to call the API")
        return 0

    import anthropic
    from collections import defaultdict
    from concurrent.futures import ThreadPoolExecutor, as_completed
    client = anthropic.Anthropic()
    state = {}
    groups = defaultdict(list)  # one paid answer per (run, question, retrieved top 5)
    for run, m, q in (todo[:1] if args.one else todo):
        groups[(run, q["id"], tuple(retrieved[(m, q["id"])]))].append((run, m, q))
    done_before = {}  # identical prompts already answered in an earlier session of this run
    for run in range(1, RUNS + 1):
        for m in METHODS:
            for q in gold:
                r = cached(run, m, q["id"])
                if r.get("judge") and not r.get("shared_from"):
                    done_before[(run, q["id"], tuple(r["retrieved"]))] = (m, r)

    def work(sig, members):
        run, qid, keys = sig
        q = members[0][2]
        if sig in done_before:
            src_m, row = done_before[sig]
        else:
            body, meta = A.call(client, A.ANSWER_SYSTEM, A.answer_prompt(q, [arts[k] for k in keys]), A.ANSWER_SCHEMA,
                                effort="medium", script="answers", estimate=spend.cost(A.MODEL, *EST_TOKENS["answer"]) * 2)
            jbody, jmeta = judge(client, q, body["answer"], state)
            src_m = members[0][1]
            row = {"qid": qid, "method": src_m, "run": run, "retrieved": list(keys),
                   "prompt_sha1": hashlib.sha1(A.answer_prompt(q, [arts[k] for k in keys]).encode()).hexdigest()[:12],
                   **body, "answer_meta": meta, "judge": jbody, "judge_meta": jmeta,
                   "cost": round(meta["cost"] + jmeta["cost"], 5)}
        for _run, m, _q in members:
            save(run, m, qid, row if m == src_m else {**row, "method": m, "shared_from": src_m, "cost": 0.0})
        return sig, row, len(members)

    n_done = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(work, sig, mem) for sig, mem in groups.items()]
        for f in as_completed(futures):
            try:
                sig, row, k = f.result()
            except A.OverBudget as e:
                print("skipped (over budget):", e)
                continue
            n_done += 1
            found = sum(x["present"] for x in row["judge"]["facts"])
            if args.one or n_done % 20 == 0 or n_done == len(groups):
                print(f"[{n_done}/{len(groups)}] run{sig[0]} {sig[1]} ({k} methods): facts {found}/{len(row['judge']['facts'])} "
                      f"· ledger ${spend.total():.2f}", flush=True)
            if args.one:
                print(json.dumps({"answer": row["answer"], "judge": row["judge"], "judge_model": row["judge_meta"]["model"]}, indent=1))
    print("\n" + spend.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
