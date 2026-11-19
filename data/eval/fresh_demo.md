# Freshness demo transcript (`make fresh`)

```text
Building northwind_kb_demo from data/ (a copy; the eval database is not touched)
kb_view commitIntervalMsec = 1000 (BM25 queries below use waitForSync, so they see a commit immediately)

Question (asked 2026-11-01): "How will you pay me for my car, and how long does it take?"

### 1. Before the policy change
| method | #1 | getting_paid versions in the top 5 |
|---|---|---|
| M1 BM25 | `how_selling_works__2026` current | none |
| M2 Vector | `getting_paid__2022` **STALE** | #1 `getting_paid__2022` **STALE** |
| M3 Vector + filter | `how_selling_works__2026` current | #4 `getting_paid__2026` current |
| M4 Graph: structural | `how_selling_works__2026` current | #4 `getting_paid__2026` current |
| M5 Graph: semantic | `how_selling_works__2026` current | #4 `getting_paid__2026` current |
| M6 Graph: both layers | `how_selling_works__2026` current | #4 `getting_paid__2026` current |
| M7 Graph: + names | `how_selling_works__2026` current | #4 `getting_paid__2026` current |
| M8 Wide -> narrow | `buy_title_northwind_finance__2022` current | #2 `getting_paid__2026` current |
| M8n Wide -> narrow, no graph | `buy_title_northwind_finance__2022` current | #2 `getting_paid__2026` current |

### 2. The policy changes: one stream transaction
AQL> INSERT @doc INTO articles RETURN NEW._key
bind: {'doc': {'_key': 'getting_paid__2026-11', 'doc_id': 'getting_paid', 'version': '2026-11', 'kind': 'rewritten', 'effective_from': '2026-11-01', 'effective_to': None, 'states': [], 'side': 'sell', 'section': 'loans', 'title': 'When and how you get paid', 'text': 'Once the paperwork is signed, we pay you by bank draft or by instant transfer to your bank account, which arrives within minutes on any day of the week. Dire...', 'codes': [], 'embedding': '<384 floats>'}}
inserted: ['getting_paid__2026-11']
AQL> UPDATE @key WITH { effective_to: @closed } IN articles RETURN { key: NEW._key, effective_to: NEW.effective_to }
bind: {'key': 'getting_paid__2026', 'closed': '2026-10-31'}
closed:   [{'key': 'getting_paid__2026', 'effective_to': '2026-10-31'}]
AQL> INSERT { _from: @new, _to: @old, on: @on } INTO supersedes RETURN CONCAT(NEW._from, " supersedes ", NEW._to)
bind: {'new': 'articles/getting_paid__2026-11', 'old': 'articles/getting_paid__2026', 'on': '2026-11-01'}
edge:     ['articles/getting_paid__2026-11 supersedes articles/getting_paid__2026']
links_to: ['articles/epayoff_network__2026', 'articles/home_pickup__2022', 'articles/home_pickup__2026', 'articles/keep_paying_until_confirmed__2022', 'articles/lender_overpayment_refund__2022'] (parsed from the new text)
AQL> FOR e IN links_to
       FILTER e._to == @old
       INSERT { _from: e._from, _to: @new, doc_id: e.doc_id } INTO links_to
       RETURN NEW._from
bind: {'old': 'articles/getting_paid__2026', 'new': 'articles/getting_paid__2026-11'}
re-linked: ['articles/how_selling_works__2022', 'articles/how_selling_works__2026', 'articles/home_pickup__2026', 'articles/selling_with_loan__2022', 'articles/business_car__2022']

embedding the new version: 19 ms · transaction: 22 ms · nothing re-indexed

### 3. The same question, right after the commit
| method | #1 | getting_paid versions in the top 5 |
|---|---|---|
| M1 BM25 | `how_selling_works__2026` current | none |
| M2 Vector | `getting_paid__2022` **STALE** | #1 `getting_paid__2022` **STALE** |
| M3 Vector + filter | `how_selling_works__2026` current | #5 `getting_paid__2026-11` current |
| M4 Graph: structural | `how_selling_works__2026` current | #5 `getting_paid__2026-11` current |
| M5 Graph: semantic | `how_selling_works__2026` current | #5 `getting_paid__2026-11` current |
| M6 Graph: both layers | `how_selling_works__2026` current | #5 `getting_paid__2026-11` current |
| M7 Graph: + names | `how_selling_works__2026` current | #5 `getting_paid__2026-11` current |
| M8 Wide -> narrow | `buy_title_northwind_finance__2022` current | #2 `getting_paid__2026-11` current |
| M8n Wide -> narrow, no graph | `buy_title_northwind_finance__2022` current | #2 `getting_paid__2026-11` current |

(every method after the commit: 429 ms)

### 4. What the current answer replaced: walk `supersedes`
AQL> FOR v, e IN 0..5 OUTBOUND @start supersedes
       RETURN { version: v._key, in_effect: CONCAT(v.effective_from, " to ", v.effective_to || "now"), replaced_it_on: e.on }
bind: {'start': 'articles/getting_paid__2026-11'}
   {'version': 'getting_paid__2026-11', 'in_effect': '2026-11-01 to now', 'replaced_it_on': None}
   {'version': 'getting_paid__2026', 'in_effect': '2026-02-01 to 2026-10-31', 'replaced_it_on': '2026-11-01'}
   {'version': 'getting_paid__2022', 'in_effect': '2022-01-01 to 2026-01-31', 'replaced_it_on': '2026-02-01'}
```
