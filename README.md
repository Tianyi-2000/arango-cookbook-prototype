<!-- DRAFT: placeholder prose; the author will rewrite this in his own words. -->

# ArangoDB cookbook prototype: GraphRAG over a versioned support knowledge base

> **Status: prototype.** The pipeline runs end to end on a laptop and is measured on a frozen set of 30 questions. Prose is a draft.

A used-car retailer's support assistant has to answer from the **current** policy, for the customer's **state** and **situation**, and it often needs facts from more than one article. Plain retrieval over a help center gets this wrong in a predictable way: the index holds every copy of a policy ever written, so the assistant quotes an outdated one. This cookbook builds the whole retrieval pipeline inside one ArangoDB database (documents, a graph, a BM25 search view and a vector index), compares six retrieval methods on the same questions, and shows a policy change reaching the next answer with no re-indexing.

> **Synthetic data.** State names are real; every rule, policy, company and number is synthetic and not legal information. Northwind Auto is fictional, and this project is not affiliated with any real retailer.

## What's inside
- **Knowledge base:** 51 help-center articles in 68 versions (2022 → 2026), 15 forms, 5 states, 12 lenders, 6 leasing companies, 25 stores, 200 past support tickets (75 of them outdated today). Some KB problems are left in on purpose (current articles citing retired forms, a broken link).
- **Two graph layers in one named graph (`kb_graph`):**
  - *structural*, parsed from the KB itself: links between articles, form codes, version chains (`supersedes`), lender and lessor names, states;
  - *semantic*, extracted by Claude: 365 concepts (situations, documents, parties, requirements…) and their relations, merged by our own normalisation rule.
- **Six retrieval methods, one AQL query each,** every query printed before it runs.
- **A frozen gold set:** 30 questions in 7 types (multi-hop, checklist, temporal, conditional, exact, semantic, unanswerable), with trap articles that look right but aren't.

## Pipeline
```
data/ ──make load──► ArangoDB (Community Edition 3.12)
                     documents: articles (+ embeddings), tickets, forms, states, lenders, lessors, stores, concepts
                     edges: links_to · supersedes · uses_form · replaced_by · applies_in · about_lender · about_lessor · cites
                            mentions · relates (semantic layer)
                     kb_view: BM25 (title, text; form codes matched exactly) · vector index on articles.embedding
question ──► M1 BM25 │ M2 vector │ M3 vector + date/state filter │ M4/M5/M6 = M3 + graph walk (structural / semantic / both)
         ──► make eval    retrieval metrics on the frozen 30
         ──► make answers Claude answers from each method's top 5; a second model judges every required fact
make fresh: new policy version + supersedes edge in one transaction → the next query answers from it
```
M4–M6 are one query: vector search finds 5 entry articles, a traversal walks to linked articles (through a link, a shared form, lender, lessor or concept), and a neighbour inherits its parent's score × 0.8 per hop. Every hit it adds carries the path that explains it.

## Results (frozen 30 questions; 27 have retrieval targets)
| method | Recall@5 | Recall@10 | Recall@5, multi-hop + checklist (12) | stale@5 ↓ | trap@5 ↓ |
|---|---|---|---|---|---|
| M1 BM25 | 0.63 | 0.75 | 0.50 | 0.78 | 0.26 |
| M2 Vector | 0.77 | 0.84 | 0.66 | 0.78 | 0.41 |
| M3 Vector + filter | 0.80 | 0.88 | 0.71 | **0.00** | 0.37 |
| M4 Graph: structural | 0.80 | 0.88 | 0.72 | 0.00 | 0.37 |
| M5 Graph: semantic | 0.80 | 0.88 | 0.71 | 0.00 | 0.33 |
| M6 Graph: both layers | 0.80 | 0.88 | 0.72 | 0.00 | 0.37 |

stale@5: share of questions with an outdated policy version in the top 5. Full tables, per-type scores and per-question wins and losses: [data/eval/scores/latest.md](data/eval/scores/latest.md).

### Answer quality (Claude Opus 5.5 answers from each method's top 5; Claude Fable 5.2 judges; mean of 3 runs, [lowest–highest run])
| method | facts found (27) | all facts (27) | says "not covered" ↓ | cites an outdated version ↓ | declines when not covered (3) |
|---|---|---|---|---|---|
| M1 BM25 | 0.65 [0.64–0.66] | 0.53 [0.52–0.56] | 0.48 | 0.16 | 1.00 |
| M2 Vector | 0.82 [0.80–0.84] | 0.73 [0.70–0.78] | 0.35 | 0.04 | 1.00 |
| M3 Vector + filter | 0.84 [0.82–0.86] | 0.78 [0.74–0.81] | 0.31 | 0.00 | 1.00 |
| M4 Graph: structural | 0.85 [0.82–0.88] | 0.80 [0.74–0.85] | 0.30 | 0.00 | 1.00 |
| M5 Graph: semantic | 0.83 [0.80–0.84] | 0.75 [0.70–0.78] | 0.31 | 0.00 | 1.00 |
| M6 Graph: both layers | 0.85 [0.82–0.88] | 0.80 [0.74–0.85] | 0.30 | 0.00 | 1.00 |

"Says not covered": answerable questions where the answer said the help center doesn't cover part of it, usually because retrieval missed an article; the model declined rather than invent. Full table and spend: [data/eval/scores/answers.md](data/eval/scores/answers.md). Total API cost for the semantic layer and all 540 answers and judgements: $7.01.

### What the numbers say
- **The biggest win is the filter, in the same query as the vector search.** Plain BM25 and vector retrieval put an outdated version in the top 5 for 78% of questions; filtering by the date the rules apply and by the customer's state brings that to 0%.
- **Graph expansion is about neutral here.** The structural graph wins q22 (it reaches the offer-validity article through a link from the duplicate-title article) and loses q42 (four neighbours of a very strong first hit push a correct article out of the top 5). The semantic layer changes no question at K=5. With this rule and this KB, vector search already finds most of what the graph would add.
- **Answers follow retrieval.** BM25's answers find 65% of the required facts and cite an outdated policy 16% of the time; with the filter, no answer cites an outdated version. The graph methods are within run-to-run noise of M3 (their ranges overlap). Every method declines the questions the help center doesn't cover.
- **What the graph does give:** an explanation for every added hit (the path), the version history (`supersedes`) and KB maintenance queries (current articles that still cite a retired form).

### Freshness demo (`make fresh`)
Payment timing changes from "1 to 3 business days" to "within minutes". In one 8–12 ms transaction the new version goes in, the old one is closed and a `supersedes` edge is added. Right after the commit, M3–M6 return the new version; plain vector search (M2) still ranks the 2022 version first. Transcript: [data/eval/fresh_demo.md](data/eval/fresh_demo.md).

## Run it
```bash
docker compose up -d                                 # ArangoDB 3.12.13 on localhost:8535, vector index enabled
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
make verify          # the ArangoDB features used here work (vector index, filtered vector search, BM25, insert after index)
make check           # data consistency
make load            # build the database from data/ (about 25 s; embeddings run locally)
make eval            # retrieval eval on the frozen gold set
make fresh           # the freshness demo
make nb              # the five chapter notebooks, run in place
# needs Claude API access (ANTHROPIC_API_KEY or `ant auth login`); results are cached in data/, so this is optional:
make answers         # dry run with a cost estimate; make answers-run to call the API
```

## Chapters
`notebooks/01_setup` · `02_data_model` · `03_freshness` · `04_retrieval` · `05_evaluation`

## What ArangoDB provides, and what this repo builds
- **ArangoDB Community Edition 3.12:** document and edge collections, named graphs and traversals (`PRUNE`, `edgeCollections`), ArangoSearch with BM25 and analyzers, a vector index (`APPROX_NEAR_COSINE`, with pre-filters), `COSINE_SIMILARITY`, stream transactions, all in one query language.
- **This repo:** the data and gold set, edge parsing, the semantic extraction prompt and name merging, the six queries and the score-propagation rule, metrics, the eval harness, the freshness demo, the answer and judge prompts. No LangChain or LlamaIndex, and no ArangoDB GraphRAG product.

## Things we found about the engine
- Vector search accepts only simple filters: two `FILTER` statements before `APPROX_NEAR_COSINE` fail with ERR 1554 once a bind variable can't be folded away; one `FILTER … AND …` works ([issues.md](issues.md) I-020).
- A document inserted after the vector index was built is found by the next query, without rebuilding the index.
- `APPROX_NEAR_COSINE` and `COSINE_SIMILARITY` differ by about 1e-8; ranking ties need an explicit tie-break to be reproducible (I-019, I-021).

## Honest limits
- The data and the questions come from the same author, and the multi-hop questions were written so a second article is needed: the results show how the mechanism behaves, not real-world accuracy.
- 30 questions is small: a difference of one or two questions is noise.
- The semantic layer's name merging is rule-based; synonyms such as "lender" and "lienholder" stay separate.
- Answers are judged by an LLM (a different model from the one answering); a human spot-check is in `data/eval/scores/judge_spotcheck.md`.

## Licence of the database
ArangoDB 3.12 Community Edition is distributed under the ArangoDB Community License: free for non-commercial use, with a 100 GB dataset limit for production use. Read the official terms before any commercial use. This prototype is non-commercial and its data is a few hundred kilobytes.

## Project docs
[stage.md](stage.md) (where it stands) · [architecture.md](architecture.md) (the design, by version) · [progress.md](progress.md) (log) · [decisions.md](decisions.md) (why) · [issues.md](issues.md) (what broke) · [eval.md](eval.md) (how it's measured)
