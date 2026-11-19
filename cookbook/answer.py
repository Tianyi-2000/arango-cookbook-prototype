"""Grounded answers and an LLM judge (stage 4, D-028). Both are one Claude API call each.

The answer model sees only the top 5 articles a retrieval method returned: key, title and text, no dates
or other metadata (as in a plain RAG pipeline), so the methods are compared on what they retrieve.
The judge checks each required fact by meaning (D-020) and whether unsupported questions were declined.
"""
import json

from cookbook import spend
from cookbook.load import plain  # noqa: F401 (used here and re-exported)

MODEL = "claude-opus-5-5"         # answers (and semantic extraction)
JUDGE_MODEL = "claude-fable-5-2"  # a different, stronger model grades the answers (D-029)
PRICE_IN, PRICE_OUT = spend.PRICES[MODEL]
CONTEXT_K = 5

ANSWER_SYSTEM = """You answer customer questions for Northwind Auto, a used-car retailer, using only the help-center articles provided.
- Answer in 2 to 4 plain sentences.
- Use only facts stated in the articles. Do not guess or use outside knowledge.
- If the articles don't answer the question, or part of it, say that the help center doesn't cover that part and suggest contacting a store. Set not_covered to true when any part isn't covered.
- cited_keys: the keys of the articles your answer relies on."""

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {"answer": {"type": "string"}, "cited_keys": {"type": "array", "items": {"type": "string"}},
                   "not_covered": {"type": "boolean"}},
    "required": ["answer", "cited_keys", "not_covered"],
    "additionalProperties": False,
}

JUDGE_SYSTEM = """You grade a support answer against a checklist. Judge by meaning, not exact wording: "300 more miles" matches "300 additional miles", and a correct computed amount matches. A fact counts as present only if the answer states it (or its exact meaning) and does not contradict it elsewhere."""

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "facts": {"type": "array", "items": {"type": "object", "properties": {
            "fact": {"type": "string"}, "present": {"type": "boolean"}}, "required": ["fact", "present"],
            "additionalProperties": False}},
        "declines_uncovered": {"type": "boolean"},
    },
    "required": ["facts", "declines_uncovered"],
    "additionalProperties": False,
}


def answer_prompt(q: dict, articles: list[dict]) -> str:
    ctx = "\n\n".join(f"[{a['_key']}] {a['title']}\n{plain(a['text'])}" for a in articles)
    state = f" The customer is in {q['state'].replace('_', ' ').title()}." if q.get("state") else ""
    return f"Today is {q['asked_on']}.{state}\n\nArticles:\n\n{ctx}\n\nCustomer question: {q['question']}"


def judge_prompt(q: dict, answer: str) -> str:
    facts = "\n".join(f"- {f}" for f in q["answer_facts"]) or "(none: the help center doesn't cover this question)"
    return (f"Customer question: {q['question']}\n\nRequired facts:\n{facts}\n\n"
            f"Does the answer decline the parts the help center doesn't cover (instead of inventing an answer)? "
            f"Question type: {'fully covered' if q['answerable'] == 'yes' else 'partly or not covered'}. "
            f"For a fully covered question, set declines_uncovered to true unless the answer wrongly says something isn't covered.\n\n"
            f"Answer to grade:\n{answer}")


# --- gold v2 (D-034, D-035): the same rules plus `items` for list questions ------------------------------------
ITEMS_RULE = ("- items: if the question asks for a list, give each item exactly as the sources name it (form code, company "
              "name, state, or article title); otherwise an empty list.")
ANSWER_SYSTEM_V2 = (ANSWER_SYSTEM.replace("customer questions", "questions from customers and support staff")
                    .replace("- Answer in 2 to 4 plain sentences.", "- Answer in 2 to 4 plain sentences; a list question may need more.")
                    + "\n" + ITEMS_RULE)
ANSWER_SCHEMA_V2 = {**ANSWER_SCHEMA,
                    "properties": {**ANSWER_SCHEMA["properties"], "items": {"type": "array", "items": {"type": "string"}}},
                    "required": ANSWER_SCHEMA["required"] + ["items"]}
ASKER = {"customer": "a customer", "support_agent": "a support agent", "kb_maintainer": "the help-center team"}


def header_v2(q: dict) -> str:
    state = f" The customer is in {q['state'].replace('_', ' ').title()}." if q.get("state") else ""
    return f"Today is {q['asked_on']}.{state}"


def answer_prompt_v2(q: dict, articles: list[dict]) -> str:
    ctx = "\n\n".join(f"[{a['_key']}] {a['title']}\n{plain(a['text'])}" for a in articles)
    return f"{header_v2(q)}\n\nArticles:\n\n{ctx}\n\nQuestion from {ASKER[q['asker']]}: {q['question']}"


class OverBudget(RuntimeError):
    """The next call could push the spend ledger over its cap (D-029)."""


def record_usage(script: str, response) -> float:
    u = response.usage
    return spend.record(script, response.model, u.input_tokens, u.output_tokens, note=response._request_id or "",
                        cache_write=getattr(u, "cache_creation_input_tokens", 0) or 0,
                        cache_read=getattr(u, "cache_read_input_tokens", 0) or 0)


def call(client, system: str, prompt: str, schema: dict, effort: str, model: str = MODEL,
         script: str = "answers", estimate: float = 0.05, max_tokens: int = 8000):
    """One structured call with server-side fallbacks (as in scripts/generate_tickets.py).

    Checks the shared ledger before the call and records the real usage after it.
    No `thinking` parameter: Opus 5.5 and Fable 5.2 think adaptively; `effort` sets how much.
    """
    if not spend.can_spend(estimate):
        raise OverBudget(f"ledger at ${spend.total():.2f}; a call of ~${estimate:.2f} could cross ${spend.CAP:.2f}")
    response = client.beta.messages.create(
        model=model,
        max_tokens=max_tokens,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    c = record_usage(script, response)
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason={response.stop_reason}, request {response._request_id}")
    body = json.loads(next(b.text for b in response.content if b.type == "text"))
    meta = {"model": response.model, "request_id": response._request_id,
            "usage": {"input": response.usage.input_tokens, "output": response.usage.output_tokens},
            "cost": round(c, 5)}
    return body, meta
