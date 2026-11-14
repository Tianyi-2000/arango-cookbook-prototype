# Issues

Problems we hit and how we fixed them. Each entry: symptom → root cause → fix → how it was verified → the lesson, which can go straight into the cookbook. Newest at the bottom. "Checked and fine" at the end lists things we tested that turned out not to be problems.

### I-001 · The vector index is off by default
- **Symptom:** creating a vector index fails, and `APPROX_NEAR_COSINE` is an unknown function.
- **Root cause:** in ArangoDB 3.12 the vector index has to be enabled when the server starts.
- **Fix:** `command: ["arangod", "--vector-index", "true"]` in `docker-compose.yml`.
- **Verified:** `scripts/verify_env.py` creates an index and checks the query plan uses it (`EnumerateNearVectorNode`).
- **Lesson:** keep the flag in the README's quickstart; it's the first thing a new user hits.

### I-002 · `text_en` splits form codes
- **Symptom:** `TOKENS("Use form NW-POA-2, not NW-POA-1.", "text_en")` → `use, form, nw, poa, 2, not, nw, poa, 1`.
- **Root cause:** the `text_en` analyzer splits on punctuation, so the two codes differ only by the token `2` vs `1`. BM25 barely separates them, and embeddings blur them too.
- **Fix:** parse codes into their own `codes` array and index it with the `identity` analyzer for exact matches (D-007; built in stage 3).
- **Verified:** `verify_env.py` prints the tokens on every run.
- **Lesson:** IDs, SKUs and form numbers need their own analyzer. This is one of the cookbook's "exact" examples.

### I-003 · There is no built-in `norm_en` analyzer
- **Symptom:** `TOKENS(..., "norm_en")` → HTTP 400, `failure to find arangosearch analyzer with name 'norm_en'`.
- **Root cause:** only some analyzers are built in (`identity`, `text_<lang>`, …). A `norm` analyzer has to be created first.
- **Fix:** none needed; we use `identity` for codes.
- **Lesson:** list the analyzers (`db.analyzers()`) before assuming one exists.

### I-004 · A noisy torch warning on import (macOS)
- **Symptom:** `NOTE: Redirects are currently not supported in MacOs.` on every run that loads sentence-transformers.
- **Root cause:** a log line from `torch.distributed.elastic`, harmless.
- **Fix:** set the logger `torch.distributed.elastic.multiprocessing.redirects` to ERROR before importing sentence-transformers. Done in the v0 kitchen; to be done again in the cookbook's embedding helper (stage 3).
- **Lesson:** keep notebook output clean, or readers think something is broken.

### I-005 · Hugging Face "unauthenticated requests" warning
- **Symptom:** `Warning: You are sending unauthenticated requests to the HF Hub.`
- **Root cause:** no `HF_TOKEN` is set; the model is public and cached after the first download.
- **Fix:** none needed. Mention it in the README so readers don't worry about it.

### I-006 · Two containers on port 8535
- **Symptom:** the v0 kitchen container and the cookbook container both mapped `127.0.0.1:8535`, so the second one couldn't start while the first was running.
- **Fix:** stopped the kitchen container on 2026-11-12 and deleted it on 2026-11-13 (D-016).
- **Lesson:** one container per port. The README states the port, and other local ArangoDB projects use 8529 and 8533.

### I-007 · The cost estimate was too low
- **Symptom:** Claude told Tianyi the whole LLM part would cost "under $0.10", then re-estimated it as "under $0.50".
- **Root cause:** a guess, not a count of tokens × price.
- **Fix:** estimate from token counts before any paid run. `generate_tickets.py` prints its estimate during the dry run, before it spends anything.
- **Lesson:** cost estimates for a cookbook come from measured token counts.

### I-008 · Moving the repo breaks `.venv`
- **Symptom:** after moving the repo folder, entry points in `.venv/bin` (pip, jupyter) still point to the old path.
- **Root cause:** virtualenv scripts have absolute shebangs.
- **Fix:** delete and recreate `.venv`, then reinstall from `requirements.txt` (about a minute with the pip cache). The Docker volume survived, because the folder name, and so the compose project name, didn't change.
- **Verified:** `scripts/verify_env.py` prints OK from the new location (2026-11-13).

---

## Checked and fine
- **A filtered vector search still uses the index.** With `FILTER d.current == true` before `APPROX_NEAR_COSINE`, the plan shows `EnumerateNearVectorNode`, and `LIMIT 5` still returns 5 matching documents. So "current versions only" can be filtered inside the vector query (`verify_env.py`, 30 random vectors, half of them current).
- **A small corpus is fine for the vector index.** `nLists` 1, 2 and 4 all train on 30 documents. Load the documents before creating the index, because it learns its clusters from vectors that already exist.
- **`text_en` keeps stopwords and stems words** ("the" stays; "paying" → "pay", "loans" → "loan"). BM25's IDF makes the common tokens cheap.
