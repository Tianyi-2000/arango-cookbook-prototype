"""M9 / M9s (D-034): Claude answers with tools instead of a fixed top 5. A manual tool-use loop, so every tool call,
its AQL and its result can be cached, printed and counted.

Opus 5.5, effort medium, at most MAX_CALLS tool calls; the final answer uses the same JSON schema as the RAG
answers (answer, cited_keys, not_covered, items). The conversation is prompt-cached (top-level cache_control),
so each turn pays full price only for what is new. Every call goes through the $50 ledger.
"""
import json

from cookbook import answer as A
from cookbook import spend
from cookbook.tools import execute

MAX_CALLS = 8
AGENT_SYSTEM = """You answer questions for Northwind Auto, a used-car retailer, from its help center and its records, using the tools. Questions come from customers or from support staff.
- Look things up before you answer, and use only facts from tool results. Do not guess or use outside knowledge.
- Answer in 2 to 4 plain sentences; a list question may need more.
- If the tools don't answer the question, or part of it, say that the help center doesn't cover that part and suggest contacting a store. Set not_covered to true when any part isn't covered.
- cited_keys: the keys of the articles your answer relies on (records are not articles).
""" + A.ITEMS_RULE + f"\n- You can make at most {MAX_CALLS} tool calls."


def run_agent(client, db, q: dict, tools: list[dict], script: str = "agent", estimate: float = 0.05) -> tuple[dict, dict]:
    """Answer gold question `q` with `tools`. Returns (body, meta); meta has the tool trace, usage and cost."""
    messages = [{"role": "user", "content": f"{A.header_v2(q)}\n\nQuestion from {A.ASKER[q['asker']]}: {q['question']}"}]
    trace, cost, calls, turns = [], 0.0, 0, 0
    usage = {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    while True:
        if not spend.can_spend(estimate):
            raise A.OverBudget(f"ledger at ${spend.total():.2f}")
        response = client.beta.messages.create(
            model=A.MODEL, max_tokens=8000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": A.ANSWER_SCHEMA_V2}},
            system=AGENT_SYSTEM, tools=tools, messages=messages, cache_control={"type": "ephemeral"},
        )
        turns += 1
        cost += A.record_usage(script, response)
        u = response.usage
        for k, v in [("input", u.input_tokens), ("output", u.output_tokens),
                     ("cache_write", getattr(u, "cache_creation_input_tokens", 0) or 0),
                     ("cache_read", getattr(u, "cache_read_input_tokens", 0) or 0)]:
            usage[k] += v
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for b in (b for b in response.content if b.type == "tool_use"):
                calls += 1
                if calls > MAX_CALLS:
                    out, err = f"Tool limit of {MAX_CALLS} calls reached: answer now with what you have.", True
                else:
                    out, err = execute(db, b.name, b.input, q)
                trace.append({"tool": b.name, "input": b.input, "error": err, "result_chars": len(out),
                              "result_head": out[:300]})
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out, **({"is_error": True} if err else {})})
            messages.append({"role": "user", "content": results})
            continue
        if response.stop_reason != "end_turn":
            raise RuntimeError(f"stop_reason={response.stop_reason}, request {response._request_id}")
        body = json.loads(next(b.text for b in response.content if b.type == "text"))
        meta = {"model": response.model, "request_id": response._request_id, "turns": turns, "tool_calls": calls,
                "trace": trace, "usage": usage, "cost": round(cost, 5)}
        return body, meta
