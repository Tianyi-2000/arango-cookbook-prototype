# ArangoDB cookbook prototype: GraphRAG over a versioned support knowledge base

> **Status: prototype, stage 1 of 6.** The spec and the KB outline are ready; the data, notebooks and results are not built yet. See [docs/SPEC.md](docs/SPEC.md).

A support assistant has to answer from the *current* policy, for the customer's *state* and *situation*, and it often needs facts from more than one article. This cookbook shows how to do that in one ArangoDB database: keyword search, vector search, version and state filters, and graph traversal over the knowledge base's own structure (links, form references, version chains), combined in single AQL queries. It also shows how to measure each piece.

The knowledge base belongs to **Northwind Auto, a fictional used-car retailer**. All companies, states and policies are invented for illustration and are not legal information.

## Plan
| Stage | What | Status |
|---|---|---|
| 1 | Spec, KB outline, environment check | done |
| 2 | Knowledge base data + data checks; gold questions written, reviewed, frozen | next |
| 3 | Notebook 1: BM25, vectors, hybrid, filters, structural graph, retrieval eval (no API key) | |
| 4 | Notebook 2: LLM-extracted graph, grounded answers, answer eval (needs an API key) | |
| 5 | Extras: geo, shortest-path explanations, text-to-AQL | |
| 6 | Fresh-clone test, final README | |

## Quickstart (environment check only, for now)
```bash
docker compose up -d                                 # ArangoDB 3.12.13 on localhost:8535
python3 -m venv .venv && source .venv/bin/activate   # Python 3.10+
pip install -r requirements.txt
python scripts/verify_env.py                         # prints OK
```
