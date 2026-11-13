# Spec: GraphRAG over a versioned support knowledge base, in one ArangoDB

Status: **prototype, draft spec** (stage 1 of 6). Feedback welcome before the build.

## The problem
A support assistant answers from the help center. Plain vector RAG fails in predictable ways:
- It retrieves the article that **looks** most like the question, even when that article covers a different case (a paid-off car rather than one with a loan, another state, the buying side rather than the selling side).
- It retrieves **superseded** policy versions next to current ones.
- It misses the **second article** an answer needs, because that article doesn't look like the question.
- It can't produce a **complete list** of requirements that are spread across articles.

The origin is a real experience: a retailer's chatbot said a car can't be sold without the title in hand. A phone agent then asked which state the customer was in, and the answer turned out to be yes, because the lender holds the title. The answer depended on facts linked across several policies.

## The idea
A help center is already a graph. Articles link to each other, cite forms by code, replace older versions, and apply to some states and not others. Vector RAG throws that structure away. ArangoDB can keep the text index, the vectors, the metadata and the graph in one database and query all of them in one AQL statement.

## What a developer learns
1. Documents, keys, and AQL basics on a real-looking KB
2. ArangoSearch: analyzers, BM25, and exact matches on form codes
3. Vector index and `APPROX_NEAR_COSINE`, including with a `FILTER` (current versions only)
4. Hybrid search: BM25 and vectors fused with RRF in one query
5. Building the **structural graph** from the KB itself: links, form references, version chains, states (deterministic, no LLM)
6. GraphRAG retrieval: hybrid seeds → graph expansion, in one query
7. *(chapter 2)* Building a **semantic graph** with an LLM (situations, requirements, parties), and scoring the extraction against a hand-labelled sample
8. *(chapter 2)* Grounded answers with citations, and how to evaluate them
9. *(later)* Geo (nearest store that can do a lease buyout), `SHORTEST_PATH` as an explanation ("why do I need this form?"), text-to-AQL, and a comparison with ArangoDB's own GraphRAG tooling

## Data
22 articles (30 versions, eight of them rewritten in 2026), 7 forms, 3 fictional states, 3 fictional leasing companies. See `KB_OUTLINE.md`. Everything is fictional and labelled as illustrative.

## Evaluation
About 40 questions in 7 types: exact, semantic, multi_hop, temporal, conditional, checklist, unanswerable. Each question also lists its **trap** articles.
- Retrieval (no LLM): Recall@k, All-gold@k, MRR, **trap@k** and **stale@k**, by question type × method
- Answers (chapter 2): required facts present, citations valid, correct refusal on unanswerable questions, wrong answers caused by a trap
- Extraction (chapter 2): precision and recall against a hand-labelled sample

Methods: M1 BM25 · M2 vector · M3 hybrid RRF · M4 M3 + version/state filter · M5 M4 + structural graph · M6 M4 + semantic graph · M7 graph traversal for checklists.

## Rules we hold ourselves to
- A question's gold articles are the ones a correct answer must cite, decided when the question is written. They are never derived from the graph or from any method's output.
- The gold set is frozen (commit + sha256) before any method runs. After that, no changes to data, questions or parameters to make a pattern appear.
- The author wrote both the articles and most of the questions. The results show how the mechanism works, not real-world accuracy, and the README says so.

## Run
Docker + Python 3.10+, no API key for chapter 1. Target: a reviewer copy-pastes the README commands into a fresh clone and gets the same numbers.
