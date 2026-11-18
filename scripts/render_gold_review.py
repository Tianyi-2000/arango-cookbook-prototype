"""Render the 30-question gold set as a readable review sheet: data/eval/gold30_review.md.

Drafts come first, grouped by type, each with why it was picked and a "Your call" line; then the kept
seeds; then the reserve. Run: python scripts/render_gold_review.py   (or: make review)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.load import DATA, TODAY, load_articles, load_gold, load_reserve  # noqa: E402

TYPES = ["exact", "semantic", "multi_hop", "temporal", "conditional", "checklist", "unanswerable"]


def titles(keys, arts):
    return "; ".join(f"{arts[k]['title']} `[{k.split('__')[1]}]`" for k in keys) or "—"


def block(q, arts, with_call=True):
    when = []
    if q["asked_on"] != TODAY:
        when.append(f"asked on {q['asked_on']}")
    if q["as_of"] != q["asked_on"]:
        when.append(f"rules as of {q['as_of']}")
    meta = " · ".join(when + ([f"state: {q['state']}"] if q["state"] else []) + ([f"tricky: {', '.join(q['tricky'])}"] if q["tricky"] else []))
    lines = [f"### {q['id']} · {q['type']}" + (f" · seed {q['seed']}" if q.get("seed") else "") + (f" · vague case {q['vague_case']}" if q.get("vague_case") else ""),
             f"**\"{q['question']}\"**"]
    if meta:
        lines.append(f"- {meta}")
    lines += [f"- Perfect answer: {q['perfect_answer']}",
              f"- Must-include: {' · '.join(f'`{f}`' for f in q['answer_facts']) or '(says it is not covered)'}",
              f"- Gold articles ({'all needed' if q['require_all'] else 'any one is enough'}): {titles(q['gold_keys'], arts)}",
              f"- Traps: {titles(q['trap_keys'], arts)}",
              f"- What makes it hard: {q['what_makes_it_hard']}"]
    if with_call:
        lines.append("- Your call: keep / edit / drop")
    return "\n".join(lines)


def main() -> None:
    arts = {a["_key"]: a for a in load_articles()}
    gold = load_gold()
    reserve = load_reserve()
    drafts = [q for q in gold if q["status"] == "draft"]
    seeds = [q for q in gold if q["status"] == "kept"]
    mix = " · ".join(f"{t} {sum(q['type'] == t for q in gold)}" for t in TYPES)
    out = ["# Gold set review: the 30 questions to freeze",
           "",
           f"**{len(gold)} questions** ({mix}). **{len(drafts)} drafts to review** (below, by type), then {len(seeds)} seeds you kept on 2026-11-13, "
           f"then the {len(reserve)} questions in reserve.",
           f"Generated from `data/eval/gold.json` and `gold_reserve.json` by `scripts/render_gold_review.py` (`make review`); edit the JSON, not this file. "
           f"\"Today\" is {TODAY}; a tag like `[2026]` is the article version.",
           "",
           "> [!todo] Your review (about 25 minutes)",
           "> For each draft: would a real customer send it? Is the perfect answer right? Are the gold articles the ones you would want retrieved?",
           "> Reply in shorthand, e.g. `q21 keep`, `q29 edit: ...`, `q48 drop, swap in q46`. Anything you don't mention counts as keep.",
           "> The 30 were chosen from the questions alone: no retrieval method existed yet (D-024). After your review the set is frozen (commit + sha256).",
           "> State names were changed to real ones today (D-023); the seeds differ from what you kept only in those names.",
           ""]
    for t in TYPES:
        qs = [q for q in drafts if q["type"] == t]
        if qs:
            out += [f"## {t} ({len(qs)} to review)", ""]
            for q in qs:
                b = block(q, arts).replace("- Your call:", f"- Why it's in the 30: {q.get('why_in_30', '—')}\n- Your call:")
                out.append(b + "\n")
    out += ["---", "", f"## Seeds already kept ({len(seeds)}), for reference", ""] + [block(q, arts, with_call=False) + "\n" for q in seeds]
    out += ["---", "", f"## Reserve ({len(reserve)}): not in the 30, used for debugging. Swap any of these in if you prefer it.", "",
            "| id | type | question | note |", "|---|---|---|---|"]
    out += [f"| {q['id']} | {q['type']} | {q['question']} | {q.get('why_not_in_30', '')} |" for q in reserve]
    out += ["", "Messy variants, off-topic messages and vague questions (35 drafts in `data/eval/candidates.json`) are not part of this freeze; they come later."]
    path = DATA / "eval" / "gold30_review.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(DATA.parent)}: {len(drafts)} drafts to review, {len(seeds)} seeds, {len(reserve)} in reserve")


if __name__ == "__main__":
    main()
