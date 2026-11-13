# Notes: what we checked and what broke

Short, dated findings. Each one says how it was checked.

## 2026-11-12 · ArangoDB 3.12.13, python-arango 8.3.7
- **Vector index flag.** `arangod --vector-index true` is required. Without it, creating a vector index fails and `APPROX_NEAR_COSINE` is an unknown function. (Carried over from an earlier project; `scripts/verify_env.py` checks it.)
- **Filtered vector search works.** With `FILTER d.current == true` before `LET s = APPROX_NEAR_COSINE(...)`, `explain` still shows `EnumerateNearVectorNode`, and `LIMIT 5` still returns 5 matching documents, not fewer. So "current versions only" can be filtered inside the vector query, and we don't have to over-fetch and filter afterwards. Checked on 30 random 8-dim vectors, half marked current.
- **Small corpora are fine.** A vector index with `nLists` 1, 2 or 4 trains (`trainingState: ready`) on 30 documents. The index trains its clusters on vectors that already exist, so load the documents first, then create the index.
- **`text_en` splits form codes.** `TOKENS("Use form NW-POA-2, not NW-POA-1.", "text_en")` → `nw, poa, 2, … nw, poa, 1`. The two codes differ by a single token, so BM25 can barely tell them apart. So codes go into their own `codes` array field, indexed with the `identity` analyzer, for exact matches.
- **`text_en` keeps stopwords** ("the" is a token) and stems ("paying" → "pay", "loans" → "loan").
