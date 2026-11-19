# Retrieval scores, gold v2 (D-031)

Run 2026-11-18T20:00:52 · commit c3b8a50 · gold sha256 59bba6c5881e · k=10, entries=5, decay=0.8, pool 10+10

### Headline (higher is better, except stale and trap)

| method | recall@5 · all (n=20) | recall@10 · all (n=20) | recall@5 · chain (n=12) | all_gold@5 · chain (n=12) | recall@5 · structural (n=8) | recall@10 · structural (n=8) | mrr@10 · all (n=20) | trap@5 · all (n=20) |
|---|---|---|---|---|---|---|---|---|
| M1 BM25 | 0.81 | 0.85 | 0.82 | 0.67 | 0.79 | 0.80 | 0.66 | 0.10 |
| M2 Vector | 0.68 | 0.82 | 0.79 | 0.67 | 0.50 | 0.71 | 0.59 | 0.10 |
| M3 Vector + filter | 0.69 | 0.82 | 0.82 | 0.67 | 0.50 | 0.77 | 0.65 | 0.10 |
| M4 Graph: structural | 0.72 | 0.78 | 0.86 | 0.75 | 0.50 | 0.62 | 0.63 | 0.10 |
| M5 Graph: semantic | 0.69 | 0.77 | 0.82 | 0.67 | 0.50 | 0.64 | 0.63 | 0.10 |
| M6 Graph: both layers | 0.72 | 0.78 | 0.86 | 0.75 | 0.50 | 0.62 | 0.63 | 0.10 |
| M7 Graph: + names | 0.72 | 0.81 | 0.86 | 0.75 | 0.50 | 0.69 | 0.63 | 0.10 |
| M8 Wide -> narrow | 0.85 | 0.90 | 0.89 | 0.75 | 0.79 | 0.93 | 0.71 | 0.10 |
| M8n Wide -> narrow, no graph | 0.83 | 0.89 | 0.86 | 0.75 | 0.79 | 0.93 | 0.71 | 0.10 |
| CE* diagnostic: cross-encoder over every current article | 0.87 | 0.93 | 0.93 | 0.83 | 0.79 | 0.93 | 0.71 | 0.10 |

CE* is not a method: it reranks every article in effect, which only a KB this small allows. If CE* beats M8, the pool is the limit; if not, the reranker is.


### Recall@5 by question type

| type | n | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M8n |
|---|---|---|---|---|---|---|---|---|---|---|
| chain | 12 | 0.82 | 0.79 | 0.82 | 0.86 | 0.82 | 0.86 | 0.86 | 0.89 | 0.86 |
| structural | 8 | 0.79 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.79 | 0.79 |

### Per question: where each step changed Recall@5

**M1 → M2:** 0 better, 4 worse, 16 unchanged

- v2c01 (chain) -0.33: lost keep_paying_until_confirmed__2022
- v2s01 (structural) -1.00: lost appointment_checklist__2026, co_owners__2026
- v2s02 (structural) -0.29: lost appointment_checklist__2026, co_owners__2026
- v2s06 (structural) -1.00: lost leased_car__2022, payoff_letter__2026

**M2 → M3:** 2 better, 1 worse, 17 unchanged

- v2c01 (chain) +0.33: gained getting_paid__2026
- v2c11 (chain) +0.50: gained negative_equity__2026
- v2c08 (chain) -0.50: lost duplicate_title_texas__2022

**M3 → M4:** 1 better, 0 worse, 19 unchanged

- v2c10 (chain) +0.50: gained negative_equity__2026; path: negative_equity__2026 via offer_scams__2026 > negative_equity__2026

**M3 → M5:** 0 better, 0 worse, 20 unchanged


**M3 → M6:** 1 better, 0 worse, 19 unchanged

- v2c10 (chain) +0.50: gained negative_equity__2026; path: negative_equity__2026 via offer_scams__2026 > negative_equity__2026

**M3 → M7:** 1 better, 0 worse, 19 unchanged

- v2c10 (chain) +0.50: gained negative_equity__2026; path: negative_equity__2026 via offer_scams__2026 > negative_equity__2026

**M3 → M8:** 6 better, 0 worse, 14 unchanged

- v2c01 (chain) +0.33: gained epayoff_network__2026, keep_paying_until_confirmed__2022; lost getting_paid__2026
- v2c10 (chain) +0.50: gained negative_equity__2026
- v2s01 (structural) +1.00: gained appointment_checklist__2026, co_owners__2026
- v2s02 (structural) +0.29: gained appointment_checklist__2026, co_owners__2026
- v2s03 (structural) +0.50: gained odometer_problems__2022
- v2s06 (structural) +0.50: gained payoff_letter__2026

**M3 → M8n:** 5 better, 0 worse, 15 unchanged

- v2c10 (chain) +0.50: gained negative_equity__2026
- v2s01 (structural) +1.00: gained appointment_checklist__2026, co_owners__2026
- v2s02 (structural) +0.29: gained appointment_checklist__2026, co_owners__2026
- v2s03 (structural) +0.50: gained odometer_problems__2022
- v2s06 (structural) +0.50: gained payoff_letter__2026

**M8n → M8:** 1 better, 0 worse, 19 unchanged

- v2c01 (chain) +0.33: gained epayoff_network__2026


### Wide step: share of gold articles in the pool, by source (M8 = all four, M8n = BM25 + vector)

| slice | n gold | BM25 | vector | graph | name | M8n pool (BM25 ∪ vector) | M8 pool (all) | M8 pool size | M8n pool size |
|---|---|---|---|---|---|---|---|---|---|
| all | 40 | 0.78 | 0.70 | 0.68 | 0.17 | 0.82 | 0.85 | 19.9 | 15.0 |
| chain | 23 | 0.87 | 0.83 | 0.87 | 0.22 | 0.87 | 0.91 | 19.5 | 14.5 |
| structural | 17 | 0.65 | 0.53 | 0.41 | 0.12 | 0.76 | 0.76 | 20.5 | 15.8 |
