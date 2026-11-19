"""Score the LLM-extracted concepts against the hand-written list for 10 article versions, and describe the layer.

Run: python scripts/check_semantic.py   (or: make check-semantic)
Recall = share of hand-listed concepts the extraction found. Agreement = share of extracted concepts that are
on the hand list (a lower bound on precision). Match rule and list: data/kb/semantic_gold.json (written first).
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cookbook.load import KB, load_articles  # noqa: E402
from cookbook.semantic import load_semantic, matches, normalize  # noqa: E402

MAX_DF = 10  # D-030: concepts in more than 10 articles are too generic to walk


def main() -> int:
    gold = json.loads((KB / "semantic_gold.json").read_text())["articles"]
    sem = load_semantic()
    rows, R, Ag = [], [], []
    for key, items in gold.items():
        ext = [c["name"] for c in sem[key]["concepts"]]
        found = [any(matches(e, it["names"]) for e in ext) for it in items]
        agree = [any(matches(e, it["names"]) for it in items) for e in ext]
        R.append(sum(found) / len(found))
        Ag.append(sum(agree) / len(agree))
        missed = [it["names"][0] for it, f in zip(items, found) if not f]
        extra = [e for e, a in zip(ext, agree) if not a]
        rows.append(f"| {key} | {sum(found)}/{len(found)} | {sum(agree)}/{len(agree)} | {', '.join(missed) or '—'} | {', '.join(extra) or '—'} |")
    print("| article version | hand-listed found | extracted on the list | missed | extracted, not on the list |")
    print("|---|---|---|---|---|")
    print("\n".join(rows))
    print(f"\nmean recall {sum(R) / len(R):.2f} · mean agreement {sum(Ag) / len(Ag):.2f} (10 versions, 88 hand-listed concepts)")

    doc_of = {a["_key"]: a["doc_id"] for a in load_articles()}
    docs = defaultdict(set)
    for key, body in sem.items():
        for c in body["concepts"]:
            docs[normalize(c["name"])].add(doc_of[key])
    df = Counter({k: len(v) for k, v in docs.items()})
    n_rel = sum(len(b["relations"]) for b in sem.values())
    print(f"\nlayer: {len(sem)} versions · {len(df)} distinct concepts after normalising · {n_rel} relations")
    print(f"concepts shared by 2+ articles (they connect articles): {sum(1 for v in df.values() if v >= 2)}")
    print(f"too generic to walk (in more than {MAX_DF} articles): {[(k, v) for k, v in df.most_common() if v > MAX_DF]}")
    print(f"most shared below the cut: {[(k, v) for k, v in df.most_common() if v <= MAX_DF][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
