"""Freeze a gold set: write the sha256 of its file (D-006, D-024, D-031).

  python scripts/freeze_gold.py         # data/eval/gold.json    -> data/eval/FROZEN     (make freeze)
  python scripts/freeze_gold.py --v2    # data/eval/gold_v2.json -> data/eval/FROZEN_v2  (make freeze-v2)

After this, the eval refuses to run if the file changes.
"""
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1] / "data" / "eval"
src, out = ("gold_v2.json", "FROZEN_v2") if "--v2" in sys.argv else ("gold.json", "FROZEN")
gold = json.loads((EVAL / src).read_text())["questions"]
if any(q["status"] == "draft" for q in gold):
    sys.exit("some questions are still status 'draft'; mark them reviewed first")
if (EVAL / out).exists() and "--force" not in sys.argv:
    sys.exit(f"{out} already exists: a frozen set is not re-frozen (use --force only with Tianyi's OK)")
sha = hashlib.sha256((EVAL / src).read_bytes()).hexdigest()
(EVAL / out).write_text(json.dumps({"file": src, "sha256": sha, "frozen_on": date.today().isoformat(), "questions": len(gold),
                                    "per_type": dict(Counter(q["type"] for q in gold))}, indent=1) + "\n")
print(f"frozen {src}: {len(gold)} questions, sha256 {sha}")
