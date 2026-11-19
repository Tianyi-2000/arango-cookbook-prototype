# Evaluation

How we measure the pipeline, how to run the checks, and when the agent has to stop. Every stage ends by running the checks for that stage the same way.

## Checks by stage
| Stage | Command | Passes when |
|---|---|---|
| any | `make verify` | the ArangoDB features the cookbook needs work (vector index, filtered vector search, BM25) |
| 2 | `make check` | the data is consistent (list below), and the counts match `stage.md` |
| 3+ | `make test-retrieve` | every method runs on every reserve question, uses the vector index (also with a state set), and M3/M4 return no stale or wrong-state version |
| 3+ | `make eval` | retrieval scores are produced on the frozen gold set and none dropped without an intended change (refuses to run if `gold.json` doesn't match `FROZEN`) |
| 3+ | `make fresh` | the changed policy is returned by M3/M4 right after the transaction |
| 4+ | `make answers` → `make answers-run` → `make answers-report` | answer scores are produced; spend stays under the $6 cap |

### What `make check` covers (stage 2)
- every `_key` is unique, and each article `_key` is `<doc_id>__<version>`
- version chains: no overlapping effective dates for one `doc_id`; *rewritten* has a 2022 and a 2026 version; *unchanged* starts 2022-01-01 and is open-ended; *new* starts 2026-02-01; *retired* ends 2026-01-31
- every `kb:` link points to an existing `doc_id`, except the broken links listed as known issues
- every `NW-` code in a text exists in `forms`; every retired code cited by a current article is a listed known issue
- every state, lender and lessor named in the data exists
- gold and reserve: every `gold_keys` / `trap_keys` entry exists; every question has a type, `answer_facts` (except unanswerable ones) and a valid `as_of`; the gold set has the D-024 mix
- tickets: each cites an article version that was in effect on the ticket's date (except the 8 planned agent mistakes, which cite the superseded version); `outdated` agrees with the dates
- tickets, faithfulness: every number and form code in an agent reply appears in its cited article or in the customer's message (whole-number match)
- tickets, variety: no two customer messages share 50% or more of their word 4-grams
- `make test-checks` injects 8 known faults into a copy of the data; all must be caught
- counts: 68 article versions, 15 forms, 5 states, 12 lenders, 6 lessors, 25 stores; gold in the D-024 mix, ids unique across gold and reserve

## Gold set
`data/eval/gold.json`: **30 questions** (D-024): multi_hop 7, checklist 5, temporal 5, conditional 4, exact 3, semantic 3, unanswerable 3. 16 are the seeds Tianyi kept; 14 are drafts, each with a written reason (`why_in_30`). The other 26 are in `data/eval/gold_reserve.json` and are used to debug code, never to score it. The tables below say what each type tests.

| Type | Tests |
|---|---|
| exact | a code or name has to match exactly |
| semantic | same meaning, different words |
| multi_hop | the answer needs a second article that doesn't look like the question |
| temporal | the right version for the date that matters |
| conditional | the right state or situation |
| checklist | the complete list, gathered from several articles |
| unanswerable | the KB doesn't say, so refuse instead of guessing |

Two dates per question:
- `asked_on`: when the customer sends the message (default: "today", 2026-11-01).
- `as_of`: the date whose rules decide the answer. Usually the same as `asked_on`; different when the question is about the past ("back in December 2025…") or the future ("my appointment is July 10"). Every gold article must be in effect on `as_of`, and **stale@k is measured against `as_of`**. A method that filters on `asked_on` is wrong on purpose for the historical questions (q28, q30).

Each question also has `trap_keys` (articles that look right but aren't) and `tricky` tags (`time_boundary`, `rule_conflict`, `messy_input`, `messy_kb`). The gold set is frozen (commit + sha256 in `data/eval/FROZEN`) before any method runs. After that, data, questions and parameters don't change to make a pattern appear.

Drafts for the next three sections live in `data/eval/candidates.json` (validated by `make check`, shown at the end of `gold_review.md`) until Tianyi decides how they join the gold set.

### Off-topic and nonsense questions (to add before the freeze)
Real chat traffic includes messages that aren't questions about the KB: gibberish, small talk, half-typed lines. For these the assistant should **skip**: it shouldn't answer from whatever article happens to rank first, and it should ask the user to rephrase or say what it can help with.
- Modeling options, decided when Tianyi adds them: (a) a new type `off_topic` with `answerable: "skip"`, or (b) type `unanswerable` with a new tricky tag `noise`. Either way: no gold articles, no retrieval metrics. The answer eval checks that the reply declines and cites nothing.
- Why it matters for retrieval: every method returns *something* for any input. The cookbook can show a simple guard, such as a minimum score or "no gold-like hit", and measure how often nonsense gets a confident answer.

### Vague questions (to add before the freeze)
Customers often don't know the right term, or write something that can mean more than one thing. Three cases, each scored differently:

| Case | Example | Gold | A good answer |
|---|---|---|---|
| **A. Missing the term, one meaning** | "the paper that says the car is mine" (= title); "the bank still kinda owns part of it" (= lien) | the one article, as usual (tag `vague`) | answers it, using the right term |
| **B. Ambiguous, more than one reasonable reading** | "can I return my car?" (a return of a car bought from Northwind, a lease turn-in, or a sale) | every plausible article; `require_all: false`, so finding any one counts. Recall@k also reports how many of the readings were found | covers the readings briefly, or says which detail decides it |
| **C. The customer says the wrong thing** | says "my lease" but has a loan | the article for **what the message says** | answers what was asked |

**Rule for case C: we grade against what the message says, not what the customer meant.** If the words point to the wrong topic, a wrong answer is the input's fault, not the system's.

**Later (stage 5, not now):** for case B, ask a clarifying question ("Did you mean returning a car you bought, or ending your lease?") instead of guessing. That needs its own metric: asks when the top candidates span different topics, and doesn't ask when the question is clear.

### Human-style wording
Most draft questions are cleaner than real messages. Before the freeze, some get rewritten with typos, broken grammar and run-ons (tag `messy_input`). This mostly hurts BM25 (misspelled tokens don't match) and is where fuzzy matching (`LEVENSHTEIN_MATCH`, n-gram analyzers) earns its place.

## Retrieval metrics (stage 3+, D-026)
Computed over the top-k article versions a method returns, per question, then averaged by question type, over all answerable questions (27) and over the multi_hop + checklist slice (12). Every cell says how many questions it covers.

| Metric | Definition |
|---|---|
| **Recall@5** (headline), Recall@10 | share of a question's gold articles found in the top k |
| All-gold@5 | 1 if *every* gold article is in the top 5, else 0; the strict metric for multi_hop and checklist |
| MRR@10 | 1 / rank of the first gold article, 0 if none |
| nDCG@5 | binary-relevance DCG of the top 5, divided by the best possible |
| stale@5 | 1 if a version not in effect on `as_of` is in the top 5; lower is better |
| trap@5 | 1 if any trap article is in the top 5; lower is better |

- **Why @5:** the KB has 50 current articles; K=10 is a fifth of it. **No precision:** questions average 1.5 gold articles, so Precision@10 can't pass about 0.15.
- **Baseline:** M1 BM25. **The ladder:** M2 vector, M3 vector + filter, M4 GraphRAG; each step adds one thing (D-025).
- The output also lists, per question, where M2 → M3 and M3 → M4 changed Recall@5, with the graph path that brought a gold article in.
- 30 questions is small: a difference of one or two questions is noise.
- Unanswerable questions have no retrieval metrics; they are scored in the answer eval.

## Answer metrics (stage 4, D-028)
M2 and M4 each give their top 5 (key, title, text; no dates) to `claude-opus-5-5`, which answers as JSON with citations. A second call checks every `answer_fact` by meaning (D-020) and whether uncovered parts were declined.
- **Facts found:** share of `answer_facts` present (answerable questions); **all facts:** every fact present
- **Cites a stale version / cites a trap:** citations that point at a version not in effect on `as_of`, or at a trap article
- **Declines when not covered:** the 3 unanswerable questions (one is half-answerable)
- **Cost:** from each response's `usage`; the run stops before the $6 cap
- A human spot-check of about 5 judgements comes before the numbers go in the README.

## Regression rule (D-018)
1. `make eval` writes `data/eval/scores/latest.json`, and copies the previous run to `data/eval/scores/history/<date>.json`.
2. It compares every method × type × headline metric with the previous run.
3. If a score dropped and the change log in `progress.md` doesn't name a change meant to cause it, **stop and wait for Tianyi**. Record it in `progress.md`, and in `issues.md` if it turns out to be a bug.

## Current scores (frozen 30, run 2026-11-18; full tables in `data/eval/scores/latest.md`)
| method | Recall@5 (27) | Recall@10 (27) | Recall@5 multi_hop + checklist (12) | All-gold@5 (12) | MRR@10 | stale@5 | trap@5 |
|---|---|---|---|---|---|---|---|
| M1 BM25 | 0.63 | 0.75 | 0.50 | 0.25 | 0.69 | 0.78 | 0.26 |
| M2 Vector | 0.77 | 0.84 | 0.66 | 0.42 | 0.73 | 0.78 | 0.41 |
| M3 Vector + filter | 0.80 | 0.88 | 0.71 | 0.50 | 0.79 | 0.00 | 0.37 |
| M4 Graph: structural | 0.80 | 0.88 | 0.72 | 0.50 | 0.79 | 0.00 | 0.37 |
| M5 Graph: semantic | 0.80 | 0.88 | 0.71 | 0.50 | 0.79 | 0.00 | 0.33 |
| M6 Graph: both layers | 0.80 | 0.88 | 0.72 | 0.50 | 0.79 | 0.00 | 0.37 |

- The filter (M3) removes every outdated version from the top 5 (78% of questions → 0%).
- Graph expansion is about neutral at K=5: M4/M6 gain q22 (multi_hop, through a structural link) and lose q42 (checklist: neighbours of a strong first hit push a gold article out). M5 changes no question.
- Semantic layer quality (`make check-semantic`): concept recall 0.88, agreement 0.72 on 10 hand-listed versions.
- Answer scores: `data/eval/scores/answers.md` (`make answers-report`).

## Honest limits (will go into the README)
- The data and most of the questions come from the same author, so the results show how the mechanism works, not real-world accuracy.
- 8 questions per type is small; differences of one or two questions are noise.
- The semantic graph is scored against a small hand-labelled sample.
