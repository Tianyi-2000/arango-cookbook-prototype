<!-- DRAFT: placeholder prose; the author will rewrite this in his own words. -->

# ArangoDB cookbook prototype: GraphRAG over a versioned support knowledge base

> **Status: prototype, stage 1 of 6.** The spec and the KB outline are ready; the data, notebooks and results are not built yet. See [docs/SPEC.md](docs/SPEC.md).

A support assistant has to answer from the *current* policy, for the customer's *state* and *situation*, and it often needs facts from more than one article. This cookbook shows how to do that in one ArangoDB database: keyword search, vector search, version and state filters, and graph traversal over the knowledge base's own structure (links, form references, version chains), combined in single AQL queries. It also shows how to measure each piece.

The knowledge base belongs to **Northwind Auto, a fictional used-car retailer**.

> **Synthetic data.** State names are real; every rule, policy, company and number is synthetic and not legal information. Northwind Auto is fictional, and this project is not affiliated with any real retailer.

## Plan
| Stage | What | Status |
|---|---|---|
| 1 | Spec, KB outline, environment check | done |
| 2 | Knowledge base (68 article versions, entities, stores) + generated support tickets + data checks; gold questions written, reviewed, frozen | next |
| 3 | Notebook 1: BM25, vectors, hybrid, filters, structural graph, retrieval eval (no API key) | |
| 4 | Notebook 2: LLM-extracted graph, grounded answers, answer eval (needs an API key) | |
| 5 | Extras: geo, shortest-path explanations, text-to-AQL | |
| 6 | Fresh-clone test, final README | |

## Project docs (read these first)
| File | What |
|---|---|
| [stage.md](stage.md) | stages, done criteria, scope |
| [progress.md](progress.md) | detailed work log |
| [architecture.md](architecture.md) | the design, by version |
| [decisions.md](decisions.md) | why we chose what we chose |
| [issues.md](issues.md) | what broke and how it was fixed |
| [eval.md](eval.md) | metrics, checks, regression rule |

## Quickstart (environment check only, for now)
```bash
docker compose up -d                                 # ArangoDB 3.12.13 on localhost:8535
python3 -m venv .venv && source .venv/bin/activate   # Python 3.10+
pip install -r requirements.txt
python scripts/verify_env.py                         # prints OK
```
