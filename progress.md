# Progress log

A detailed log, newest first. Add an entry after every working session or run: **Did** (what was done), **Changed** (files or data), **Why**, **Stuck / waiting**. Any automatic adjustment the agent makes gets its own line. High-level status is in [stage.md](stage.md).

---

## 2026-11-13 · Stage 2: data, checks, gold set, ticket plan (checkpoint v2.5)
- **Did:** wrote the knowledge base: 51 articles / 68 versions in 8 section files, with `kb:` links and `NW-` codes in the text; `forms` (15), `states` (5), `lenders` (12), `lessors` (6), `stores` (25), `known_issues` (3). Wrote `cookbook/load.py` and `scripts/check_data.py` (`make check`). Mutation-tested the checker with 5 injected faults: the first harness never applied them (I-010); after fixing that, the anachronism check missed one (I-009); after that fix, all 5 are caught (`make test-checks`). Built the gold set: 56 questions, 8 per type (16 kept seeds + 40 drafts), plus `make review` for a readable sheet. Checked every answer fact against its gold articles: 24 are paraphrases or computed values, none contradicts an article, so facts will be graded by meaning (D-020). Wrote `scripts/generate_tickets.py`: a deterministic plan (200 tickets, 75 outdated today, 8 agent mistakes, about $2.68 estimated) and a dry run; the API path is written but not yet run.
- **Changed:** `data/kb/**`, `data/eval/gold.json`, `data/eval/gold_review.md`, `data/tickets/plan.json`, `cookbook/load.py`, `scripts/{check_data,test_check_data,render_gold_review,generate_tickets}.py`, `Makefile` (check, test-checks, review, tickets-plan, tickets-one, tickets). One article edit made the Apex fee unambiguous (it's added to the buyout amount).
- **Auto-adjustments:** store services made explicit (I-013); agent mistakes picked by count (I-011); `kb:` link markup stripped from ticket prompts.
- **Stuck / waiting:** (1) `ANTHROPIC_API_KEY` in `.env` to run `make tickets-one`, then `make tickets`. (2) Tianyi's review of the 40 draft questions in `data/eval/gold_review.md`, then freeze.

---

## 2026-11-13 · Harness and vault (architecture v2.0)
- **Did:** created the Obsidian vault `~/Projects/Arango/` (Home, CLAUDE.md, internship placeholder, templates, Minimal theme). Moved this repo from the interview-prep vault to `10 Cookbook Demo/`. Ran `docker compose down` before the move and `up` after; the volume `arango-cookbook-prototype_arango_data` survived. Recreated `.venv` (I-008). `verify_env.py` passes in the new location. Deleted the v0 kitchen: folder, container `arango-kitchen`, volume `arango-graphrag-kitchen_kitchen_data` (D-016). Wrote the six harness files. Folded `NOTES.md` into `issues.md` and deleted it, to keep one source of truth.
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
