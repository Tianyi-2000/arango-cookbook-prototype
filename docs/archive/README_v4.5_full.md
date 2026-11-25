> **Archived 2026-11-24.** The long README as of checkpoint v4.5 (commit 6f172f0), kept for reference. Personal practice demo, not an official ArangoDB cookbook. Short version: [README](../../README.md).

<!-- DRAFT: placeholder prose; the author will rewrite this in his own words. -->

# ArangoDB cookbook prototype: GraphRAG over a versioned support knowledge base

> **Status: prototype.** The pipeline runs end to end on a laptop and is measured on two frozen question sets: 30 general support questions (v1) and 20 questions written to need a graph (v2). Prose is a draft.

A used-car retailer's support assistant has to answer from the **current** policy, for the customer's **state** and **situation**, and it often needs facts from more than one article or from records no single article lists. Plain retrieval over a help center gets this wrong in predictable ways: it quotes an outdated copy of a policy, it misses the second article a question needs, and it can't answer "which ones" questions at all. This cookbook builds the whole pipeline inside one ArangoDB database (documents, a graph, a BM25 search view and a vector index), compares retrieval methods and an answering agent with graph tools on the same frozen questions, and shows a policy change reaching the next answer with no re-indexing.

> **Synthetic data.** State names are real; every rule, policy, company and number is synthetic and not legal information. Northwind Auto is fictional, and this project is not affiliated with any real retailer.

## Quickstart (Docker and Python 3.10+)
```bash
make setup   # start ArangoDB 3.12 in Docker, create .venv, wait for the database, check the features used here
make load    # build the database from data/ (about 25 s; embeddings run locally)
make demo    # data checks, every retrieval eval, the freshness demo, answer tables from the cache (no API key)
```
Then open the chapters in `notebooks/` (or run them all with `make nb`). Calling Claude again is optional: answers are cached in `data/eval/`.

## What's inside
- **Knowledge base:** 51 help-center articles in 68 versions (2022 → 2026), 15 forms, 5 states, 12 lenders, 6 leasing companies, 25 stores, 200 past support tickets (75 of them outdated today). Some KB problems are left in on purpose (current articles citing retired forms, a broken link).
- **Two graph layers in one named graph (`kb_graph`):**
  - *structural*, parsed from the KB itself: links between articles, form codes, version chains (`supersedes`), lender and lessor names, states;
  - *semantic*, extracted by Claude: 365 concepts (situations, documents, parties, requirements…) and their relations, merged by our own normalisation rule.
- **Nine retrieval methods and two answering agents,** each query printed before it runs.
- **Two frozen question sets:** v1, 30 support questions in 7 types with trap articles; v2, 20 questions written to need a graph (12 *chain* questions reached through a link, a form or a named company; 8 *list* questions), with 8 more for debugging.

## Pipeline
```
data/ ──make load──► ArangoDB (Community Edition 3.12)
                     documents: articles (+ embeddings), tickets, forms, states, lenders, lessors, stores, concepts
                     edges: links_to · supersedes · uses_form · replaced_by · applies_in · about_lender · about_lessor · cites
                            mentions · relates (semantic layer)
                     kb_view: BM25 (title, text; form codes matched exactly) · vector index on articles.embedding
question ──► M1 BM25 │ M2 vector │ M3 vector + date/state filter │ M4–M6 = M3 + graph walk (structural / semantic / both)
         ──► M7  = M4 + entry points from names in the question (form codes, lenders, leasing companies)
         ──► M8  = one AQL query builds a wide pool (BM25 ∪ vector ∪ graph neighbours ∪ named entities)
                   → a local cross-encoder ranks it                                        (M8n: the same pool without the graph)
         ──► M9  = Claude answers with 4 tools over the database: search, read an article, look up a record, list records
                   (fixed AQL templates; the model never writes AQL)                       (M9s: search only)
         ──► make eval / make eval-v2       retrieval metrics on the frozen sets
         ──► make answers-* / answers-v2-*  Claude answers from each method; a second model judges every required fact
make fresh: new policy version + supersedes edge in one transaction → the next query answers from it
```
M4–M6 are one query: vector search finds 5 entry articles, a traversal walks to linked articles (through a link, a shared form, lender, lessor or concept), and a neighbour inherits its parent's score × 0.8 per hop. Every hit it adds carries the path that explains it. M7 also starts the walk from a form, lender or leasing company the question names (a dictionary match, no LLM).

## Results on questions that need a graph (gold v2: 12 chain + 8 list questions)
### Retrieval
| method | Recall@5, chain (12) | All-gold@5, chain (12) | Recall@5, list (8) | Recall@10, list (8) |
|---|---|---|---|---|
| M1 BM25 | 0.82 | 0.67 | 0.79 | 0.80 |
| M2 Vector | 0.79 | 0.67 | 0.50 | 0.71 |
| M3 Vector + filter | 0.82 | 0.67 | 0.50 | 0.77 |
| M4 Graph: structural | 0.86 | 0.75 | 0.50 | 0.62 |
| M7 Graph: + names | 0.86 | 0.75 | 0.50 | 0.69 |
| M8 Wide → narrow | **0.89** | 0.75 | **0.79** | **0.93** |
| M8n Wide → narrow, no graph | 0.86 | 0.75 | 0.79 | 0.93 |
| *CE\*: cross-encoder over every current article (diagnostic)* | *0.93* | *0.83* | *0.79* | *0.93* |

M5/M6 have the same Recall@5 as M3/M4 here. Full tables, pool recall per source and per-question changes: [data/eval/scores/v2_latest.md](../../data/eval/scores/v2_latest.md).

### Answers (Claude Opus 5.5 answers; Claude Fable 5.2 judges; mean of 3 runs)
| method | facts found (20) | all facts (20) | list items found (8) | list items correct (8) | exact list (8) | says "not covered" ↓ | $ per paid answer |
|---|---|---|---|---|---|---|---|
| M3 Vector + filter (top 5) | 0.64 | 0.55 | 0.38 | 0.38 | 0.38 | 0.35 | 0.023 |
| M4 Graph: structural (top 5) | 0.64 | 0.57 | 0.38 | 0.38 | 0.38 | 0.43 | ~0.023 |
| M7 Graph: + names (top 5) | 0.64 | 0.57 | 0.38 | 0.38 | 0.38 | 0.43 | ~0.023 |
| M8 Wide → narrow (top 5) | 0.74 | 0.63 | 0.60 | 0.75 | 0.50 | 0.33 | 0.023 |
| M8n Wide → narrow, no graph (top 5) | 0.74 | 0.63 | 0.60 | 0.75 | 0.50 | 0.33 | ~0.023 |
| M9s Agent: search only | 0.88 | 0.85 | 0.79 | 0.88 | 0.75 | 0.15 | 0.034 |
| **M9 Agent: search + graph tools** | **0.98** | **0.95** | **1.00** | **1.00** | **1.00** | **0.03** | 0.031 |

Run-to-run ranges: at most 0.05 on facts and list scores, up to 0.10 on "says not covered". $ per paid answer includes the judge; RAG methods that retrieve the same top 5 share one paid answer (M7's top 5 equals M4's on every question). List items are scored in code from the answer's `items` field (an item that maps to no known form, company, state or article counts as wrong). Full table with ranges and spend: [data/eval/scores/v2_answers.md](../../data/eval/scores/v2_answers.md); per question: [v2_answers_per_question.md](../../data/eval/scores/v2_answers_per_question.md); the questions: [data/eval/gold_v2_review.md](../../data/eval/gold_v2_review.md).

### What the numbers say
- **List questions need the database, not a better top 5.** No top 5 holds "every form that is new since February 2026" (seven forms in seven articles) or "the lenders that aren't in the e-payoff network" (the help center never names them; only the lender records do). The agent with graph tools got all 8 lists exactly right in all 3 runs; search only, 6 of 8; the best RAG method, 4 of 8. Most of that gain comes from reading the records directly (`list_records`); walking edges decided the audit question ("which current articles still tell customers to use a retired form": retired forms → the articles that use them → read each) and the impact question (form → `uses_form` → articles).
- **For chain questions, graph retrieval helps a little.** Recall@5 goes 0.82 (M3) → 0.86 (graph walk) → 0.89 (wide → narrow); the graph's share of M8 is one question (v2c01: M7 reaches the e-payoff network article through the lender's name but its inherited score ranks it 10th; in M8 the reranker lifts it to 4th), and it changed no answer (M8 and M8n score the same). In this small KB the second article is usually also a close text match.
- **Searching more than once is worth a lot on its own** (M9s 0.88 facts vs 0.74 for the same search used once), and the graph tools add the rest (0.98). They cost about the same as a RAG answer: prompt caching makes the extra turns cheap, and the agent averaged 2.8 tool calls.
- **Retrieve wide, rank narrow works.** The cross-encoder lifts Recall@5 on the list questions from 0.50 to 0.79 and on v1 from 0.80 to 0.85 (v1 is a seen set for it), mostly through articles that only BM25 put into the pool. The pool is its limit: CE\* beats M8 on chain questions because one article (v2c05, cars that don't run) never enters the pool from any source.
- **What the graph didn't fix.** v2c08 needs Texas's duplicate-title rule for a customer in Georgia; the state filter removes that article for every filtered method; only M9 found the Texas timing (in 2 of 3 runs), from the Texas state record. On the two KB-conflict questions (a current article still naming a retired form) every method answered correctly, because the current rule sat in the same context; citing the outdated article didn't mislead the model here.

## Results on general support questions (gold v1, frozen 30; 27 have retrieval targets)
| method | Recall@5 | Recall@10 | Recall@5, multi-hop + checklist (12) | stale@5 ↓ | trap@5 ↓ |
|---|---|---|---|---|---|
| M1 BM25 | 0.63 | 0.75 | 0.50 | 0.78 | 0.26 |
| M2 Vector | 0.77 | 0.84 | 0.66 | 0.78 | 0.41 |
| M3 Vector + filter | 0.80 | 0.88 | 0.71 | **0.00** | 0.37 |
| M4 Graph: structural | 0.80 | 0.88 | 0.72 | 0.00 | 0.37 |
| M5 Graph: semantic | 0.80 | 0.88 | 0.71 | 0.00 | 0.33 |
| M6 Graph: both layers | 0.80 | 0.88 | 0.72 | 0.00 | 0.37 |
| *M7 Graph: + names (seen)* | *0.80* | *0.92* | *0.72* | *0.00* | *0.37* |
| *M8 Wide → narrow (seen)* | *0.85* | *0.92* | *0.76* | *0.00* | *0.37* |
| *M8n Wide → narrow, no graph (seen)* | *0.85* | *0.94* | *0.76* | *0.00* | *0.33* |

stale@5: share of questions with an outdated policy version in the top 5. *Seen*: M7–M8n were designed after reading these results, so their rows are not a clean test. Full tables: [data/eval/scores/latest.md](../../data/eval/scores/latest.md).

### Answer quality on v1 (Claude Opus 5.5 answers from each method's top 5; Claude Fable 5.2 judges; mean of 3 runs, [lowest–highest run])
| method | facts found (27) | all facts (27) | says "not covered" ↓ | cites an outdated version ↓ | declines when not covered (3) |
|---|---|---|---|---|---|
| M1 BM25 | 0.65 [0.64–0.66] | 0.53 [0.52–0.56] | 0.48 | 0.16 | 1.00 |
| M2 Vector | 0.82 [0.80–0.84] | 0.73 [0.70–0.78] | 0.35 | 0.04 | 1.00 |
| M3 Vector + filter | 0.84 [0.82–0.86] | 0.78 [0.74–0.81] | 0.31 | 0.00 | 1.00 |
| M4 Graph: structural | 0.85 [0.82–0.88] | 0.80 [0.74–0.85] | 0.30 | 0.00 | 1.00 |
| M5 Graph: semantic | 0.83 [0.80–0.84] | 0.75 [0.70–0.78] | 0.31 | 0.00 | 1.00 |
| M6 Graph: both layers | 0.85 [0.82–0.88] | 0.80 [0.74–0.85] | 0.30 | 0.00 | 1.00 |

- **The biggest win on v1 is the filter, in the same query as the vector search.** Plain BM25 and vector retrieval put an outdated version in the top 5 for 78% of questions; filtering by the date the rules apply and by the customer's state brings that to 0%.
- **Graph expansion is about neutral on v1.** It wins q22 (the offer-validity article, through a link from the duplicate-title article) and loses q42 (four neighbours of a strong first hit push a correct article out). The semantic layer changes no question at K=5.
- **Answers follow retrieval.** With the filter, no answer cites an outdated version; the graph methods are within run-to-run noise of M3; every method declines the questions the help center doesn't cover. Full table: [data/eval/scores/answers.md](../../data/eval/scores/answers.md).

API cost in the spend ledger (semantic layer, 960 answers and their judgements, agents included): $14.63; the tickets cost $3.10 before the ledger existed.

### Freshness demo (`make fresh`)
Payment timing changes from "1 to 3 business days" to "within minutes". In one transaction (8–25 ms across runs) the new version goes in, the old one is closed and a `supersedes` edge is added. Right after the commit, every filtered method (M3–M8n) returns the new version; plain vector search (M2) still ranks the 2022 version first. Transcript: [data/eval/fresh_demo.md](../../data/eval/fresh_demo.md).

## Why a graph matters more in a large, messy KB (argued, not measured here)
This KB is small and tidy: about 50 articles in effect on any day, one author, consistent names and links. That is why vector search already reaches most of the second articles a chain question needs, and why CE\* (rerank every article) is even possible. A real help center differs in ways that each favour the graph:

1. **Look-alikes crowd the top k.** With thousands of articles, many restating one policy for other products, states or years, the top 10 by similarity fills with near-copies of the closest topic, and the second article a question needs (the lender, the form, the state rule) drops out. A link or a shared entity reaches it however many look-alikes exist.
2. **A walk costs the neighbourhood, not the KB.** Expanding 5 entry articles over their links and forms touches tens of nodes whether the KB holds 50 articles or 50,000. Reranking everything (CE\* here) grows with the KB; reranking a pool that the graph helped fill doesn't.
3. **Names collide.** More lenders, products and partners means more near-identical names (here already two "Harbor"s and two "Summit"s). Embeddings blur names; an entity dictionary plus edges keeps them apart and makes "every article about this lender" exact.
4. **List and maintenance questions grow with the KB.** "Which current articles still tell customers to use a retired form?" is 2 of 50 here. In a large help center no top k can list them; a graph query over form status and `uses_form` edges returns all of them, which is how stale advice gets fixed before a customer reads it.
5. **Messy prose, clean structure.** The text of a big KB drifts (synonyms, typos, outdated wording), but its structure (links, form codes, CMS fields, version dates, product IDs) usually stays machine-readable. The structural graph is built from that structure, not from the prose.
6. **Change at scale.** Versions with `supersedes` edges and a date filter keep one query correct as policies change; re-chunking or re-embedding the KB for each change doesn't scale.

What would test this: the same question types, frozen the same way, on a KB about ten times larger with near-duplicates and many more entities. Not built here.

## Run it, step by step
```bash
make setup           # docker compose up -d (ArangoDB 3.12.13 on localhost:8535, vector index on), .venv, make verify
make check           # data consistency, including gold v2 answers recomputed from the records
make load            # build the database from data/
make test-retrieve   # every method on the debugging questions: index use, nothing stale, determinism
make eval            # v1 retrieval eval (frozen 30)
make eval-v2         # v2 retrieval eval (frozen 20), with pool recall per source
make fresh           # the freshness demo
make nb              # the six chapter notebooks, run in place
# needs Claude API access (ANTHROPIC_API_KEY or `ant auth login`); results are cached in data/, so this is optional:
make answers         # v1 dry run with a cost estimate; make answers-run calls the API
make answers-v2      # v2 dry run (RAG methods + agents); make answers-v2-run calls the API
```
The cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`, about 90 MB) and the embedding model download from Hugging Face on first use and run on the CPU.

## Chapters
`notebooks/01_setup` · `02_data_model` · `03_freshness` · `04_retrieval` · `05_evaluation` · `06_graph_questions`

## What ArangoDB provides, and what this repo builds
- **ArangoDB Community Edition 3.12:** document and edge collections, named graphs and traversals (`PRUNE`, `edgeCollections`, start vertices from a bind variable), ArangoSearch with BM25 and analyzers, a vector index (`APPROX_NEAR_COSINE`, with pre-filters), `COSINE_SIMILARITY`, subqueries and `UNION_DISTINCT` (the wide pool is one query), stream transactions, all in one query language.
- **This repo:** the data and both gold sets, edge parsing, the semantic extraction prompt and name merging, the name dictionary, the queries and the score-propagation rule, the reranking step, the agent's tool templates and loop, metrics, the eval harness, the freshness demo, the answer and judge prompts. No LangChain or LlamaIndex, and no ArangoDB GraphRAG product.

## Things we found about the engine
- Vector search accepts only simple filters: two `FILTER` statements before `APPROX_NEAR_COSINE` fail with ERR 1554 once a bind variable can't be folded away; one `FILTER … AND …` works ([issues.md](../../issues.md) I-020).
- A document inserted after the vector index was built is found by the next query, without rebuilding the index.
- `APPROX_NEAR_COSINE` and `COSINE_SIMILARITY` differ by about 1e-8; ranking ties need an explicit tie-break to be reproducible (I-019, I-021).

## Honest limits
- **Same author.** The data and both question sets come from the same author, and gold v2 was written *to need a graph*. The results show how each method handles these kinds of question, not how often customers ask them or real-world accuracy.
- **The filter is given the right date and state.** Each gold question carries the date whose rules apply (`as_of`) and the customer's state, and the filtered methods use them as they are. That is why stale@5 is exactly 0. A real assistant has to get the state from the account and the date from the message; that step isn't built or measured. And a hard state filter is wrong when the rule belongs to another state (v2c08).
- **M9's list wins rest on records.** This KB has structured records for forms, lenders, leasing companies and states that agree with the text (`make check`). A help center without them would have to extract them first.
- **Small sets.** 30 and 20 questions: a difference of one or two questions is noise. The three answer runs vary little because the same retrieval feeds each run.
- The semantic layer's name merging is rule-based; synonyms such as "lender" and "lienholder" stay separate.
- Answers are judged by an LLM (a different model from the one answering); human spot-checks: `data/eval/scores/judge_spotcheck.md` (v1) and `v2_judge_spotcheck.md` (v2).

## Licence of the database
ArangoDB 3.12 Community Edition is distributed under the ArangoDB Community License: free for non-commercial use, with a 100 GB dataset limit for production use. Read the official terms before any commercial use. This prototype is non-commercial and its data is a few hundred kilobytes.

## Project docs
[stage.md](../../stage.md) (where it stands) · [architecture.md](../../architecture.md) (the design, by version) · [progress.md](../../progress.md) (log) · [decisions.md](../../decisions.md) (why) · [issues.md](../../issues.md) (what broke) · [eval.md](../../eval.md) (how it's measured)
