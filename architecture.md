# Architecture and design, by version

## How versions work
- **x.0** is a design: what we build and how it fits together. A new x.0 is only for a major design or architecture change, and **Tianyi confirms it before the number changes**.
- **x.5** marks a checkpoint: a stretch of work under design x.0 is finished, but the project isn't.
- There are no 1.1 or 1.2 versions. Smaller changes go in [progress.md](progress.md) (what happened), [decisions.md](decisions.md) (why) and [issues.md](issues.md) (what broke).
- The newest version is at the top. Older ones stay as they were written.

**Current: v3.0** (2026-11-17): real place names, a 30-question gold set, retrieval in ArangoDB as a four-step ladder, a live freshness demo, and an answer eval.

| Version | Date | What | Confirmed by |
|---|---|---|---|
| v3.0 | 2026-11-17 | Retrieval in ArangoDB: M1–M4 ladder, freshness demo, gold 30, real place names, answer eval | Tianyi (plan approval, 2026-11-17) |
| v2.5 | 2026-11-13 | Checkpoint: KB data, data checks (mutation-tested), 56-question gold set, ticket plan | — |
| v2.0 | 2026-11-12 | Medium-size KB: tickets, lenders, stores, four kinds of tricky cases | Tianyi (answers on size, tickets, tricky cases) |
| v1.5 | 2026-11-12 | Checkpoint: stage 1 done under v1.0 | — |
| v1.0 | 2026-11-12 | A cookbook for developers: versioned KB, structural + LLM graph, gold set with traps | Tianyi (plan approval) |
| v0.5 | 2026-11-12 | Checkpoint: kitchen steps 0–3 running | — |
| v0.0 | 2026-11-12 | "GraphRAG kitchen": a step-by-step learning lab | Tianyi (chose the data and the LLM option) |

---

## v3.0: retrieval in ArangoDB, measured (2026-11-17)
**Confirmed by:** Tianyi (approved the 2026-11-17 plan, including Recall@5 as the headline) · **Status:** in progress (gold freeze pending)

### Why this version
Tianyi's goal for the day: a pipeline that runs end to end, with numbers showing what ArangoDB's graph adds to retrieval, and an LLM answer step under $10. v2.0 had the data but no retrieval at all, and 56 questions were too many to review.

### What changed from v2.5
| Area | v2.5 | v3.0 | Why |
|---|---|---|---|
| Place names | 5 fictional states, 25 fictional cities | VA, NC, GA, TX, CA; 25 real cities; rules still synthetic, disclaimer on top | D-023 |
| Gold | 56 (8 per type), drafts unreviewed | 30 (16 seeds + 14 drafts with reasons), 26 in reserve | D-024 |
| Methods | M1–M7 planned | M1–M4, one change per step; graph rule fixed in advance | D-025 |
| Headline metric | Recall@10 | Recall@5; nDCG@5 added; no precision | D-026 |
| LLM steps | graph extraction + answers (stage 4) | answers + judge now (M2 vs M4, $6 cap); LLM-extracted graph later | D-028 |
| Freshness | versions in the data | a live policy change in one transaction (`make fresh`) | D-027 |

### Pipeline
```
data/kb/*.json, data/tickets/tickets.json
   │  make load (cookbook/build.py): parse links, codes, versions, names → edges; embed articles (MiniLM, local)
   ▼
ArangoDB northwind_kb ── documents: articles 68 · tickets 200 · forms 15 · states 5 · lenders 12 · lessors 6 · stores 25
                      ── edges:     links_to 138 · supersedes 17 · uses_form 24 · replaced_by 2 · applies_in 7
                                    about_lender 7 · about_lessor 18 · cites 200           (graph: kb_graph)
                      ── kb_view (ArangoSearch: BM25 on title/text, exact codes) · vector index on articles.embedding
   │
question ──► M1 BM25 │ M2 vector │ M3 vector + filter (as_of, state) │ M4 = M3 + graph expansion   (one AQL each)
   │
   ├─► make eval: Recall@5/10, All-gold@5, MRR, nDCG@5, stale@5, trap@5 by type → data/eval/scores/latest.{json,md}
   ├─► make answers-run: top 5 → Opus 5.5 answer (JSON, citations) → judge by meaning → data/eval/answers/
   └─► make fresh: new policy version + supersedes edge in one transaction → same question, new answer
```

### M4, the GraphRAG step (D-025)
M3's top 10 are candidates; the top 5 are entry points. From each, one traversal of `kb_graph` reaches other articles through `links_to` (1 hop) or through a shared form, lender or lessor (2 hops; 3 with `replaced_by`). `PRUNE` stops at the first article, so a path never runs through another article; states and `supersedes` are not walked. Neighbours must pass M3's filter. Score = max(own cosine, parent × 0.8^hops); best row per article wins; top k. Each result carries the path that raised it (`via`), which explains the hit.

### What ArangoDB provides vs what this repo builds
- **ArangoDB Community Edition 3.12.13:** document and edge collections, named graph and traversal (`PRUNE`, `edgeCollections`), ArangoSearch with BM25 and analyzers, the vector index with `APPROX_NEAR_COSINE` and pre-filters, `COSINE_SIMILARITY`, stream transactions. All in one database and one query language.
- **This repo:** the KB and gold data, the edge parsing, the four queries, the score-propagation rule, the metrics and the eval harness, the freshness demo, the answer and judge prompts. No LangChain or LlamaIndex; no ArangoDB GraphRAG product.

### Engine limits found (and how the code works around them)
- Vector search accepts filters only in simple shapes: two `FILTER` statements fail with ERR 1554 once a state is set; one `FILTER … AND …` works (I-020).
- `APPROX_NEAR_COSINE` (float32) and `COSINE_SIMILARITY` (float64) differ by about 1e-8; M4 scores with one of them only (I-019).
- A document inserted after the vector index was built is found by the next query, with no rebuild (verified).

### Not built yet
Running the eval on the frozen 30; the answer run; the LLM-extracted semantic graph (was stage 4, now later); hybrid RRF; entering the graph from names in the question (lender, lessor, form code); numbered chapter notebooks; README in Tianyi's words.

---

## v2.5: checkpoint, stage 2 data and checks (2026-11-13)
Built under v2.0, with no design change:
- **Data:** 51 articles / 68 versions (`data/kb/articles/01_…08_*.json`), `forms`, `states`, `lenders`, `lessors`, `stores`, `known_issues`. The structural graph will be parsed from `kb:` links and `NW-` codes by `cookbook/load.py`.
- **Checks:** `make check` (counts, version chains, no time travel in links or codes, known issues present, structured records agree with the text, stores, gold, tickets) and `make test-checks` (5 injected faults, all caught).
- **Gold:** 56 questions with two dates each (`asked_on`, `as_of`, D-019); facts graded by meaning (D-020). 40 drafts await review.
- **Tickets:** 200 generated with `claude-opus-5-5` (signed in with `ant auth login`) from a deterministic plan: 75 outdated today, 8 agent mistakes that cite the superseded version, and a persona and vehicle on each for variety. They pass the faithfulness and variety gates (D-021).
- **Not yet built:** loading into ArangoDB, the graph, embeddings, retrieval, notebooks (stage 3).

---

## v2.0: medium-size knowledge base with tricky cases
**Date:** 2026-11-12 · **Confirmed by:** Tianyi · **Status:** in progress (stage 2)

### Why this version
v1.0's 30 article versions were too few to tell the methods apart, and its traps were too clean. Tianyi asked for a decent-size dataset to play with and for real edge cases.

### Data model (one ArangoDB database, `northwind_kb`)
| Collection | Type | Size | Holds |
|---|---|---|---|
| `articles` | document | 51 articles, 68 versions | `_key` = `<doc_id>__<version>`, `doc_id`, `version`, `kind` (unchanged / rewritten / new / retired), `effective_from`, `effective_to` (null = current), `states` (empty = all), `side` (sell / buy), `section`, `title`, `text`, `codes` (parsed from text) |
| `tickets` | document | ~200 | past support conversations, 2022-03 to 2026-10; `created_at`, `channel`, `state`, `customer`, `agent`, `cites` (article version keys), `outdated`, `agent_error` |
| `forms` | document | 15 | `code`, `name`, `status`, `effective_from`, `retired_on`, `replaced_by`, `accepted_until` |
| `states` | document | 5 | fictional states and their rules |
| `lenders` | document | 12 | `name`, `epayoff_network`, `joined` |
| `lessors` | document | 6 | `name`, `third_party_buyout` (by period), `fee`, `equity_to_customer` |
| `stores` | document | 25 | `name`, `state`, `location` (GeoJSON point), `hours`, `services` (used in stage 5) |

"Today" is fixed at **2026-11-01** so results are reproducible.

### Graph (`kb_graph`)
**Structural layer:** built by parsing the data, so it's deterministic and needs no LLM.
| Edge collection | From → To | Source |
|---|---|---|
| `links_to` | article → article | `[label](kb:<doc_id>)` in the text |
| `supersedes` | article version → older version | same `doc_id`, consecutive versions |
| `uses_form` | article → form | `NW-XXX-n` in the text |
| `replaced_by` | form → form | `forms.replaced_by` |
| `applies_in` | article → state | `articles.states` |
| `about_lessor` / `about_lender` | article → lessor / lender | names in the text |
| `cites` | ticket → article version | `tickets.cites` |

**Semantic layer** (stage 4, planned): `concepts` (situation, requirement, party) + `mentions` (article → concept) + `requires` / `issued_by` (concept → concept), extracted by Claude with structured outputs. The output is cached and committed, and scored against a hand-labelled sample.

### Search and vectors
- ArangoSearch view over `articles` (later also `tickets`): `title` and `text` with `text_en` for BM25; `codes` with `identity` for exact matches (because `text_en` splits form codes, see I-002); fuzzy matching for typos (`LEVENSHTEIN_MATCH`) in the messy-input examples.
- Vector index on `articles.embedding`: `all-MiniLM-L6-v2`, 384 dimensions, cosine, small `nLists`. A `FILTER` on the version dates works inside the vector query and still uses the index (checked).

### Retrieval methods (each one AQL query)
M1 BM25 · M2 vector · M3 hybrid RRF · M4 = M3 + filter to versions valid on `as_of` and to the customer's state · M5 = M4 + structural graph expansion (`links_to`, `uses_form` → `replaced_by`, `applies_in`, `supersedes`) · M6 = M4 + semantic graph expansion (stage 4) · M7 graph traversal for checklist questions (stage 4)

### Evaluation
About 56 gold questions, 8 per type: exact, semantic, multi_hop, temporal, conditional, checklist, unanswerable. Each question has `gold_keys`, `trap_keys`, `tricky` tags, `as_of`, `state` and `answer_facts`. Metrics and the regression rule are in [eval.md](eval.md). Recall@10 is the headline; BM25 is the baseline.

### Tickets (how they're generated)
`scripts/generate_tickets.py`: Python decides each ticket's date, topic, cited version, state, channel, whether it's outdated now, and whether it contains an agent mistake (about 4%). Claude writes only the conversation text from the cited article version. Tickets are never the authority; gold keys point to articles.

### KB problems left in on purpose
Current articles that cite retired forms (`selling_for_someone_else` → NW-POA-1, `odometer_problems` → NW-ODO-1); a link to a missing article (`toll_tags_personal_data` → `account_deletion`); old tickets that contradict current articles. A graph query can find the first two.

### Changes from v1.0
- KB: 22 articles / 30 versions → 51 articles / 68 versions. New version kinds: *new in 2026* and *retired*. Explicit transition rules.
- New collections: `tickets`, `lenders`, `stores`; `states` 3 → 5; `lessors` 3 → 6; `forms` 7 → 15. New edges: `cites`, `about_lender`.
- Gold: ~40 → ~56 questions, and tricky tags with their own slice in the eval.
- Seed questions drafted by Claude and kept by Tianyi (in v1.0, Tianyi was to write them).

---

## v1.5: checkpoint, stage 1 done (2026-11-12)
Built under v1.0: repo scaffold, `docker-compose.yml` (ArangoDB 3.12.13, `--vector-index true`, port 8535), `scripts/verify_env.py`, `docs/SPEC.md`, `docs/KB_OUTLINE.md`. Checks showed that a filtered vector search uses the index, `text_en` splits form codes, and `nLists` 1–4 trains on 30 documents.

---

## v1.0: a cookbook for developers (2026-11-12)
**Confirmed by:** Tianyi (plan approval)

### Why this version
Tianyi: the cookbook is "the recipe for developers to learn the tools ArangoDB offers", so it has to be in English, shareable, and show the strengths of a graph database for RAG. v0's learning lab didn't fit.

### Design
- Audience: developers learning ArangoDB. Everything in the repo is English.
- Data: 22 articles / 30 versions (2022 → 2026), 7 forms, 3 fictional states, 3 lessors.
- Two graph layers: structural (parsed from links, codes, versions, states) and semantic (LLM-extracted, scored against a hand-labelled sample). A hand-written facts graph was rejected, because it puts the answers into the graph.
- Gold: ~40 questions in 7 types with trap keys; gold articles decided when a question is written, frozen before any method runs.
- Methods M1–M7, metrics Recall@k, All-gold@k, MRR, trap@k, stale@k.
- Two notebooks (no-LLM chapter, LLM chapter); local git, no push.

### Changes from v0.5
Audience (Tianyi → developers), language (Chinese → English), data (12 flat articles → a versioned KB with entities), a graph from the KB's own structure, an eval plan from the start, and a new repo (`arango-cookbook-prototype`).

---

## v0.5: checkpoint, kitchen steps 0–3 running (2026-11-12)
Steps 0–3 ran: connect, documents, BM25, vector. On the multi-hop question ("Can I sell my car without the title? I'm still paying off the loan.") BM25 and vector each found 1 of 3 expected articles, and both ranked the trap article (`lost_title`) second. On the paraphrase question, BM25 ranked the right article 3rd and vector ranked it 1st.

---

## v0.0: "GraphRAG kitchen" (2026-11-12)
**Confirmed by:** Tianyi (chose the data and the LLM option)
- Goal: let Tianyi see how RAG and GraphRAG get done, one step at a time.
- Data: 12 short synthetic articles from a fictional used-car retailer, including one trap article.
- Shape: one script per step (`steps/s00`–`s10`), each using one ArangoDB feature and printing every AQL query; explanation cards in Chinese (`KITCHEN.md`).
- Planned steps: connect → documents → BM25 → vector → hybrid → plain RAG → LLM-extracted graph → traversal → GraphRAG retrieval → GraphRAG answer → small eval.
- Deleted on 2026-11-13; this record is all that's left (D-016).
