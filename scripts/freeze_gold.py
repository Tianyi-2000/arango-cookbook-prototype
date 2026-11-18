"""Freeze the gold set: write data/eval/FROZEN with the sha256 of data/eval/gold.json (D-006, D-024).

After this, `make eval` refuses to run if gold.json changes. Run: python scripts/freeze_gold.py (make freeze).
"""
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1] / "data" / "eval"
gold = json.loads((EVAL / "gold.json").read_text())["questions"]
if any(q["status"] == "draft" for q in gold):
    sys.exit("some questions are still status 'draft'; mark them reviewed first")
sha = hashlib.sha256((EVAL / "gold.json").read_bytes()).hexdigest()
(EVAL / "FROZEN").write_text(json.dumps({"sha256": sha, "frozen_on": date.today().isoformat(), "questions": len(gold),
                                         "per_type": dict(Counter(q["type"] for q in gold))}, indent=1) + "\n")
print(f"frozen: {len(gold)} questions, sha256 {sha}")
