"""One spend ledger for every API call made from 2026-11-18 on (D-029): data/eval/spend.json.

Every script records each call's real `usage` here and checks the total before the next call, so the
$50 cap holds across scripts and reruns. Prices are $ per million tokens; thinking tokens are output.
"""
import json
import os
import threading
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
CACHE_READ = {"claude-opus-5-5": 0.05, "claude-fable-5-2": 0.025}  # cache reads, as a share of the input price
CACHE_WRITE = 1.25                                                   # 5-minute cache writes, same
_LOCK = threading.RLock()  # answers run in threads: reads and writes of the ledger take turns
WORST = (8.00, 40.00)  # unknown model (e.g. a fallback): count it at the highest price


def price(model: str) -> tuple[float, float]:
    return next((p for m, p in PRICES.items() if model.startswith(m)), WORST)


def cost(model: str, input_tokens: int, output_tokens: int, cache_write: int = 0, cache_read: int = 0) -> float:
    """input_tokens are the uncached ones; cached prompt tokens are priced separately (prompt caching)."""
    pi, po = price(model)
    read = next((r for m, r in CACHE_READ.items() if model.startswith(m)), 0.1)
    return (input_tokens + cache_write * CACHE_WRITE + cache_read * read) / 1e6 * pi + output_tokens / 1e6 * po


def _rows() -> list[dict]:
    return json.loads(LEDGER.read_text())["calls"] if LEDGER.exists() else []


def total() -> float:
    with _LOCK:
        return round(sum(r["cost"] for r in _rows()), 4)


def can_spend(estimate: float) -> bool:
    return total() + estimate <= CAP


def record(script: str, model: str, input_tokens: int, output_tokens: int, note: str = "",
           cache_write: int = 0, cache_read: int = 0) -> float:
    with _LOCK:
        return _record(script, model, input_tokens, output_tokens, note, cache_write, cache_read)


def _record(script, model, input_tokens, output_tokens, note, cache_write=0, cache_read=0) -> float:
    c = round(cost(model, input_tokens, output_tokens, cache_write, cache_read), 6)
    row = {"at": datetime.now().isoformat(timespec="seconds"), "script": script, "model": model,
           "input": input_tokens, "output": output_tokens, "cost": c, "note": note}
    if cache_write or cache_read:
        row.update({"cache_write": cache_write, "cache_read": cache_read})
    rows = _rows() + [row]
    tmp = LEDGER.with_suffix(".tmp")
    tmp.write_text(json.dumps({"cap": CAP, "note": "API spend from 2026-11-18 on (D-029); tickets before that cost $3.10 (D-021)",
                                  "total": round(sum(r["cost"] for r in rows), 4), "calls": rows}, indent=1) + "\n")
    os.replace(tmp, LEDGER)  # atomic: a reader never sees half a file
    return c


def summary() -> str:
    by = {}
    for r in _rows():
        k = (r["script"], r["model"])
        n, c = by.get(k, (0, 0.0))
        by[k] = (n + 1, c + r["cost"])
    lines = [f"  {s:22} {m:18} {n:4} calls  ${c:6.2f}" for (s, m), (n, c) in sorted(by.items())]
    return "\n".join(lines + [f"  total ${total():.2f} of ${CAP:.2f}"])
