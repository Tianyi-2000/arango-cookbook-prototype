"""Test the tests: inject one fault at a time into a copy of data/ and confirm check_data.py catches it.

Run: python scripts/test_check_data.py   (or: make test-checks). Exit code 0 = every fault was caught.
The real data/ is never modified; each fault goes into a fresh temporary copy.
"""
import json, shutil, sys, tempfile, io, contextlib
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R)); sys.path.insert(0, str(R / "scripts"))
import cookbook.load as L
import check_data

def art_file(tmp, key):
    for p in (tmp / "kb" / "articles").glob("*.json"):
        rows = json.loads(p.read_text())
        for r in rows:
            if r["_key"] == key:
                return p, rows, r
def mut_link(tmp):
    p, rows, r = art_file(tmp, "selling_with_loan__2022"); r["text"] += " See [e-payoff](kb:epayoff_network)."; p.write_text(json.dumps(rows))
def mut_code(tmp):
    p, rows, r = art_file(tmp, "appointment_checklist__2026"); r["text"] = r["text"].replace("form NW-ODO-2, which replaced", "the form, which replaced"); p.write_text(json.dumps(rows))
def mut_known(tmp):
    f = tmp / "kb" / "known_issues.json"; k = json.loads(f.read_text()); k[2]["target"] = "nope"; f.write_text(json.dumps(k))
def mut_lender(tmp):
    p, rows, r = art_file(tmp, "epayoff_network__2026"); r["text"] = r["text"].replace("Granite Bank", "A bank"); p.write_text(json.dumps(rows))
def mut_dates(tmp):
    p, rows, r = art_file(tmp, "offer_validity__2026"); r["effective_from"] = "2026-01-15"; p.write_text(json.dumps(rows))
def mut_ticket_number(tmp):
    f = tmp / "tickets" / "tickets.json"; t = json.loads(f.read_text()); t[0]["agent"] += " There is also a $999 fee."; f.write_text(json.dumps(t))
def mut_ticket_flag(tmp):
    f = tmp / "tickets" / "tickets.json"; t = json.loads(f.read_text()); t[0]["agent_error"] = not t[0]["agent_error"]; f.write_text(json.dumps(t))
missed = 0
for name, mut in [("anachronistic link", mut_link), ("retired form without replacement", mut_code), ("known issue missing", mut_known), ("network lender missing from text", mut_lender), ("overlapping versions", mut_dates), ("ticket agent invents a number", mut_ticket_number), ("ticket agent_error flag flipped", mut_ticket_flag)]:
    tmp = Path(tempfile.mkdtemp()) / "data"; shutil.copytree(R / "data", tmp)
    mut(tmp); L.KB, L.DATA = tmp / "kb", tmp; check_data.failures.clear()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = check_data.main()
    fails = [l.strip() for l in out.getvalue().splitlines() if l.startswith("FAIL")]
    missed += code != 1
    print(f"{'CAUGHT' if code == 1 else 'MISSED'}  {name:34} -> {[f for f in fails if not f.startswith('FAILED')]}")
sys.exit(1 if missed else 0)
