# Progress log

A detailed log, newest first. Add an entry after every working session or run: **Did** (what was done), **Changed** (files or data), **Why**, **Stuck / waiting**. Any automatic adjustment the agent makes gets its own line. High-level status is in [stage.md](stage.md).

---

## 2026-11-18 · Semantic layer, M5/M6, first retrieval eval on the frozen 30
- **Did:** spend ledger with a $50 cap (D-029). Wrote the expected concepts for 10 versions and committed them before extracting (60867bf). Extracted concepts and relations for all 68 versions with Opus 5.5: $0.85. `make check-semantic`: recall 0.88, agreement 0.72; misses are mostly synonyms. Loaded the layer (365 concepts, 689 mentions, 453 relates). M4–M6 now share one query with the edge set as a bind variable (D-030). A snapshot of M1–M4 on the reserve caught a non-deterministic tie order (I-021), fixed with a key tie-break. Rules committed (284abe1) before `make eval` ran on the gold set.
- **Result (frozen 30, 27 answerable):** Recall@5 M1 0.63 · M2 0.77 · M3 0.80 · M4 0.80 · M5 0.80 · M6 0.80. Recall@10: 0.75 / 0.84 / 0.88 / 0.88 / 0.88 / 0.88. **stale@5: M1 0.78, M2 0.78, M3–M6 0.00.** Multi-hop Recall@5: M3 0.83, M4 0.90, M5 0.83, M6 0.90. Per question, M3 → M4: q22 gained `offer_validity__2026` through `duplicate_title_north_carolina__2022` (a structural link); q42 lost `leased_car__2022`, pushed out by four neighbours of a strong first hit (`home_pickup__2026`), each inheriting 0.8 × its score. M5 changed no question's Recall@5.
- **Reading:** on this KB the big, clean win is filtering by date and state inside the vector query (stale hits 78% → 0%). Graph expansion as defined in D-025 is about neutral at K=5 (one win, one loss); the semantic layer adds nothing measurable. Nothing was tuned after the run; ideas for a better expansion are for a later version with new questions.
- **Stuck / waiting:** nothing; next is the answer eval (D-029).

---

## 2026-11-18 · Gold set frozen
- **Did:** Tianyi reviewed the 14 drafts and kept all of them. Marked them `kept` (`reviewed_by: tianyi 2026-11-18`), `make check` passes, `make test-checks` 8/8, `make freeze` wrote `data/eval/FROZEN` (30 questions, sha256 5935c443…). Stage 2 done.
- **Also decided today:** API budget raised to $50 (D-029): answers for every method, Fable 5.2 as an independent judge, an LLM-extracted semantic graph with methods M5/M6, three answer runs. M5/M6 rules are written before the first gold eval.

---

## 2026-11-17 · Loaded into ArangoDB; M1–M4; freshness demo; eval and answer code ready
- **Did:** (1) `make load` (`cookbook/build.py`) rebuilds `northwind_kb` from data/ in about 25 s: 7 document and 8 edge collections, `kb_graph`, `kb_view` (BM25; `codes` exact), a vector index (MiniLM, nLists 4, probe all). A graph query finds exactly the 2 current articles that still cite a retired form (KI-1, KI-2). (2) `verify_env.py` check 5: a document inserted after the vector index was built is found by the next query; `COSINE_SIMILARITY` exists. (3) `cookbook/retrieve.py`: M1–M4, one AQL each (D-025). Two bugs, found on the reserve questions: a 1e-8 score tie credited the graph (I-019), and two FILTER statements break vector search once a state is set (I-020). `make test-retrieve` guards both. (4) `cookbook/metrics.py` (6 hand-computed cases pass), `scripts/run_eval.py` (refuses unless gold.json matches FROZEN; D-018 comparison), `make freeze`. Reserve run, for debugging only: stale@5 is 0.90 (M1) and 0.95 (M2), 0.00 for M3/M4; M4 = M3 on the reserve (only 1 multi-hop question there). Nothing was tuned. (5) `make fresh` (D-027): the policy change is one 8 ms transaction; right after it, M3/M4 return the new version and M2 still ranks the 2022 version first. The first demo question didn't reach the article with any vector method, so it was reworded once (logged in D-027). (6) `cookbook/answer.py` + `scripts/run_answers.py` (D-028), dry run by default, $6 cap.
- **Auto-adjustments:** answer spend cap lowered from the plan's $8 to $6, so tickets ($3.10) + answers stay under $10.
- **Stuck / waiting:** Tianyi's review of `data/eval/gold30_review.md` → `make freeze` → `make eval` → README results → `make answers-run`.

---

## 2026-11-17 · Real place names; gold set cut to 30 (architecture v3.0 confirmed)
- **Did:** Tianyi approved today's plan, which is design v3.0: real state names, a 30-question gold set, a four-step retrieval ladder (BM25 → vector → vector + filter → + graph), a live freshness demo, then Opus 5.5 answers under an $8 cap. (1) `scripts/rename_places.py` replaced the five fictional states with Virginia, North Carolina, Georgia, Texas and California, and the 25 store cities with real ones (approximate coordinates). It edits raw file text with five ordered rules (key strings, `duplicate_title_*` ids, prose by case, "an Eastvale" → "a California"), then fails if any old name is left outside `data/tickets/archive/`. One row in `docs/KB_OUTLINE.md` used an abbreviated form (`` `_brevin` ``) that the rules missed; fixed by hand. Disclaimers added to `README.md` and `data/kb/README.md` (D-023). (2) `scripts/select_gold30.py` kept the 16 seeds and added 14 drafts, each with a written reason (D-024). The other 26 are in `data/eval/gold_reserve.json`. `make review` now writes `data/eval/gold30_review.md`; the old `gold_review.md` was removed.
- **Changed:** 159 data/doc files from the rename; `cookbook/load.py` (+`load_reserve`); `scripts/check_data.py` (`GOLD_MIX` replaces 8 per type; reserve and candidates are checked against gold + reserve); `scripts/render_gold_review.py`.
- **Result:** `make check` passes, `make test-checks` 8 of 8 caught. Cost $0: nothing was regenerated.
- **Stuck / waiting:** Tianyi reviews the 14 drafts in `data/eval/gold30_review.md`, then the freeze. Meanwhile: loading into ArangoDB and the retrieval methods (no gold needed).

---

## 2026-11-14 · Candidates drafted: messy wording, off-topic, vague
- **Did:** drafted 35 candidates in `data/eval/candidates.json`: 18 human-style variants of existing questions (typos in key terms like "odomoter" and "notorized", run-ons, no punctuation, abbreviations, a mangled code "nw lrl 1"; covering all 7 types), 9 off-topic messages (gibberish, small talk, a greeting, a half-typed line, a prompt-injection attempt, one borderline car question), and 8 vague questions (3 missing the term, 3 ambiguous, 2 wrong term). Kept out of `gold.json` until Tianyi decides how to model them. `make check` validates them; `make test-checks` has an 8th fault for them. It was MISSED at first: the check read the real file instead of going through the loader (I-018). Fixed; now 8 of 8 are caught. They appear at the end of `gold_review.md`.
- **Stuck / waiting:** Tianyi's review (tomorrow): the 40 drafts plus these 35, and two modeling decisions.

---

## 2026-11-13 · Vague questions documented (D-022)
- **Did:** recorded Tianyi's request to add vague questions before the freeze, in three cases (missing term, ambiguous, wrong term), with scoring rules in `eval.md`. Rule: wrong-term messages are graded on what they say. Clarifying follow-ups ("Did you mean…?") added to stage 5 as a plan, not built. Reminder added to the review sheet.

---

## 2026-11-13 · Reminder added: human-style and off-topic questions
- **Did:** recorded Tianyi's request as stage-2 done criteria before the freeze: (1) rewrite some gold questions the way people really type (typos, grammar errors, run-ons), and (2) add meaningless or off-topic messages that the assistant should skip, not answer. Added a "to add before the freeze" section to `eval.md` with the two ways to model them, and a reminder box at the top of `data/eval/gold_review.md`.
- **Stuck / waiting:** Tianyi's review, which now includes these two items.

---

## 2026-11-13 · First pushed to GitHub (private)
- **Did:** archived the first ticket batch as evidence (`data/tickets/archive/`), added before/after samples to I-015 and I-017, removed a real company name from the seed notes and personal context from two docs, created the private GitHub repo and pushed `main`.
- **Why:** Tianyi asked to push the current progress.

---

## 2026-11-13 · Tickets generated (stage 2)
- **Did:** Tianyi installed `ant` and signed in (`ant auth login`, workspace Default); no key file is stored. Removed the empty `ANTHROPIC_API_KEY=` from `.env` and the key gate from the script (I-014). Tested 1 ticket, then generated 200 (batch 1). A new faithfulness check flagged 3 numbers (2 false alarms, 1 invented date; I-017). A bulk variety measure showed near-duplicate messages (I-015). While fixing that, found the `\1` link bug in the prompts (I-016). Added persona and vehicle hints, prompt rules, a variety check (threshold 50%, set in advance) and collision-free personas; regenerated all 200 (batch 2), then the 4 tickets whose persona changed.
- **Result:** 200 tickets; `make check` passes all 11 checks; `make test-checks` catches 7 of 7 injected faults (2 new ones for tickets). Highest customer-message overlap 39% (was 100%); "you guys" 0 (was 71). Sample: t018 (2026-08) is an agent mistake that still allows personal checks.
- **Cost:** about $3.10 in total (D-021). Actual usage per ticket ≈ 780 input + 230 output tokens.
- **Auto-adjustments:** personas re-drawn for t066, t095, t154, t168 (collision rule); those 4 regenerated.
- **Stuck / waiting:** Tianyi's review of the 40 draft gold questions, then freeze. After that, stage 3.

---

## 2026-11-13 · Vault folders renamed to 01 / 02 / 03
- **Did:** renamed `10 Cookbook Demo` → `01 Cookbook Demo`, `20 Internship (placeholder)` → `02 Internship (placeholder)`, `90 Templates` → `03 Templates` (Tianyi found 10/20/90 confusing). Updated every reference in the vault, the vault's `CLAUDE.md`, the Obsidian templates setting, the pointers in the other notes vault, and memory. Older entries below keep the old names as history. `docker compose down` before and `up` after; recreated `.venv` (I-008 again). `make verify`, `make check` and `make test-checks` all pass at the new path. Created `.env` from `.env.example`, with the key left empty for Tianyi.
- **Why:** Tianyi's preference.
- **Stuck / waiting:** the API key in `.env`; the review of the 40 draft questions.

---

## 2026-11-13 · Stage 2: data, checks, gold set, ticket plan (checkpoint v2.5)
- **Did:** wrote the knowledge base: 51 articles / 68 versions in 8 section files, with `kb:` links and `NW-` codes in the text; `forms` (15), `states` (5), `lenders` (12), `lessors` (6), `stores` (25), `known_issues` (3). Wrote `cookbook/load.py` and `scripts/check_data.py` (`make check`). Mutation-tested the checker with 5 injected faults: the first harness never applied them (I-010); after fixing that, the anachronism check missed one (I-009); after that fix, all 5 are caught (`make test-checks`). Built the gold set: 56 questions, 8 per type (16 kept seeds + 40 drafts), plus `make review` for a readable sheet. Checked every answer fact against its gold articles: 24 are paraphrases or computed values, none contradicts an article, so facts will be graded by meaning (D-020). Wrote `scripts/generate_tickets.py`: a deterministic plan (200 tickets, 75 outdated today, 8 agent mistakes, about $2.68 estimated) and a dry run; the API path is written but not yet run.
- **Changed:** `data/kb/**`, `data/eval/gold.json`, `data/eval/gold_review.md`, `data/tickets/plan.json`, `cookbook/load.py`, `scripts/{check_data,test_check_data,render_gold_review,generate_tickets}.py`, `Makefile` (check, test-checks, review, tickets-plan, tickets-one, tickets). One article edit made the Apex fee unambiguous (it's added to the buyout amount).
- **Auto-adjustments:** store services made explicit (I-013); agent mistakes picked by count (I-011); `kb:` link markup stripped from ticket prompts.
- **Stuck / waiting:** (1) `ANTHROPIC_API_KEY` in `.env` to run `make tickets-one`, then `make tickets`. (2) Tianyi's review of the 40 draft questions in `data/eval/gold_review.md`, then freeze.

---

## 2026-11-13 · Harness and vault (architecture v2.0)
- **Did:** created the Obsidian vault `~/Projects/Arango/` (Home, CLAUDE.md, internship placeholder, templates, Minimal theme). Moved this repo from another notes vault to `10 Cookbook Demo/`. Ran `docker compose down` before the move and `up` after; the volume `arango-cookbook-prototype_arango_data` survived. Recreated `.venv` (I-008). `verify_env.py` passes in the new location. Deleted the v0 kitchen: folder, container `arango-kitchen`, volume `arango-graphrag-kitchen_kitchen_data` (D-016). Wrote the six harness files. Folded `NOTES.md` into `issues.md` and deleted it, to keep one source of truth.
- **Changed:** `stage.md`, `progress.md`, `architecture.md`, `decisions.md`, `issues.md`, `eval.md` (new); `NOTES.md` (removed); `.gitignore` (+ `.obsidian/`); README (links to the harness files).
- **Why:** Tianyi wants these files to be the north star. A new session reads them before searching the code (D-015).
- **Stuck / waiting:** nothing yet; stage 2 data work starts next.

## 2026-11-13 · Seed questions kept
- **Did:** drafted 16 seed-question candidates (two per type plus two tricky ones), each with the perfect answer, must-include facts, what makes it hard, and why it was picked. Tianyi kept all 16. Listed six facts the articles must state so that every kept question has one correct answer.
- **Changed:** `data/eval/seed_candidates.md` (renamed from `seed_questions_tianyi.md`). Commit `5fee546`.
- **Why:** Tianyi was too tired to write them (D-013).

## 2026-11-12 · Medium size, tricky cases (architecture v2.0)
- **Did:** rewrote `docs/KB_OUTLINE.md` at medium size: 51 articles / 68 versions in four kinds (unchanged, rewritten, new, retired), transition rules, 15 forms, 5 states, 12 lenders, 6 lessors, ~200 tickets, 25 stores, KB problems left in on purpose, and the tricky-case list. Rewrote the seed-question template so every field says what to write and why, with a filled example per type. Marked README and SPEC as drafts for Tianyi to rewrite.
- **Changed:** `docs/KB_OUTLINE.md`, `docs/SPEC.md`, `README.md`, the seed template. Commit `637666c`.
- **Why:** Tianyi: the data was too small to play with, and he wanted real edge cases (D-009, D-011).

## 2026-11-12 · Stage 1 done (checkpoint v1.5)
- **Did:** checked three risks in a scratch database before writing data. A filtered vector search uses the index; `text_en` splits form codes; `nLists` 1–4 train on 30 documents. Scaffolded the repo: `docker-compose.yml` (3.12.13, `--vector-index true`, port 8535), pinned `requirements.txt`, `Makefile`, `cookbook/db.py` (connects, and prints every AQL query before running it), `scripts/verify_env.py`. Wrote `docs/SPEC.md` and the first `docs/KB_OUTLINE.md` (22 articles / 30 versions). `git init`, local only.
- **Changed:** new repo `arango-cookbook-prototype`. Commit `e45b17d`.
- **Stuck:** port 8535 was held by the kitchen container, so it was stopped (I-006).

## 2026-11-12 · Redesign as a developer cookbook (architecture v1.0)
- **Did:** discussed the redesign with Tianyi and agreed on: fictional states; a structural graph plus an LLM graph; Tianyi to write one seed question per type; the name "cookbook prototype".
- **Why:** Tianyi: the cookbook is for developers learning ArangoDB, it must be in English, and it needs versions, graph-shaped data, traps, multi-hop questions and an eval (D-003 to D-006).

## 2026-11-12 · Kitchen steps 0–3 (architecture v0.0 → v0.5)
- **Did:** built the kitchen: 12 synthetic articles and step scripts for connect, documents, BM25 and vector, each printing its AQL. Results on three demo questions: keyword, both methods 1/1; paraphrase, BM25 rank 3 and vector rank 1; multi-hop, both 1/3, with the trap `lost_title` ranked 2nd by both.
- **Stuck:** the direction was wrong (a Chinese learning lab, not a developer cookbook), so it was redesigned as v1.0 and later deleted.
