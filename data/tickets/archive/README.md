# Archived ticket batches

`batch1_tickets.json`: the first 200 generated tickets (2026-11-13), kept as evidence for issues I-015 and I-017. It was replaced by the current `../tickets.json` and is **not** loaded by anything: `cookbook/load.py` reads only `data/tickets/tickets.json`.

What was wrong with it: near-duplicate customer messages (t182 and t189 identical; 58 pairs shared at least 15% of their word 4-grams; "you guys" in 71 of 200), and one invented date (t076). To reproduce the failures, copy it over `tickets.json` in a scratch copy of `data/` and run `scripts/check_data.py`.
