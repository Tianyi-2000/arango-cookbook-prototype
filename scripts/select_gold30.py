"""One-off (2026-11-17, D-024): cut the 56-question gold set to 30, chosen from the questions alone.

No retrieval method existed when this ran, so the choice can't be fitted to any method's results.
Mix: multi_hop 7, checklist 5, temporal 5, conditional 4, exact 3, semantic 3, unanswerable 3.
All 16 seeds Tianyi kept are in; 14 drafts are added (reasons below). The other 26 move to
data/eval/gold_reserve.json unchanged (debugging uses those, never the frozen 30).
"""
import json
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1] / "data" / "eval"

WHY = {  # draft id: why it is in the 30
    "q04": "A bare form code: tests the exact-match `codes` field (I-002). The payoff-letter article is a look-alike trap.",
    "q16": "Shares almost no words with its article ('stuff in the car's computer' = personal data, paired phones): the purest paraphrase test.",
    "q21": "Needs three articles (home pickup, getting paid, e-payoff network); only the first looks like the question. The lender name is the bridge.",
    "q22": "A state article (duplicate title in North Carolina) plus the offer-validity article; the price answer is only in the second.",
    "q23": "Starts on the buying side and ends on the selling side, with a trap that looks closer (Northwind-financed titles).",
    "q24": "Inheritance + loan + e-payoff network; the lender name is the only path to the third article.",
    "q44": "Four articles across titles, a state's duplicate-title process and plates: the list is spread out.",
    "q47": "Negative equity, payoff letter, e-payoff network and the appointment checklist: four articles from one lender name.",
    "q48": "Insurance, plates and toll tags: three articles that look unrelated, plus a state rule.",
    "q28": "About December 2025, so the 2022 version is right; a method that filters on 'today' instead of as_of fails on purpose (D-019).",
    "q29": "The answer is a lender's joining date in the e-payoff network, checked against the appointment date.",
    "q31": "The friend's 2023 mailed check matches the old version: the 'agent repeats an outdated answer' case this cookbook is about.",
    "q36": "The 2022 version says pickup works in every state; the current one excludes Texas.",
    "q52": "The Northwind-financing article looks like the place to answer from, but the KB never gives rates: should refuse.",
}
NOT_PICKED = {"q20": "near-duplicate of seed q18 (lease equity with a different lessor)"}


def main() -> None:
    src = json.loads((EVAL / "gold.json").read_text())
    if len(src["questions"]) != 56:
        raise SystemExit(f"expected the 56-question set, found {len(src['questions'])}; already split?")
    keep, reserve = [], []
    for q in src["questions"]:
        if q["status"] == "kept":
            keep.append(q)
        elif q["id"] in WHY:
            keep.append({**q, "why_in_30": WHY[q["id"]]})
        else:
            reserve.append({**q, **({"why_not_in_30": NOT_PICKED[q["id"]]} if q["id"] in NOT_PICKED else {})})
    head = {k: v for k, v in src.items() if k != "questions"}
    gold = {**head, "note": head.get("note", "") + " Cut to 30 on 2026-11-17 (D-024); the rest are in gold_reserve.json.", "questions": keep}
    res = {**head, "note": "Questions not in the frozen 30 (D-024). Use these, not the gold set, to debug retrieval code.", "questions": reserve}
    (EVAL / "gold.json").write_text(json.dumps(gold, indent=1, ensure_ascii=False) + "\n")
    (EVAL / "gold_reserve.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(f"gold.json: {len(keep)} questions · gold_reserve.json: {len(reserve)} questions")


if __name__ == "__main__":
    main()
