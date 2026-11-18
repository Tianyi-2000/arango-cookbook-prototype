# Stages

The high-level plan: what each stage is for, when it counts as done, and what it must not touch. Work-by-work detail goes in [progress.md](progress.md); the design itself is in [architecture.md](architecture.md).

**Current design:** architecture **v3.0** (2026-11-17) · **Current stage:** 2 → 3 (gold freeze waiting on Tianyi; stage 3 code done)

| # | Stage | Status |
|---|---|---|
| 1 | Spec, KB outline, environment check | done 2026-11-12 |
| 2 | Knowledge-base data, data checks, gold set | **almost done**: freeze waiting on Tianyi's review of 14 drafts |
| 3 | Retrieval in ArangoDB: load, M1–M4, retrieval eval, freshness demo | **code done**; eval runs after the freeze |
| 4 | Grounded answers and answer eval (Opus 5.5, under $6) | code done, dry run only |
| 5 | Extras: LLM-extracted graph, hybrid RRF, entering the graph from names, geo, text-to-AQL, clarifying questions | planned, not scheduled |
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

## Stage 2: knowledge-base data, data checks, gold set (almost done)
**Goal:** all the data the cookbook runs on exists, matches `docs/KB_OUTLINE.md`, and a script checks it.
**Done when:**
- [x] 51 articles / 68 versions, `forms` (15), `states` (5), `lenders` (12), `lessors` (6), `stores` (25), known KB issues present
- [x] `make check` passes; `make test-checks` catches 8 of 8 injected faults
- [x] about 200 tickets generated, cached, committed, and covered by `make check`
- [x] real state and city names, rules unchanged, disclaimer on top (D-023, 2026-11-17)
- [x] gold set cut to 30 in a fixed mix, 26 kept in reserve (D-024)
- [ ] **Tianyi has reviewed the 14 drafts in `data/eval/gold30_review.md`**, and `make freeze` has written `data/eval/FROZEN`

**Moved to later (D-024):** messy wording, off-topic and vague questions (35 drafts in `data/eval/candidates.json`). They join in a second gold version, not this freeze.

## Stage 3: retrieval in ArangoDB (code done)
**Goal:** one command loads the KB; four retrieval methods, one AQL each, are measured on the frozen gold set; a live policy change shows up in the next query.
**Done when:**
- [x] `make load`: documents, parsed edges, `kb_graph`, `kb_view`, vector index (about 25 s)
- [x] `make verify` also checks that a document inserted after the vector index was built is found right away
- [x] M1–M4 in `cookbook/retrieve.py` (D-025); `make test-retrieve` passes on the reserve questions
- [x] `make fresh`: the policy change and its before/after, transcript in `data/eval/fresh_demo.md` (D-027)
- [ ] `make eval` on the frozen 30: tables in `data/eval/scores/latest.md`, multi-hop + checklist slice, per-question wins and losses
- [ ] results table and honest limits in the README (DRAFT)

**Out of scope:** changing the gold set, the M4 rule or any parameter after seeing gold results.

## Stage 4: grounded answers (code done, not run)
**Goal:** show what retrieval quality means for the answers a customer gets.
**Done when:**
- [x] `cookbook/answer.py`, `scripts/run_answers.py`: dry run by default, $6 cap checked before every call (D-028)
- [ ] `make answers-run`: M2 and M4 on the 30, each answer judged by meaning; `make answers-report`
- [ ] a human spot-check of about 5 judgements before the numbers go in the README

## Stage 5: extras (planned, not scheduled)
LLM-extracted semantic graph (concepts and relations by Claude, scored against a hand-labelled sample; was stage 4 in v2.0); hybrid BM25 + vector with RRF; entering the graph from names in the question (lenders, lessors, form codes); clarifying follow-ups for ambiguous questions (D-022); geo (`GEO_DISTANCE` + graph); `SHORTEST_PATH` explanations; text-to-AQL; community versions of ArangoDB's AI-suite ideas; comparison with other GraphRAG approaches.

## Stage 6: publish
**Done when:**
- [ ] five numbered chapter notebooks (01 setup · 02 data model · 03 freshness · 04 retrieval · 05 evaluation) that run with `make nb`, outputs saved
- [ ] Tianyi has rewritten the README, SPEC and notebook prose in his own words
- [ ] a fresh clone in a new folder works by copy-pasting the README commands
- [ ] a one-page spec is sent to the reviewers
