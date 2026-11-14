"""Generate ~200 past support tickets (2022-03 to 2026-10) from the knowledge base.

Python decides every fact about a ticket: date, topic, which article version the agent used,
state, channel, customer style, whether it's outdated today, and whether the agent made a mistake
(used a superseded version). Claude only writes the conversation text from that one article version,
so the text can't drift from the plan (D-010).

    python scripts/generate_tickets.py            # dry run: plan + cost estimate + one example prompt (no API calls)
    python scripts/generate_tickets.py --one      # generate the first missing ticket (needs `ant auth login` or an API key)
    python scripts/generate_tickets.py --all      # generate every missing ticket, then assemble tickets.json

Each generated ticket is cached in data/tickets/raw/<key>.json, so reruns never pay twice.
"""
import argparse
import json
import os
import random
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.load import DATA, LINK_RE, REWRITE_DATE, TODAY, in_effect, load_kb, version_on  # noqa: E402

N_TICKETS = 200
SEED = 2026
FIRST_DAY, LAST_DAY = date(2022, 3, 1), date(2026, 10, 31)
N_AGENT_ERRORS = 8  # 4% of 200, picked from the tickets where a mistake is possible
CHANNELS = [("chat", 0.5), ("email", 0.3), ("phone_note", 0.2)]
STYLES = ["brief", "rambling", "typos", "polite", "frustrated"]
MODEL = "claude-opus-5-5"
# Opus 5.5 list prices (USD per million tokens), for the estimate only.
PRICE_IN, PRICE_OUT = 4.00, 20.00
EST_OUTPUT_TOKENS = 600  # conversation text plus low-effort thinking; a deliberately high guess

OUT_DIR = DATA / "tickets"
RAW_DIR = OUT_DIR / "raw"

SYSTEM = """You write realistic, short support conversations for a fictional used-car retailer, Northwind Auto, \
to be used as test data. Everything about the company is fictional.

Rules:
- Return JSON with two fields: "customer" (the customer's message) and "agent" (the support reply).
- The customer writes in their own everyday words, 1 to 4 sentences, in the requested style. Don't copy the article's phrasing.
- The agent answers in 2 to 4 sentences using ONLY facts stated in the article provided. Don't add policies, numbers, \
forms or steps that aren't in it. The agent may name the article's title.
- Channel "phone_note": the agent field is the agent's short note after a call, in the third person ("Customer asked..."), \
and the customer field is a one-line summary of what the caller said.
- Don't mention AI, test data or that the company is fictional."""


def plan_tickets(kb: dict) -> list[dict]:
    """Decide every ticket's facts with a seeded RNG, so the plan is the same on every run."""
    rng = random.Random(SEED)
    arts = kb["articles"]
    states = [s["_key"] for s in kb["states"]]
    doc_ids = sorted({a["doc_id"] for a in arts})
    weight = {d: (0.3 if next(a for a in arts if a["doc_id"] == d)["side"] == "buy" else 1.0) for d in doc_ids}
    span = (LAST_DAY - FIRST_DAY).days
    tickets = []
    while len(tickets) < N_TICKETS:
        day = (FIRST_DAY + timedelta(days=rng.randrange(span + 1))).isoformat()
        doc_id = rng.choices(doc_ids, weights=[weight[d] for d in doc_ids])[0]
        current = version_on(arts, doc_id, day)
        if current is None:  # the article didn't exist on that day (new in 2026, or retired)
            continue
        cited = current
        tickets.append({
            "_key": f"t{len(tickets) + 1:03d}",
            "created_at": day,
            "channel": rng.choices([c for c, _ in CHANNELS], weights=[w for _, w in CHANNELS])[0],
            "style": rng.choice(STYLES),
            "state": rng.choice(cited["states"] or states),
            "topic": doc_id,
            "cites": [cited["_key"]],
            "agent_error": False,
            "outdated": not in_effect(cited, TODAY),
        })
    # Agent mistakes: after the rewrite, on a rewritten article, the agent answers from the superseded
    # 2022 version. Only those tickets can have this mistake, so pick exactly N_AGENT_ERRORS of them.
    by_key = {a["_key"]: a for a in arts}
    eligible = [t for t in tickets if t["created_at"] >= REWRITE_DATE and by_key[t["cites"][0]]["kind"] == "rewritten"]
    for t in rng.sample(eligible, min(N_AGENT_ERRORS, len(eligible))):
        t["cites"] = [f"{t['topic']}__2022"]
        t["agent_error"] = True
        t["outdated"] = True
    return tickets


def build_prompt(t: dict, article: dict) -> str:
    return (f"Ticket date: {t['created_at']}\nChannel: {t['channel']}\nCustomer style: {t['style']}\n"
            f"Customer's state: {t['state'].title()}\n\n"
            f"Article the agent used:\nTitle: {article['title']}\n{LINK_RE.sub(r'\\1', article['text'])}\n\n"
            "Write the conversation as JSON.")


SCHEMA = {
    "type": "object",
    "properties": {"customer": {"type": "string"}, "agent": {"type": "string"}},
    "required": ["customer", "agent"],
    "additionalProperties": False,
}


def generate_one(client, t: dict, article: dict) -> dict:
    """One API call. Server-side fallbacks are on: if the model declines, the API retries on a fallback model."""
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(t, article)}],
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"{t['_key']}: stop_reason={response.stop_reason}, request {response._request_id}")
    text = next(b.text for b in response.content if b.type == "text")
    body = json.loads(text)
    return {"customer": body["customer"].strip(), "agent": body["agent"].strip(),
            "model": response.model, "request_id": response._request_id,
            "usage": {"input": response.usage.input_tokens, "output": response.usage.output_tokens}}


def assemble(plan: list[dict]) -> int:
    """Join the plan with every cached conversation into data/tickets/tickets.json (only complete tickets)."""
    rows = []
    for t in plan:
        raw = RAW_DIR / f"{t['_key']}.json"
        if raw.exists():
            body = json.loads(raw.read_text())
            rows.append({**t, "customer": body["customer"], "agent": body["agent"]})
    (OUT_DIR / "tickets.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--one", action="store_true", help="generate the first missing ticket")
    mode.add_argument("--all", action="store_true", help="generate every missing ticket")
    args = parser.parse_args()

    kb = load_kb()
    by_key = {a["_key"]: a for a in kb["articles"]}
    plan = plan_tickets(kb)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "plan.json").write_text(json.dumps(plan, indent=1) + "\n")

    years = Counter(t["created_at"][:4] for t in plan)
    print(f"plan: {len(plan)} tickets -> data/tickets/plan.json")
    print(f"  by year: {dict(sorted(years.items()))}")
    print(f"  outdated today: {sum(t['outdated'] for t in plan)} · agent errors: {sum(t['agent_error'] for t in plan)}")
    print(f"  channels: {dict(Counter(t['channel'] for t in plan))}")
    print(f"  most common topics: {Counter(t['topic'] for t in plan).most_common(5)}")

    prompts = [SYSTEM + build_prompt(t, by_key[t["cites"][0]]) for t in plan]
    est_in = sum(len(p) for p in prompts) / 4  # ~4 characters per token
    est_out = EST_OUTPUT_TOKENS * len(plan)
    cost = est_in / 1e6 * PRICE_IN + est_out / 1e6 * PRICE_OUT
    print(f"  estimate for all {len(plan)}: ~{est_in / 1000:.0f}k input + ~{est_out / 1000:.0f}k output tokens ≈ ${cost:.2f} ({MODEL})")

    missing = [t for t in plan if not (RAW_DIR / f"{t['_key']}.json").exists()]
    print(f"  cached: {len(plan) - len(missing)} · missing: {len(missing)}")

    if not (args.one or args.all):
        print("\n--- example prompt (first ticket) ---\n" + build_prompt(plan[0], by_key[plan[0]["cites"][0]]))
        print("\nDry run only. Use --one to generate one ticket, --all for the rest.")
        return 0
    if os.getenv("ANTHROPIC_API_KEY") == "":
        print("ANTHROPIC_API_KEY is set but empty, which would hide your `ant auth login` sign-in. Remove it from .env.")
        return 1

    import anthropic
    # No key check here: the SDK finds credentials itself, from ANTHROPIC_API_KEY or from an
    # `ant auth login` sign-in on this machine (issue I-014).
    client = anthropic.Anthropic()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    todo = missing[:1] if args.one else missing
    for i, t in enumerate(todo, 1):
        try:
            body = generate_one(client, t, by_key[t["cites"][0]])
        except anthropic.AuthenticationError as e:
            print(f"Not signed in: run `ant auth login` (or set ANTHROPIC_API_KEY in .env). Details: {e}")
            return 1
        except TypeError as e:  # the SDK raises this when it finds no credentials at all
            print(f"No credentials found: run `ant auth login`. Details: {e}")
            return 1
        (RAW_DIR / f"{t['_key']}.json").write_text(json.dumps(body, indent=1, ensure_ascii=False) + "\n")
        print(f"[{i}/{len(todo)}] {t['_key']} {t['created_at']} {t['topic']}: {body['usage']}")
        if args.one:
            print(f"  customer: {body['customer']}\n  agent:    {body['agent']}")
    print(f"assembled {assemble(plan)} tickets -> data/tickets/tickets.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
