# Evaluation

How we measure the pipeline, how to run the checks, and when the agent has to stop. Every stage ends by running the checks for that stage the same way.

## Checks by stage
| Stage | Command | Passes when |
|---|---|---|
| any | `make verify` | the ArangoDB features the cookbook needs work (vector index, filtered vector search, BM25) |
| 2 | `make check` | the data is consistent (list below), and the counts match `stage.md` |
| 3+ | `make eval` | retrieval scores are produced and none dropped without an intended change |
| 4+ | `make eval-answers` | answer scores are produced (needs an API key) |

### What `make check` covers (stage 2)
- every `_key` is unique, and each article `_key` is `<doc_id>__<version>`
- version chains: no overlapping effective dates for one `doc_id`; *rewritten* has a 2022 and a 2026 version; *unchanged* starts 2022-01-01 and is open-ended; *new* starts 2026-02-01; *retired* ends 2026-01-31
- every `kb:` link points to an existing `doc_id`, except the broken links listed as known issues
- every `NW-` code in a text exists in `forms`; every retired code cited by a current article is a listed known issue
- every state, lender and lessor named in the data exists
- gold: every `gold_keys` / `trap_keys` entry exists; every question has a type, `answer_facts` (except unanswerable ones) and a valid `as_of`; 8 questions per type
- tickets: each cites an article version that was in effect on the ticket's date
- counts: 68 article versions, 15 forms, 5 states, 12 lenders, 6 lessors, 25 stores, 56 gold questions

## Gold set
`data/eval/gold.json`, about 56 questions, 8 per type.

| Type | Tests |
|---|---|
| exact | a code or name has to match exactly |
| semantic | same meaning, different words |
| multi_hop | the answer needs a second article that doesn't look like the question |
| temporal | the right version for the date that matters |
| conditional | the right state or situation |
| checklist | the complete list, gathered from several articles |
| unanswerable | the KB doesn't say, so refuse instead of guessing |

Each question also has `trap_keys` (articles that look right but aren't) and `tricky` tags (`time_boundary`, `rule_conflict`, `messy_input`, `messy_kb`). The gold set is frozen (commit + sha256 in `data/eval/FROZEN`) before any method runs. After that, data, questions and parameters don't change to make a pattern appear.

## Retrieval metrics (stage 3+)
Computed over the top-k articles a method returns, per question, then averaged by question type × method.

| Metric | Definition |
|---|---|
| **Recall@10** (headline), Recall@5 | share of a question's gold articles found in the top k |
| All-gold@k | 1 if *every* gold article is in the top k, else 0; the strict metric for multi_hop and checklist |
| MRR@10 | 1 / rank of the first gold article, 0 if none |
| trap@k | 1 if any trap article is in the top k; lower is better |
| stale@k | 1 if a version not in effect on `as_of` is in the top k; lower is better |

- **Baseline:** M1 BM25. **First comparison:** M2 vector, at Recall@10 (D-017).
- The table always says how many questions each cell covers (8 per type, so one question = 0.125).
- Unanswerable questions have no gold articles. They're reported in the answer eval, not in Recall.

## Answer metrics (stage 4+, needs an API key)
- **Facts:** share of `answer_facts` found in the answer
- **Citations:** every cited key is one of the retrieved articles
- **Refusals:** unanswerable questions get "not covered"; the answerable parts of half-answerable questions still get answered
- **Trap-caused errors:** wrong answers whose citations include a trap article

## Regression rule (D-018)
1. `make eval` writes `data/eval/scores/latest.json`, and copies the previous run to `data/eval/scores/history/<date>.json`.
2. It compares every method × type × headline metric with the previous run.
3. If a score dropped and the change log in `progress.md` doesn't name a change meant to cause it, **stop and wait for Tianyi**. Record it in `progress.md`, and in `issues.md` if it turns out to be a bug.

## Current scores
None yet. Retrieval starts in stage 3.

## Honest limits (will go into the README)
- The data and most of the questions come from the same author, so the results show how the mechanism works, not real-world accuracy.
- 8 questions per type is small; differences of one or two questions are noise.
- The semantic graph is scored against a small hand-labelled sample.
