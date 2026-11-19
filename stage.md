# Stages

The high-level plan: what each stage is for, when it counts as done, and what it must not touch. Work-by-work detail goes in [progress.md](progress.md); the design itself is in [architecture.md](architecture.md).

**Current design:** architecture v3.0, checkpoint **v3.5** (2026-11-18) · **Current stage:** 4 done; next: Tianyi's own words in README/notebooks (stage 6), and the v4.0 question in architecture.md

| # | Stage | Status |
|---|---|---|
| 1 | Spec, KB outline, environment check | done 2026-11-12 |
| 2 | Knowledge-base data, data checks, gold set | done 2026-11-18 (gold frozen) |
| 3 | Retrieval in ArangoDB: load, M1–M6, retrieval eval, freshness demo | done 2026-11-18 (README is a draft) |
| 4 | Semantic layer; grounded answers and answer eval (Opus 5.5 answers, Fable 5.2 judge, $50 ledger) | done 2026-11-18 |
| 5 | Extras: hybrid RRF, entering the graph from names, geo, text-to-AQL, clarifying questions | planned, not scheduled |
| 6 | Publish: five numbered chapter notebooks, README in Tianyi's words, fresh-clone test | not started |

Rule for every stage: when it ends, run the checks in [eval.md](eval.md). If a score drops and no change was meant to cause it, stop and wait for Tianyi.

---

## Stage 1: spec, KB outline, environment check (done 2026-11-12)
**Goal:** agree on what is being built, before building it.
**Done when:**
- [x] `docs/SPEC.md`: problem, idea, what a developer learns, evaluation, rules
- [x] `docs/KB_OUTLINE.md`: every article, form, state, lender, lessor; versions; tricky cases
- [x] `scripts/verify_env.py` passes: vector index, filtered vector search, BM25, form-code tokens
- [x] seed questions: 16 candidates, all kept by Tianyi (2026-11-13)

**Out of scope:** writing article text; any retrieval code.

## Stage 2: knowledge-base data, data checks, gold set (done 2026-11-18)
**Goal:** all the data the cookbook runs on exists, matches `docs/KB_OUTLINE.md`, and a script checks it.
**Done when:**
- [x] 51 articles / 68 versions, `forms` (15), `states` (5), `lenders` (12), `lessors` (6), `stores` (25), known KB issues present
- [x] `make check` passes; `make test-checks` catches 8 of 8 injected faults
- [x] about 200 tickets generated, cached, committed, and covered by `make check`
- [x] real state and city names, rules unchanged, disclaimer on top (D-023, 2026-11-17)
- [x] gold set cut to 30 in a fixed mix, 26 kept in reserve (D-024)
- [x] Tianyi reviewed the 14 drafts and kept all (2026-11-18); `make freeze` wrote `data/eval/FROZEN` (sha256 5935c443…)

**Moved to later (D-024):** messy wording, off-topic and vague questions (35 drafts in `data/eval/candidates.json`). They join in a second gold version, not this freeze.

## Stage 3: retrieval in ArangoDB (done 2026-11-18)
**Goal:** one command loads the KB; four retrieval methods, one AQL each, are measured on the frozen gold set; a live policy change shows up in the next query.
**Done when:**
- [x] `make load`: documents, parsed edges, `kb_graph`, `kb_view`, vector index (about 25 s)
- [x] `make verify` also checks that a document inserted after the vector index was built is found right away
- [x] M1–M4 in `cookbook/retrieve.py` (D-025); `make test-retrieve` passes on the reserve questions
- [x] `make fresh`: the policy change and its before/after, transcript in `data/eval/fresh_demo.md` (D-027)
- [x] `make eval` on the frozen 30: tables in `data/eval/scores/latest.md`, multi-hop + checklist slice, per-question wins and losses (2026-11-18)
- [x] results table and honest limits in the README (DRAFT, 2026-11-18)

**Out of scope:** changing the gold set, the M4 rule or any parameter after seeing gold results.

## Stage 4: semantic layer and grounded answers (in progress)
**Goal:** show what retrieval quality means for the answers a customer gets.
**Done when:**
- [x] semantic layer: 68 extractions cached, `make check-semantic` (recall 0.88), loaded into `kb_graph`; M5/M6 (D-030)
- [x] `cookbook/answer.py`, `scripts/run_answers.py`, spend ledger with a $50 cap (D-029)
- [x] `make answers-run`: M1–M6 × 30 × 3 runs, Fable 5.2 judge; `make answers-report` (2026-11-18, $7.01 in total)
- [x] a human spot-check of 5 judgements (`data/eval/scores/judge_spotcheck.md`): Tianyi agrees with all 5 (2026-11-18)

## Stage 5: extras (planned, not scheduled)
hybrid BM25 + vector with RRF; entering the graph from names in the question (lenders, lessors, form codes); clarifying follow-ups for ambiguous questions (D-022); geo (`GEO_DISTANCE` + graph); `SHORTEST_PATH` explanations; text-to-AQL; community versions of ArangoDB's AI-suite ideas; comparison with other GraphRAG approaches.

## Stage 6: publish
**Done when:**
- [x] five numbered chapter notebooks (01 setup · 02 data model · 03 freshness · 04 retrieval · 05 evaluation) that run with `make nb`, outputs saved (all five run, 2026-11-18)
- [ ] Tianyi has rewritten the README, SPEC and notebook prose in his own words
- [ ] a fresh clone in a new folder works by copy-pasting the README commands
- [ ] a one-page spec is sent to the reviewers
