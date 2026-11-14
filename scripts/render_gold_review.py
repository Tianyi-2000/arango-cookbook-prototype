"""Render data/eval/gold.json as a readable review sheet: data/eval/gold_review.md.

Drafts come first, grouped by type, each with a "Your call" line. The 16 kept seeds are listed at the
end for reference. Run: python scripts/render_gold_review.py   (or: make review)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.load import DATA, TODAY, load_articles, load_gold  # noqa: E402

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
    lines = [f"### {q['id']} · {q['type']}" + (f" · seed {q['seed']}" if q["seed"] else ""),
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
    drafts = [q for q in gold if q["status"] == "draft"]
    seeds = [q for q in gold if q["status"] == "kept"]
    out = ["# Gold set review",
           "",
           f"{len(gold)} questions, 8 per type. **{len(drafts)} drafts to review** (below, by type) and {len(seeds)} seeds already kept (at the end).",
           f"Generated from `data/eval/gold.json` by `scripts/render_gold_review.py`; don't edit this file, edit the JSON and re-run. "
           f"\"Today\" is {TODAY}; a version tag like `[2026]` shows which article version is meant.",
           "",
           "For each draft: would a real customer send it? Is the perfect answer right? Do you agree with what makes it hard? "
           "Mark keep / edit / drop. After your review the gold set is frozen.",
           "",
           "> [!todo] Before the freeze: make it sound like real people",
           "> - Rewrite some questions the way people really type: misspellings, broken grammar, run-on sentences, no punctuation, two questions in one.",
           "> - Add a few meaningless or off-topic messages (\"asdf??\", \"whats the weather\", a half-typed line). The right behavior is to skip them: no answer from the KB, just ask to rephrase.",
           "> - Tell Claude in shorthand, e.g. `q12 edit: \"my car dont start no more can u still buy it\"`, or `add off-topic: \"lol ok\"`.",
           ""]
    for t in TYPES:
        qs = [q for q in drafts if q["type"] == t]
        out += [f"## {t} ({len(qs)} drafts)", ""] + [block(q, arts) + "\n" for q in qs]
    out += ["---", "", "## Seeds already kept (2026-11-13), for reference", ""] + [block(q, arts, with_call=False) + "\n" for q in seeds]
    path = DATA / "eval" / "gold_review.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {path.relative_to(DATA.parent)}: {len(drafts)} drafts, {len(seeds)} seeds")


if __name__ == "__main__":
    main()
