"""One spend ledger for every API call made from 2026-11-18 on (D-029): data/eval/spend.json.

Every script records each call's real `usage` here and checks the total before the next call, so the
$50 cap holds across scripts and reruns. Prices are $ per million tokens; thinking tokens are output.
"""
import json
from datetime import datetime

from cookbook.load import DATA

LEDGER = DATA / "eval" / "spend.json"
CAP = 50.00
PRICES = {  # (input, output) $ per million tokens
    "claude-opus-5-5": (4.00, 20.00),
    "claude-fable-5-2": (8.00, 40.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
WORST = (8.00, 40.00)  # unknown model (e.g. a fallback): count it at the highest price


def price(model: str) -> tuple[float, float]:
    return next((p for m, p in PRICES.items() if model.startswith(m)), WORST)


def cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pi, po = price(model)
    return input_tokens / 1e6 * pi + output_tokens / 1e6 * po


def _rows() -> list[dict]:
    return json.loads(LEDGER.read_text())["calls"] if LEDGER.exists() else []


def total() -> float:
    return round(sum(r["cost"] for r in _rows()), 4)


def can_spend(estimate: float) -> bool:
    return total() + estimate <= CAP


def record(script: str, model: str, input_tokens: int, output_tokens: int, note: str = "") -> float:
    c = round(cost(model, input_tokens, output_tokens), 6)
    rows = _rows() + [{"at": datetime.now().isoformat(timespec="seconds"), "script": script, "model": model,
                       "input": input_tokens, "output": output_tokens, "cost": c, "note": note}]
    LEDGER.write_text(json.dumps({"cap": CAP, "note": "API spend from 2026-11-18 on (D-029); tickets before that cost $3.10 (D-021)",
                                  "total": round(sum(r["cost"] for r in rows), 4), "calls": rows}, indent=1) + "\n")
    return c


def summary() -> str:
    by = {}
    for r in _rows():
        k = (r["script"], r["model"])
        n, c = by.get(k, (0, 0.0))
        by[k] = (n + 1, c + r["cost"])
    lines = [f"  {s:22} {m:18} {n:4} calls  ${c:6.2f}" for (s, m), (n, c) in sorted(by.items())]
    return "\n".join(lines + [f"  total ${total():.2f} of ${CAP:.2f}"])
