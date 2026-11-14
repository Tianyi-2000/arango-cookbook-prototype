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

### I-009 · The data check let an anachronistic link through
- **Symptom:** a mutation test added a link from `selling_with_loan__2022` (unchanged since 2022) to `epayoff_network` (new in 2026), and `make check` still passed.
- **Root cause:** the check asked whether the two articles' effective periods *overlap*. An unchanged 2022 article is still in effect in 2026, so it overlaps everything. But its text was written in 2022 and can't mention a 2026 article.
- **Fix:** a version's links and form codes must exist **on the day the version took effect**. A retired form is allowed only when the same text names its replacement (for example "NW-ODO-2 replaced NW-ODO-1").
- **Verified:** `make test-checks` catches all 5 injected faults; `make check` passes on the real data.
- **Lesson:** "valid at some point" isn't the same as "valid when it was written". Time-versioned data needs the second rule.

### I-010 · The first mutation test never applied its mutations
- **Symptom:** all 5 injected faults reported MISSED, including overlapping versions, which the checker clearly catches when run directly.
- **Root cause:** the loop copied the data but never called the mutation function on the copy.
- **Fix:** call `mut(tmp)` before running the checker. The harness now lives in `scripts/test_check_data.py` (`make test-checks`) and exits non-zero if any fault is missed.
- **Lesson:** a test of the tests needs at least one case known to fail. "Everything missed" is just as suspicious as "everything passed".

### I-011 · The ticket plan had zero agent mistakes
- **Symptom:** the first dry run planned 200 tickets with `agent errors: 0`; the design calls for about 4%.
- **Root cause:** a 4% coin flip was applied only to tickets that could have the mistake (dated after the rewrite, on a rewritten article), which is about 10 tickets, so the expected count was under 1.
- **Fix:** collect the eligible tickets, then pick exactly `N_AGENT_ERRORS = 8` of them with the seeded RNG.
- **Verified:** the dry run shows 8; the same seed gives the same `plan.json` (identical sha) on two runs; every planned ticket passes the ticket rules from `check_data.py`.
- **Lesson:** when a rare event has a target count, sample the count directly instead of hoping a probability produces it.

### I-012 · Two small vault mistakes
- **Symptom:** the Home page's run command `cd "~/Projects/Arango/..."` fails, because `~` doesn't expand inside quotes. The internship page's `[[stage]]` link was ambiguous, because the vault has two `stage.md` files.
- **Fix:** `cd ~/Projects/Arango/"01 Cookbook Demo"/arango-cookbook-prototype`, and full-path wikilinks (`[[02 Internship (placeholder)/stage|stage]]`).
- **Verified:** ran the `cd` line in a shell; both links point to the placeholder files.

### I-013 · Random store services didn't match "select stores"
- **Symptom:** the seeded random draws gave towing at 17 of 25 stores, which doesn't fit the article's "select stores".
- **Fix:** services and Sunday hours are set by store position within each state (towing at 2 per state = 10, lease buyouts at 3 per state = 15, Sunday at 1 per state = 5; no home pickup in Dunmore). This is a design choice, not noise.

### I-014 · An empty `ANTHROPIC_API_KEY` would hide the `ant auth login` sign-in (caught before it happened)
- **Symptom (expected):** Tianyi chose to sign in with `ant auth login` instead of an API key. `.env` (copied from `.env.example`) contained `ANTHROPIC_API_KEY=` with no value, and `cookbook/db.py` loads `.env` on import. An env var set to an empty string can be taken as "a key is set" and win over the sign-in. Separately, `generate_tickets.py` refused to run without the variable.
- **Fix:** `.env.example` and `.env` now have the line commented out, with a note. The script no longer checks the variable: the SDK resolves credentials itself (API key, or the `ant` sign-in). The script stops with a clear message if the variable is set but empty, and on authentication errors.
- **Verified:** the dry run still works with no credentials; the first real call (`make tickets-one`) after sign-in is the end-to-end test.
- **Lesson:** don't gate on one credential source when the SDK supports several, and never ship a template that sets a secret to an empty value.

### I-015 · The first batch of tickets was repetitive
- **Symptom:** in the first 200 generated tickets, two customer messages were word-for-word identical (t182, t189), 58 pairs shared at least 15% of their word 4-grams, and 71 of 200 used "you guys".
- **Root cause:** tickets with the same topic, style and state got almost the same prompt, and the model (at low effort) wrote almost the same message.
- **Fix:** every ticket now gets a vehicle and a customer persona, drawn from a separate seeded RNG so the rest of the plan didn't change. The prompt asks for varied openings and no filler. A repeat of an earlier (topic, state, style, persona) combination gets a fresh persona from a third RNG; this changed t066, t095, t154 and t168. A new check fails any pair of customer messages sharing 50% or more of their 4-grams. The threshold was set before the regenerated tickets were checked, and it flags 5 pairs in the first batch.
- **Verified:** the second batch has 0 "you guys" and 153 distinct 4-word openings. Its highest overlap is 39% (it was 100%), and `make check` passes.
- **Before and after** (same planned tickets):
  - Batch 1, t182: *"Hi, my car won't start anymore. Can I still sell it to you guys?"*
  - Batch 1, t189: *"Hi, my car won't start anymore. Can I still sell it to you guys?"* (identical)
  - Batch 2, t182 (veteran, midsize SUV): *"Hi, my midsize SUV won't start anymore. Can I still sell it to Northwind Auto? I'm in Corlan."*
  - Batch 2, t189 (long-distance commuter, full-size SUV): *"My SUV won't start anymore. Can I still sell it to you? I'm in Corlan."*
- **What's left, honestly:** short ("brief") messages on the same topic still look alike. This pair is at 35%, under the 50% gate, because there are only so many ways to say "my car won't start". Real customers write like that too, so they stay.
- **Evidence:** the full first batch is kept in `data/tickets/archive/batch1_tickets.json` (not loaded by anything).
- **Lesson:** look at generated data in bulk, not one sample. One sample looked fine; 200 showed the template.

### I-016 · Ticket prompts said "\1" instead of the link text
- **Symptom:** article links in the prompts came out as a literal `(\1)` instead of the link label.
- **Root cause:** the replacement `r'\\1'` inside an f-string was escaped twice when it was patched in. The earlier check only confirmed that `(kb:` was gone, not what replaced it.
- **Fix:** a `plain_text()` helper outside the f-string, with an assert that a sample link becomes its label.
- **Impact:** none of the first-batch texts contained `\1`, and that batch was replaced anyway (I-015).
- **Lesson:** when testing a text transform, check the output equals what you expect, not just that the input pattern is gone.

### I-017 · Faithfulness check: two false alarms and one real finding
- **Symptom:** the new "numbers must come from the cited article" check flagged t076 ("90", "1") and t155 ("80").
- **Root cause:** "90" and "80" were the customer's own mileage, repeated by the agent: a false alarm. "1" came from the agent working out "last Saturday, November 1" from the ticket date: a real finding, because that fact isn't in any source. The first matching version was also too loose ("1" matched inside "2026"), and a too-strict version then missed "NW-ODO-1," before a comma.
- **The invented date** (batch 1, t076, ticket dated 2025-11-07): *"Since your car was delivered last Saturday, November 1, your 7 days run through tomorrow…"* The arithmetic is right, but the delivery date appears in neither the article nor the customer's message.
- **Fix:** the source text now includes the customer's message; numbers match as whole numbers (a unit test with 9 cases passes); and the prompt tells the agent not to work out calendar dates.
- **Verified:** the second batch passes; the archived first batch still fails on t076 "1", as it should.

### I-018 · The candidates check read the real file, so its test missed
- **Symptom:** `make test-checks` reported MISSED for "ambiguous candidate requires all readings", right after the candidates check was added.
- **Root cause:** the check built the path to `candidates.json` from its own file location instead of going through `cookbook.load`, so the test's patched data folder was ignored and the real (correct) file was checked every time. Also, the commit that added it went in before the test run was read, and its progress note wrongly said "caught".
- **Fix:** `load_candidates()` in `cookbook/load.py`, used by the check. The progress note was corrected.
- **Verified:** `make test-checks` catches 8 of 8; `make check` passes.
- **Lesson:** every data read goes through one loader, or tests can't redirect it. Read the test output before committing.

---

## Checked and fine
- **A filtered vector search still uses the index.** With `FILTER d.current == true` before `APPROX_NEAR_COSINE`, the plan shows `EnumerateNearVectorNode`, and `LIMIT 5` still returns 5 matching documents. So "current versions only" can be filtered inside the vector query (`verify_env.py`, 30 random vectors, half of them current).
- **A small corpus is fine for the vector index.** `nLists` 1, 2 and 4 all train on 30 documents. Load the documents before creating the index, because it learns its clusters from vectors that already exist.
- **`text_en` keeps stopwords and stems words** ("the" stays; "paying" → "pay", "loans" → "loan"). BM25's IDF makes the common tokens cheap.
