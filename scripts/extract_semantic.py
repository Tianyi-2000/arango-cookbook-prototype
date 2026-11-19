"""Extract concepts and relations from each article version with Claude (the semantic graph layer, D-030).

  python scripts/extract_semantic.py            # dry run: one prompt and the cost estimate, no API calls
  python scripts/extract_semantic.py --one      # extract one article version, to check the output
  python scripts/extract_semantic.py --run      # every version not cached yet

One call per article version, structured output. Cached in data/kb/semantic/<key>.json and committed,
so a rerun never pays twice. Every call is recorded in the spend ledger (D-029).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cookbook import answer as A  # noqa: E402
from cookbook import spend  # noqa: E402
from cookbook.load import load_articles  # noqa: E402
from cookbook.semantic import KINDS, REL_TYPES, SEM_DIR  # noqa: E402

MODEL = "claude-opus-5-5"
EFFORT = "medium"
EST_OUT = 1500  # output tokens per call, thinking included (estimate)

SYSTEM = """You extract a small knowledge graph from one help-center article of a used-car retailer. Return the concepts a support agent would use to connect this article to related ones, and the relations between those concepts.
Rules:
- A concept is a short, generic, lowercase, singular noun phrase of 1 to 4 words, named the way a support agent would name it, for example "payoff letter", "lienholder", "power of attorney", "death certificate", "photo id", "lease buyout".
- Use the article's own wording when it names something. Only include concepts the article actually mentions.
- Leave out company and lender names, form codes (NW-...), state names, amounts and dates: they are handled elsewhere.
- kind: situation (a customer's circumstance), document (something to bring, sign or receive), party (a person or organisation role), requirement (a rule or condition), action (something someone must do), service (something the retailer offers).
- Each relation links two of your concepts by their exact names: requires (a situation or action needs a document or action), issued_by (a document comes from a party), applies_when (a rule applies in a situation), alternative_to (either one works), part_of.
- Aim for 5 to 15 concepts and only the relations the article states."""

SCHEMA = {
    "type": "object",
    "properties": {
        "concepts": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "kind": {"type": "string", "enum": KINDS}},
            "required": ["name", "kind"], "additionalProperties": False}},
        "relations": {"type": "array", "items": {"type": "object", "properties": {
            "source": {"type": "string"}, "target": {"type": "string"}, "type": {"type": "string", "enum": REL_TYPES}},
            "required": ["source", "target", "type"], "additionalProperties": False}},
    },
    "required": ["concepts", "relations"],
    "additionalProperties": False,
}


def prompt(a: dict) -> str:
    return f"Article: {a['title']}\n\n{A.plain(a['text'])}"


def per_call_estimate(a: dict) -> float:
    return spend.cost(MODEL, (len(SYSTEM) + len(prompt(a))) // 4, EST_OUT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--one", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    SEM_DIR.mkdir(parents=True, exist_ok=True)
    todo = [a for a in load_articles() if not (SEM_DIR / f"{a['_key']}.json").exists()]
    est = sum(per_call_estimate(a) for a in todo)
    print(f"{len(todo)} article versions to extract · estimated ${est:.2f} · ledger ${spend.total():.2f} of ${spend.CAP:.2f}")
    if not (args.one or args.run):
        if todo:
            print(f"\n--- system ---\n{SYSTEM}\n--- user ({todo[0]['_key']}) ---\n{prompt(todo[0])}")
        print("\ndry run only; --one or --run to call the API")
        return 0
    import anthropic
    client = anthropic.Anthropic()
    for i, a in enumerate(todo[:1] if args.one else todo, 1):
        body, meta = A.call(client, SYSTEM, prompt(a), SCHEMA, effort=EFFORT, model=MODEL,
                            script="extract_semantic", estimate=2 * per_call_estimate(a))
        out = {"key": a["_key"], "model": meta["model"], "request_id": meta["request_id"], "usage": meta["usage"], **body}
        (SEM_DIR / f"{a['_key']}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
        print(f"[{i}/{len(todo)}] {a['_key']}: {len(body['concepts'])} concepts, {len(body['relations'])} relations, "
              f"${meta['cost']:.3f} (ledger ${spend.total():.2f})")
        if args.one:
            print(json.dumps(body, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
