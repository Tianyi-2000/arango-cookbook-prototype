"""One-off (2026-11-17, D-023): replace the five fictional states and their store cities with real ones.

The rules, policies, companies and numbers stay synthetic. Only the place names change.
Kept in the repo as a record of exactly what was replaced. Running it twice is a no-op.

Rules, applied to raw file text in this order (so JSON formatting is untouched):
  1. `an Aldora` / `an Eastvale` -> `a Virginia` / `a California` (grammar)
  2. `duplicate_title_<old>` -> `duplicate_title_<new_key>` (doc ids, keys, links, cites)
  3. `"<old>"` as a whole JSON string (state keys) -> `"<new_key>"`
  4. `<Old>` as a word in prose -> the real name (`North Carolina`)
  5. `<old>` lower-case in prose (messy customer messages) -> lower-case real name (`north carolina`)
`data/kb/stores.json` is rewritten from the table below: five real cities per state, approximate
city-centre coordinates, same hours and services by position.
`data/tickets/archive/` is evidence of an earlier batch and keeps the old names.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STATES = {  # old key: (new key, real name)
    "aldora": ("virginia", "Virginia"),
    "brevin": ("north_carolina", "North Carolina"),
    "corlan": ("georgia", "Georgia"),
    "dunmore": ("texas", "Texas"),
    "eastvale": ("california", "California"),
}

CITIES = {  # new state key: five (city, [lon, lat]) in store order 01..05
    "virginia": [("Richmond", [-77.4360, 37.5407]), ("Virginia Beach", [-75.9780, 36.8529]),
                 ("Arlington", [-77.1068, 38.8816]), ("Roanoke", [-79.9414, 37.2710]),
                 ("Charlottesville", [-78.4767, 38.0293])],
    "north_carolina": [("Charlotte", [-80.8431, 35.2271]), ("Raleigh", [-78.6382, 35.7796]),
                       ("Greensboro", [-79.7920, 36.0726]), ("Durham", [-78.8986, 35.9940]),
                       ("Wilmington", [-77.9447, 34.2257])],
    "georgia": [("Atlanta", [-84.3880, 33.7490]), ("Savannah", [-81.0998, 32.0809]),
                ("Augusta", [-81.9748, 33.4735]), ("Macon", [-83.6324, 32.8407]),
                ("Athens", [-83.3576, 33.9519])],
    "texas": [("Houston", [-95.3698, 29.7604]), ("Dallas", [-96.7970, 32.7767]),
              ("Austin", [-97.7431, 30.2672]), ("San Antonio", [-98.4936, 29.4241]),
              ("El Paso", [-106.4850, 31.7619])],
    "california": [("Los Angeles", [-118.2437, 34.0522]), ("San Diego", [-117.1611, 32.7157]),
                   ("San Jose", [-121.8863, 37.3382]), ("Sacramento", [-121.4944, 38.5816]),
                   ("Fresno", [-119.7871, 36.7378])],
}

TEXT_FILES = (
    sorted((ROOT / "data" / "kb").rglob("*.json"))
    + [ROOT / "data" / "tickets" / "tickets.json", ROOT / "data" / "tickets" / "plan.json"]
    + sorted((ROOT / "data" / "tickets" / "raw").glob("*.json"))
    + [ROOT / "data" / "eval" / "gold.json", ROOT / "data" / "eval" / "candidates.json",
       ROOT / "data" / "eval" / "seed_candidates.md", ROOT / "docs" / "KB_OUTLINE.md",
       ROOT / "docs" / "SPEC.md", ROOT / "scripts" / "check_data.py"]
)
OLD_RE = re.compile("|".join(STATES), re.I)


def rename_text(s: str) -> str:
    for old, (key, name) in STATES.items():
        cap = old.capitalize()
        s = re.sub(rf"\b([Aa])n {cap}\b", lambda m: f"{m.group(1)} {name}", s)
        s = s.replace(f"duplicate_title_{old}", f"duplicate_title_{key}")
        s = s.replace(f'"{old}"', f'"{key}"')
        s = re.sub(rf"\b{cap}\b", name, s)
        s = re.sub(rf"\b{old}\b", name.lower(), s)
    return s


def rewrite_stores() -> None:
    path = ROOT / "data" / "kb" / "stores.json"
    stores = json.loads(path.read_text())
    for s in stores:
        old_state, pos = s["_key"].rsplit("_", 1)
        if old_state not in STATES:  # already renamed
            continue
        key = STATES[old_state][0]
        city, coords = CITIES[key][int(pos) - 1]
        s.update({"_key": f"{key}_{pos}", "name": f"Northwind {city}", "city": city, "state": key})
        s["location"]["coordinates"] = coords
    path.write_text(json.dumps(stores, indent=1, ensure_ascii=False) + "\n")


def main() -> int:
    rewrite_stores()
    changed = 0
    for path in TEXT_FILES:
        if not path.exists():
            continue
        before = path.read_text(encoding="utf-8")
        after = rename_text(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
    print(f"rewrote stores.json; renamed places in {changed} files")

    # Every file outside the archive must be free of the old names, and every JSON file must still parse.
    left = []
    for path in list((ROOT / "data").rglob("*")) + list((ROOT / "docs").rglob("*")) + \
            list((ROOT / "scripts").glob("*.py")) + list((ROOT / "cookbook").glob("*.py")):
        if path.is_dir() or "archive" in path.parts or path.suffix not in {".json", ".md", ".py"}:
            continue
        if path.name == "rename_places.py" or path.name == "gold_review.md":  # this file; review is re-rendered
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            json.loads(text)
        for m in OLD_RE.finditer(text):
            left.append(f"{path.relative_to(ROOT)}: {text[max(0, m.start() - 30):m.end() + 30]!r}")
    if left:
        print("old names still present:", *left[:20], sep="\n  ")
        return 1
    print("check: no old place names left outside data/tickets/archive/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
