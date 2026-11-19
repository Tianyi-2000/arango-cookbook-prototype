# Retrieval scores

Run 2026-11-18T17:17:59 · commit 284abe1 · gold sha256 5935c443e31e · k=10, entries=5, decay=0.8

### Headline (higher is better, except stale and trap)

| method | recall@5 · all (n=27) | recall@10 · all (n=27) | recall@5 · multi_hop + checklist (n=12) | all_gold@5 · multi_hop + checklist (n=12) | mrr@10 · all (n=27) | ndcg@5 · all (n=27) | stale@5 · all (n=27) | trap@5 · all (n=27) |
|---|---|---|---|---|---|---|---|---|
| M1 BM25 | 0.63 | 0.75 | 0.50 | 0.25 | 0.69 | 0.58 | 0.78 | 0.26 |
| M2 Vector | 0.77 | 0.84 | 0.66 | 0.42 | 0.73 | 0.68 | 0.78 | 0.41 |
| M3 Vector + filter | 0.80 | 0.88 | 0.71 | 0.50 | 0.79 | 0.74 | 0.00 | 0.37 |
| M4 Graph: structural | 0.80 | 0.88 | 0.72 | 0.50 | 0.79 | 0.74 | 0.00 | 0.37 |
| M5 Graph: semantic | 0.80 | 0.88 | 0.71 | 0.50 | 0.79 | 0.74 | 0.00 | 0.33 |
| M6 Graph: both layers | 0.80 | 0.88 | 0.72 | 0.50 | 0.79 | 0.74 | 0.00 | 0.37 |

### Recall@5 by question type

| type | n | M1 | M2 | M3 | M4 | M5 | M6 |
|---|---|---|---|---|---|---|---|
| exact | 3 | 1.00 | 0.67 | 0.67 | 0.67 | 0.67 | 0.67 |
| semantic | 3 | 0.33 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| multi_hop | 7 | 0.60 | 0.79 | 0.83 | 0.90 | 0.83 | 0.90 |
| temporal | 5 | 0.80 | 0.80 | 0.80 | 0.80 | 0.80 | 0.80 |
| conditional | 4 | 0.75 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| checklist | 5 | 0.37 | 0.47 | 0.54 | 0.47 | 0.54 | 0.47 |

### Per question: where each step changed Recall@5

**M1 → M2:** 8 better, 2 worse, 17 unchanged

- q10 (semantic) +1.00: gained inherited_car__2026
- q16 (semantic) +1.00: gained toll_tags_personal_data__2022
- q19 (multi_hop) +1.00: gained epayoff_network__2026, payoff_letter__2026
- q21 (multi_hop) +0.33: gained epayoff_network__2026
- q23 (multi_hop) +0.33: gained selling_with_loan__2022
- q36 (conditional) +1.00: gained home_pickup__2026
- q41 (checklist) +0.20: gained inherited_car__2026
- q42 (checklist) +0.33: gained leased_car__2022
- q04 (exact) -1.00: lost lien_still_on_title__2022
- q24 (multi_hop) -0.33: gained inherited_car__2026; lost epayoff_network__2026, selling_with_loan__2022

**M2 → M3:** 2 better, 0 worse, 25 unchanged

- q24 (multi_hop) +0.33: gained selling_with_loan__2022
- q42 (checklist) +0.33: gained appointment_checklist__2026

**M3 → M4:** 1 better, 1 worse, 25 unchanged

- q22 (multi_hop) +0.50: gained offer_validity__2026; path: offer_validity__2026 via duplicate_title_north_carolina__2022 > offer_validity__2026
- q42 (checklist) -0.33: lost leased_car__2022

**M3 → M5:** 0 better, 0 worse, 27 unchanged


**M3 → M6:** 1 better, 1 worse, 25 unchanged

- q22 (multi_hop) +0.50: gained offer_validity__2026; path: offer_validity__2026 via duplicate_title_north_carolina__2022 > offer_validity__2026
- q42 (checklist) -0.33: lost leased_car__2022

