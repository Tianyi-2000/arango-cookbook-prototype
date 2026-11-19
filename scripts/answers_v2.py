"""Answer eval on gold v2 (D-034, D-035), called by `run_answers.py --v2`.

RAG methods (M3, M4, M7, M8, M8n) answer from their top 5, as in v1. The agents answer with tools: M9s with search
only, M9 with search + read_article + lookup + list_records. Opus 5.5 answers, Fable 5.2 judges each required fact,
3 runs. List questions also get item precision and recall, computed in code from the answer's `items`.
Cache: data/eval/answers_v2/run<N>/<method>/<qid>.json (RAG methods with the same top 5 share one answer).
"""
import hashlib
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean

from cookbook import agent as AG
from cookbook import answer as A
from cookbook import retrieve as R
from cookbook import spend
from cookbook.db import get_db
from cookbook.entities import item_key
from cookbook.load import DATA, load_articles, load_gold_v2
from cookbook.tools import GRAPH_TOOLS, SEARCH_ONLY
from run_answers import EST_TOKENS, judge, per_question_estimate
from run_eval import frozen_ok

RAG = ["M3", "M4", "M7", "M8", "M8n"]
AGENTS = {"M9s": SEARCH_ONLY, "M9": GRAPH_TOOLS}
LABELS = {**{m: R.METHODS[m][0] for m in RAG}, "M9s": "Agent: search only", "M9": "Agent: search + graph tools"}
RUNS = 3
OUT = DATA / "eval" / "answers_v2"
AGENT_EST = 0.08  # $ per agent answer before the first measurement; replaced by the measured mean once some exist


def path(run, m, qid):
    return OUT / f"run{run}" / m / f"{qid}.json"


def cached(run, m, qid) -> dict:
    p = path(run, m, qid)
    return json.loads(p.read_text()) if p.exists() else {}


def save(run, m, qid, row):
    p = path(run, m, qid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(row, indent=1, ensure_ascii=False) + "\n")


def item_scores(q: dict, items: list[str]) -> dict:
    """Precision and recall of a list answer (D-035). An item maps to a key with the M7 name dictionary (a form
    item maps to the first code it contains); an item that maps to nothing counts as a wrong item."""
    keys = [item_key(q["item_kind"], s) for s in items]
    pred, wrong = {k for k in keys if k}, sum(k is None for k in keys)
    gold = set(q["answer_items"])
    tp, n = len(pred & gold), len(pred) + wrong
    return {"item_recall": tp / len(gold), "item_precision": tp / n if n else 0.0, "item_exact": float(pred == gold and not wrong)}


def agent_estimate() -> float:
    costs = [r["agent_meta"]["cost"] for run in range(1, RUNS + 1) for m in AGENTS
             for p in (OUT / f"run{run}" / m).glob("*.json") if (r := json.loads(p.read_text())).get("agent_meta")]
    return mean(costs) if costs else AGENT_EST


def scores(rows: list[tuple[dict, dict]]) -> dict:
    out = {"facts": mean(sum(f["present"] for f in r["judge"]["facts"]) / len(r["judge"]["facts"]) for _, r in rows),
           "all_facts": mean(all(f["present"] for f in r["judge"]["facts"]) for _, r in rows),
           "gap": mean(r["not_covered"] for _, r in rows)}
    chain = [(q, r) for q, r in rows if q["type"] == "chain"]
    struct = [(q, r) for q, r in rows if q["type"] == "structural"]
    out["facts_chain"] = mean(sum(f["present"] for f in r["judge"]["facts"]) / len(r["judge"]["facts"]) for _, r in chain)
    for k in ["item_recall", "item_precision", "item_exact"]:
        out[k] = mean(item_scores(q, r["items"])[k] for q, r in struct)
    trapq = [(q, r) for q, r in rows if q["trap_keys"]]
    out["cites_trap"] = mean(bool(set(r["cited_keys"]) & set(q["trap_keys"])) for q, r in trapq)
    out["cost"] = mean(r.get("cost_own", r["cost"]) for _, r in rows)
    agent_rows = [r for _, r in rows if r.get("agent_meta")]
    out["tool_calls"] = mean(r["agent_meta"]["tool_calls"] for r in agent_rows) if agent_rows else None
    return out


def report(gold: list[dict]) -> str:
    keys = [("facts", "facts found (20)"), ("all_facts", "all facts (20)"), ("facts_chain", "facts, chain (12)"),
            ("item_recall", "list items found (8)"), ("item_precision", "list items correct (8)"), ("item_exact", "exact list (8)"),
            ("cites_trap", "cites the KB-conflict article ↓ (2)"), ("gap", "says not covered ↓"), ("tool_calls", "tool calls"),
            ("cost", "$ per answer")]
    L = ["Mean over the runs, [lowest–highest run]. Facts: judged by Fable 5.2 by meaning. List items: from the answer's "
         "`items`, mapped to keys in code (D-035). KB-conflict article: v2c06/v2c07, where a current article still names "
         "a retired form. $ per answer: answer + judge, the cost of a shared RAG answer counted once per method.", "",
         "| method | runs | " + " | ".join(h for _, h in keys) + " |", "|---|---|" + "---|" * len(keys)]
    for m in RAG + list(AGENTS):
        per_run = []
        for run in range(1, RUNS + 1):
            rows = [(q, cached(run, m, q["id"])) for q in gold]
            if all(r.get("judge") for _, r in rows):
                per_run.append(scores(rows))
        if not per_run:
            continue

        def cell(k):
            xs = [s[k] for s in per_run if s[k] is not None]
            if not xs:
                return "–"
            fmt = (lambda v: f"{v:.3f}") if k == "cost" else (lambda v: f"{v:.1f}") if k == "tool_calls" else (lambda v: f"{v:.2f}")
            return f"{fmt(mean(xs))} [{fmt(min(xs))}–{fmt(max(xs))}]" if len(xs) > 1 else fmt(xs[0])
        L.append(f"| {m} {LABELS[m]} | {len(per_run)} | " + " | ".join(cell(k) for k, _ in keys) + " |")
    L += ["", f"Answers: {A.MODEL} (effort medium). RAG: top {A.CONTEXT_K} articles, text only. Agents: at most {AG.MAX_CALLS} tool calls, "
          "fixed AQL templates (`cookbook/tools.py`). Judge: Fable 5.2 (effort low).", "", "Spend (ledger, from 2026-11-18):", "```", spend.summary(), "```"]
    return "\n".join(L)


def per_question(gold: list[dict]) -> str:
    L = ["# Gold v2 answers, per question (run 1)", "", "facts found / required; list questions also show items found / expected (wrong items).", "",
         "| question | " + " | ".join(RAG + list(AGENTS)) + " |", "|---|" + "---|" * (len(RAG) + len(AGENTS))]
    for q in gold:
        cells = []
        for m in RAG + list(AGENTS):
            r = cached(1, m, q["id"])
            if not r.get("judge"):
                cells.append("–")
                continue
            c = f"{sum(f['present'] for f in r['judge']['facts'])}/{len(r['judge']['facts'])}"
            if q["type"] == "structural":
                s = item_scores(q, r["items"])
                found = round(s["item_recall"] * len(q["answer_items"]))
                extra = (len(r["items"]) - found) if r["items"] else 0
                c += f" · {found}/{len(q['answer_items'])}" + (f" ({extra})" if extra > 0 else "")
            if set(r["cited_keys"]) & set(q["trap_keys"]):
                c += " · trap"
            cells.append(c)
        L.append(f"| {q['id']} {q['type']} | " + " | ".join(cells) + " |")
    return "\n".join(L)


def spotcheck(gold: list[dict], n: int = 5) -> str:
    import random
    rng = random.Random(18)
    picks = rng.sample([(m, q) for m in RAG + list(AGENTS) for q in gold
                        if cached(1, m, q["id"]).get("judge") and not cached(1, m, q["id"]).get("shared_from")], n)
    L = ["# Judge spot-check, gold v2 (5 random judgements from run 1)", "",
         "For each: does the judge's verdict match what the answer says? Mark agree / disagree.", ""]
    for m, q in picks:
        r = cached(1, m, q["id"])
        L += [f"## {q['id']} · {m} · {q['type']}", f"**Question:** {q['question']}", "", f"**Answer:** {r['answer']}", ""]
        if q["type"] == "structural":
            L += [f"**Items:** {r['items']} → {item_scores(q, r['items'])}", ""]
        L += ["**Judge:**"] + [f"- {'✅' if f['present'] else '❌'} {f['fact']}" for f in r["judge"]["facts"]]
        L += ["", "Your call: agree / disagree", ""]
    return "\n".join(L)


def main(args) -> int:
    if args.dev_one:
        return dev_one()
    ok, why = frozen_ok(v2=True)
    if not ok:
        print("refusing to run on gold v2:", why)
        return 1
    gold = load_gold_v2()
    if args.report:
        md = report(gold)
        print(md)
        (DATA / "eval" / "scores" / "v2_answers.md").write_text(f"# Answer eval, gold v2\n\n{md}\n")
        (DATA / "eval" / "scores" / "v2_answers_per_question.md").write_text(per_question(gold) + "\n")
        (DATA / "eval" / "scores" / "v2_judge_spotcheck.md").write_text(spotcheck(gold) + "\n")
        return 0

    arts = {a["_key"]: a for a in load_articles()}
    db = get_db()
    retrieved = {(m, q["id"]): [r["key"] for r in R.retrieve(db, m, q, k=A.CONTEXT_K)] for m in RAG for q in gold}
    todo = [(run, m, q) for run in range(1, RUNS + 1) for m in RAG + list(AGENTS) for q in gold
            if not cached(run, m, q["id"]).get("judge")]
    rag_sigs = {(run, q["id"], tuple(retrieved[(m, q["id"])])) for run, m, q in todo if m in RAG}
    n_agent = sum(m in AGENTS for _, m, _ in todo)
    est = len(rag_sigs) * per_question_estimate() + n_agent * (agent_estimate() + spend.cost(A.JUDGE_MODEL, *EST_TOKENS["judge"]))
    print(f"{len(todo)} answers to fill: {len(rag_sigs)} distinct RAG prompts + {n_agent} agent runs")
    print(f"estimated ${est:.2f} (agent ${agent_estimate():.3f} per answer) · ledger ${spend.total():.2f} of ${spend.CAP:.2f}")
    if not (args.one or args.run):
        q = gold[0]
        print(f"\nexample RAG prompt (M8, {q['id']}):\n--- system ---\n{A.ANSWER_SYSTEM_V2}\n--- user ---\n"
              f"{A.answer_prompt_v2(q, [arts[k] for k in retrieved[('M8', q['id'])]])}")
        print(f"\nagent system prompt:\n{AG.AGENT_SYSTEM}\n\ndry run only; --one or --run to call the API")
        return 0

    import anthropic
    client = anthropic.Anthropic()
    state = {}
    groups = defaultdict(list)
    for run, m, q in todo:
        sig = (run, q["id"], m) if m in AGENTS else (run, q["id"], tuple(retrieved[(m, q["id"])]))
        groups[sig].append((run, m, q))
    if args.one:  # one RAG and one agent answer for the first question that needs both
        keep = [s for s in groups if s[2] == "M9"][:1] + [s for s in groups if s[2] not in AGENTS][:1]
        groups = {s: groups[s] for s in keep}

    def work(sig, members):
        run, qid = sig[0], sig[1]
        q = members[0][2]
        src_m = members[0][1]
        if src_m in AGENTS:
            body, ameta = AG.run_agent(client, get_db(), q, AGENTS[src_m],  # one connection per thread
                                       script=f"agent_{src_m}",
                                       estimate=agent_estimate() * 3)
            meta, extra = {"model": ameta["model"], "request_id": ameta["request_id"], "usage": ameta["usage"], "cost": ameta["cost"]}, {"agent_meta": ameta}
            keys = []
        else:
            keys = list(sig[2])
            prompt = A.answer_prompt_v2(q, [arts[k] for k in keys])
            body, meta = A.call(client, A.ANSWER_SYSTEM_V2, prompt, A.ANSWER_SCHEMA_V2, effort="medium", script="answers_v2",
                                estimate=spend.cost(A.MODEL, *EST_TOKENS["answer"]) * 2)
            extra = {"prompt_sha1": hashlib.sha1(prompt.encode()).hexdigest()[:12]}
        jbody, jmeta = judge(client, q, body["answer"], state)
        row = {"qid": qid, "method": src_m, "run": run, "retrieved": keys, **body, "answer_meta": meta, **extra,
               "judge": jbody, "judge_meta": jmeta, "cost": round(meta["cost"] + jmeta["cost"], 5)}
        for _run, m, _q in members:
            save(run, m, qid, row if m == src_m else {**row, "method": m, "shared_from": src_m, "cost_own": 0.0})
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
                print(f"[{n_done}/{len(groups)}] run{sig[0]} {sig[1]} {row['method']}: facts {found}/{len(row['judge']['facts'])} "
                      f"· ${row['cost']:.3f} · ledger ${spend.total():.2f}", flush=True)
            if args.one:
                print(json.dumps({k: row[k] for k in ["answer", "items", "cited_keys", "not_covered", "judge"]}, indent=1, ensure_ascii=False))
                if row.get("agent_meta"):
                    print("tools:", [(t["tool"], t["input"]) for t in row["agent_meta"]["trace"]], "turns", row["agent_meta"]["turns"],
                          "usage", row["agent_meta"]["usage"])
    print("\n" + spend.summary())
    return 0


def dev_one() -> int:
    """Smoke test on a dev question (never cached with gold): one M9 answer, with its tool trace and cost."""
    import anthropic
    q = next(x for x in load_gold_v2(dev=True) if x["id"] == "v2d07")
    body, meta = AG.run_agent(anthropic.Anthropic(), get_db(), q, GRAPH_TOOLS, script="agent_dev", estimate=0.3)
    print(json.dumps(body, indent=1, ensure_ascii=False))
    for t in meta["trace"]:
        print("tool", t["tool"], t["input"], "error" if t["error"] else "", t["result_chars"], "chars")
    print("turns", meta["turns"], "usage", meta["usage"], f"cost ${meta['cost']:.4f}", "items", item_scores(q, body["items"]))
    return 0
