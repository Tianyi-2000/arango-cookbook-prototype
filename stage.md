# Stages

The high-level plan: what each stage is for, when it counts as done, and what it must not touch. Work-by-work detail goes in [progress.md](progress.md); the design itself is in [architecture.md](architecture.md).

**Current design:** architecture v4.0, checkpoint **v4.5** (2026-11-18) · **Current stage:** 5 done; 6 (publish) needs Tianyi's own words and his OK to push

| # | Stage | Status |
|---|---|---|
| 1 | Spec, KB outline, environment check | done 2026-11-12 |
| 2 | Knowledge-base data, data checks, gold set | done 2026-11-18 (gold frozen) |
| 3 | Retrieval in ArangoDB: load, M1–M6, retrieval eval, freshness demo | done 2026-11-18 (README is a draft) |
| 4 | Semantic layer; grounded answers and answer eval (Opus 5.5 answers, Fable 5.2 judge, $50 ledger) | done 2026-11-18 |
| 5 | v4.0: questions that need a graph (gold v2), names → graph (M7), wide → narrow (M8), graph tools (M9) | done 2026-11-18 |
| 6 | Publish: chapter notebooks, quickstart, README in Tianyi's words, fresh-clone test | in progress |
| 7 | Extras: hybrid RRF, geo, text-to-AQL, clarifying questions, inferring the date and state | planned, not scheduled |

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

## Stage 4: semantic layer and grounded answers (done 2026-11-18)
**Goal:** show what retrieval quality means for the answers a customer gets.
**Done when:**
- [x] semantic layer: 68 extractions cached, `make check-semantic` (recall 0.88), loaded into `kb_graph`; M5/M6 (D-030)
- [x] `cookbook/answer.py`, `scripts/run_answers.py`, spend ledger with a $50 cap (D-029)
- [x] `make answers-run`: M1–M6 × 30 × 3 runs, Fable 5.2 judge; `make answers-report` (2026-11-18, $7.01 in total)
- [x] a human spot-check of 5 judgements (`data/eval/scores/judge_spotcheck.md`): Tianyi agrees with all 5 (2026-11-18)

## Stage 5: questions that need a graph (v4.0, done 2026-11-18)
**Goal:** measure the graph on questions where it should matter (chain and list questions), with rules fixed before the run and ablations that isolate what the graph adds.
**Done when:**
- [x] gold v2 (12 chain + 8 structural) and 8 dev questions written; structural answers recomputed from the records by `make check`; `make freeze-v2` (D-031)
- [x] M7 names → graph, M8 wide → narrow with a cross-encoder, M8n; debugged on dev + v1 reserve only; rules committed before the gold v2 run (D-032, D-033)
- [x] `make eval-v2`: retrieval on gold v2 and pool recall per source; `make eval` on v1 (seen) with M1–M6 unchanged
- [x] M9 agent and M9s (D-034); answer eval on gold v2: M3, M4, M7, M8, M8n, M9s, M9 × 3 runs; item precision/recall; spend within the $50 ledger
- [x] README: v4.0 results, why a graph matters more in a large, messy KB (argued, no invented numbers)

**Out of scope:** changing gold v2 or any v4.0 rule after its first run; a bigger KB; text-to-AQL.

## Stage 6: publish
**Done when:**
- [x] a three-command quickstart in the README
- [x] a "what you'll learn" opening per chapter (DRAFT)
- [x] numbered chapter notebooks (01 setup · 02 data model · 03 freshness · 04 retrieval · 05 evaluation · 06 graph questions) that run with `make nb`, outputs saved (all six run, 2026-11-18)
- [ ] Tianyi has rewritten the README, SPEC and notebook prose in his own words
- [x] a fresh clone in a new folder works by copy-pasting the README commands (2026-11-18: `make setup`, `make load`, `make demo`; same tables)
- [ ] a one-page spec is sent to the reviewers

## Stage 7: extras (planned, not scheduled)
hybrid BM25 + vector with RRF; clarifying follow-ups for ambiguous questions (D-022); geo (`GEO_DISTANCE` + graph); `SHORTEST_PATH` explanations; text-to-AQL; inferring `as_of` and state from the message; community versions of ArangoDB's AI-suite ideas; comparison with other GraphRAG approaches.
