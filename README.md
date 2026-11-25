<!-- DRAFT -->

# A small GraphRAG demo on ArangoDB (practice prototype)

> **Personal practice project, not real work.** This is not an official ArangoDB cookbook or product, and it is not affiliated with or endorsed by ArangoDB. It was built to learn and test ideas, laid out like a cookbook recipe. Toy dataset, small self-written question sets, not production-ready.
>
> **Synthetic data.** State names are real; every rule, policy, company and number is made up and is not legal information. "Northwind Auto" is fictional and not affiliated with any real retailer.

## What this demo pokes at
A support assistant for a (fictional) used-car retailer has to answer from the **current** policy, for the customer's **state** and **situation**. Plain RAG over a help center has three bad habits:
- It quotes the 2022 policy like it's still 2022.
- It finds one article when the answer needs two.
- Asked "which ones?", it shrugs.

This demo keeps everything in one ArangoDB database (documents, a graph, a BM25 search view, a vector index), compares 9 retrieval methods and 2 answering agents on the same frozen questions, and checks that a policy change reaches the next answer with no re-indexing.

## Quickstart (Docker and Python 3.10+)
```bash
make setup   # start ArangoDB 3.12 in Docker, create .venv, wait for the database, check the features used here
make load    # build the database from data/ (about 25 s; embeddings run locally)
make demo    # data checks, every retrieval eval, the freshness demo, answer tables from the cache (no API key)
```
Claude's answers are cached in `data/eval/`, so no API key is needed to see the results.

## Walkthrough notebooks
Six short chapters in [`notebooks/`](notebooks/) (`make nb` runs them all):

| # | chapter | what it shows |
|---|---|---|
| 01 | setup | ArangoDB 3.12 with the vector index on; checking vector search, filtered vector search and BM25 before any data code |
| 02 | data model | documents, edges, a named graph, a BM25 view and a vector index in one database; a graph built from structure already in the data |
| 03 | freshness | a policy change reaching the next answer with no re-indexing: one stream transaction, a date filter, a `supersedes` edge |
| 04 | retrieval | BM25, vector search, a date/state filter and a graph walk as single AQL queries; reading a graph hit's path |
| 05 | evaluation | a frozen question set, trap articles, stale-version hits, an LLM judge, run-to-run variance |
| 06 | graph questions | three ways to use the graph when vector search isn't enough: names → graph (M7), wide → narrow (M8), graph tools for an agent (M9) |

## What's inside
- **A toy help center:** 51 articles in 68 versions (2022 → 2026), 15 forms, 5 states, 12 lenders, 6 leasing companies, 25 stores, 200 past support tickets (75 of them outdated today). A few KB mistakes are left in on purpose (current articles citing retired forms, a broken link).
- **Two graph layers in one named graph (`kb_graph`):** *structural*, parsed from the KB (links, form codes, version chains, lender and lessor names, states); *semantic*, 365 concepts and their relations extracted by Claude, merged by a rule-based name normalisation.
- **9 retrieval methods and 2 answering agents,** each query printed before it runs.
- **Two frozen question sets:** v1, 30 general support questions (7 types, with trap articles); v2, 20 questions written to need a graph (12 *chain*, 8 *list*), plus 8 more for debugging.

## The methods
| method | what it does |
|---|---|
| M1 | BM25 |
| M2 | vector search |
| M3 | vector search + date/state filter, in the same query |
| M4 / M5 / M6 | M3 + a graph walk over structural / semantic / both edge sets |
| M7 | M4 + entry points from names in the question (form codes, lenders, leasing companies; a dictionary match, no LLM) |
| M8 | one AQL query builds a wide pool (BM25 ∪ vector ∪ graph neighbours ∪ named entities), then a local cross-encoder ranks it |
| M8n | M8 without the graph |
| M9 | Claude answers with 4 tools over the database: search, read an article, look up a record, list records (fixed AQL templates; the model never writes AQL) |
| M9s | M9 with the search tool only |

The graph walk (M4–M6): vector search finds 5 entry articles, a traversal walks to linked articles (through a link, a shared form, lender, leasing company or concept), and a neighbour inherits its parent's score × 0.8 per hop. Every hit it adds carries the path that explains it.

## Freshness demo (`make fresh`)
- Payment timing changes from "1 to 3 business days" to "within minutes". One transaction (8–25 ms across runs) inserts the new version, closes the old one and adds a `supersedes` edge.
- Right after the commit, every filtered method (M3–M8n) returns the new version; plain vector search (M2) still ranks the 2022 version first. Old habits. [Transcript](data/eval/fresh_demo.md)

## Results: a small, self-written test
Gold v2: 20 questions written *to need a graph*, by the same author as the data. Read it as a sanity check of the ideas, not a benchmark; the limits are right below.

Answers (Claude Opus 5.5 answers, Claude Fable 5.2 judges, mean of 3 runs):

| method | facts found (20 questions) | exact lists (8 list questions) | $ per answer, judge included |
|---|---|---|---|
| M3 Vector + filter (top 5) | 0.64 | 3/8 | 0.023 |
| M8 Wide → narrow (top 5) | 0.74 | 4/8 | 0.023 |
| M9s Agent: search only | 0.88 | 6/8 | 0.034 |
| M9 Agent: search + graph tools | 0.98 | 8/8 | 0.031 |

What it suggests, in this small KB:
- **Lists needed the database, not a better top 5.** No top 5 holds "every form that is new since February 2026" (seven forms in seven articles). Most of M9's gain came from reading the records directly (`list_records`); walking edges decided the audit question (current articles still naming a retired form) and the impact question.
- **On chain questions the graph helped a little.** Retrieval Recall@5: 0.82 (M3) → 0.86 (graph walk) → 0.89 (M8). The graph's share of M8 is one question, and it changed no answer (M8 and M8n score the same). Here the second article is usually also a close text match.
- **Searching more than once helped a lot on its own** (M9s 0.88 vs 0.74 for the same search used once); the graph tools added the rest, at about the cost of a RAG answer (prompt caching; 2.8 tool calls on average).
- **Retrieve wide, rank narrow helped** (list Recall@5 0.50 → 0.79), mostly through articles only BM25 put into the pool. It can't rank what never gets in: one article (v2c05) never enters the pool.
- **Not fixed:** v2c08, a customer in Georgia needs Texas's duplicate-title rule, and the state filter politely removes that article. Only M9 found the Texas timing (2 of 3 runs), from the Texas state record.
- **On v1 (30 general questions) the filter did most of the work.** BM25 and vector search put an outdated version in the top 5 for 78% of questions; the date/state filter brought that to 0% (it is handed the right date and state, see limits). Graph expansion was about neutral there.

API spend: $14.63 in the ledger (semantic layer, 960 answers and their judgements, agents included), plus $3.10 for the tickets before the ledger existed.

Full tables: v2 [retrieval](data/eval/scores/v2_latest.md) · [answers](data/eval/scores/v2_answers.md) · [per question](data/eval/scores/v2_answers_per_question.md) · [the questions](data/eval/gold_v2_review.md) · v1 [retrieval](data/eval/scores/latest.md) · [answers](data/eval/scores/answers.md)

## Limits (read these before trusting any number above)
- **Same author.** The data and both question sets come from the same author, and gold v2 was written to need a graph. The results show how each method handles these kinds of question, not how often customers ask them or real-world accuracy.
- **The filter is handed the right date and state.** Each question carries the date whose rules apply and the customer's state, so stale@5 = 0 by construction. Getting them from a real account and message isn't built or measured, and a hard state filter is wrong when the rule belongs to another state (v2c08).
- **M9's list results rest on clean records.** Forms, lenders, leasing companies and states exist as structured records that agree with the text (`make check`). A help center without them would have to extract them first.
- **Small sets.** 30 and 20 questions: a difference of one or two questions is noise. The 3 answer runs vary little because the same retrieval feeds each run.
- **Rule-based name merging** in the semantic layer: synonyms such as "lender" and "lienholder" stay separate.
- **An LLM judges the answers** (a different model from the one answering). Spot-checks of 5 judgements: [v1](data/eval/scores/judge_spotcheck.md) by Claude and then a human, [v2](data/eval/scores/v2_judge_spotcheck.md) by Claude only.

<details>
<summary><b>Why a graph might matter more in a big, messy KB</b> (argued, not measured)</summary>

This KB is small and tidy: about 50 articles in effect on any day, one author, consistent names and links. That is why vector search already finds most of the second articles a chain question needs, and why reranking every article is even possible. A real help center differs in ways that each favour the graph:

1. **Look-alikes crowd the top k.** Thousands of near-copies (other products, states, years) push the second article out; a link or a shared entity still reaches it.
2. **A walk costs the neighbourhood, not the KB.** Expanding 5 entry articles touches tens of nodes whether the KB holds 50 articles or 50,000; reranking everything grows with the KB.
3. **Names collide.** More lenders and partners means more near-identical names (already two "Harbor"s and two "Summit"s here). Embeddings blur names; a dictionary plus edges keeps them apart.
4. **List and maintenance questions grow with the KB.** "Which current articles still name a retired form?" is 2 of 50 here; in a large help center no top k can list them, a graph query can.
5. **Messy prose, clean structure.** Text drifts, but links, form codes, CMS fields and version dates usually stay machine-readable, and the structural graph is built from those.
6. **Change at scale.** Versions with `supersedes` edges and a date filter keep one query correct as policies change; re-embedding the KB for each change doesn't scale.

What would test this: the same question types, frozen the same way, on a KB about ten times larger with near-duplicates and many more entities. Not built here.
</details>

<details>
<summary><b>Run it step by step</b></summary>

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
</details>

<details>
<summary><b>Notes from building it</b> (may be specific to this setup)</summary>

- Vector search accepts only simple filters: two `FILTER` statements before `APPROX_NEAR_COSINE` fail with ERR 1554 once a bind variable can't be folded away; one `FILTER … AND …` works.
- A document inserted after the vector index was built is found by the next query, without rebuilding the index.
- `APPROX_NEAR_COSINE` and `COSINE_SIMILARITY` differ by about 1e-8, so ranking ties need an explicit tie-break to be reproducible.
</details>

## What ArangoDB provides, and what this repo builds
- **ArangoDB Community Edition 3.12:** document and edge collections, named graphs and traversals, ArangoSearch with BM25, a vector index with pre-filters, subqueries and `UNION_DISTINCT` (the wide pool is one query), stream transactions, all in one query language.
- **This repo:** the data and both question sets, edge parsing, the semantic extraction prompt and name merging, the name dictionary, the queries and the score rule, the reranking step, the agent's tool templates and loop, metrics, the eval harness, the freshness demo, the answer and judge prompts. No LangChain or LlamaIndex, and no ArangoDB GraphRAG product.

## Licence of the database
ArangoDB 3.12 Community Edition is distributed under the ArangoDB Community License: free for non-commercial use, with a 100 GB dataset limit for production use. Read the official terms before any commercial use. This demo is non-commercial and its data is a few hundred kilobytes.

---
The long version of this README (every table, the pipeline diagram): [docs/archive/README_v4.5_full.md](docs/archive/README_v4.5_full.md)
