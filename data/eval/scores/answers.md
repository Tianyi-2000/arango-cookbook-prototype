# Answer eval

Mean over the runs, with the lowest and highest run in brackets. facts and all facts: the 27 answerable questions. cites stale / cites trap: share of answers citing an outdated version or a trap article (lower is better). says not covered: answerable questions where the answer said the help center doesn't cover (part of) it, usually because retrieval missed an article (lower is better). declines: the 3 questions the help center doesn't fully cover.

| method | runs | facts found | all facts | says not covered | cites stale | cites trap | declines when not covered |
|---|---|---|---|---|---|---|---|
| M1 BM25 | 3 | 0.65 [0.64–0.66] | 0.53 [0.52–0.56] | 0.48 [0.48–0.48] | 0.16 [0.13–0.17] | 0.13 [0.13–0.13] | 1.00 [1.00–1.00] |
| M2 Vector | 3 | 0.82 [0.80–0.84] | 0.73 [0.70–0.78] | 0.35 [0.30–0.37] | 0.04 [0.03–0.07] | 0.19 [0.17–0.20] | 1.00 [1.00–1.00] |
| M3 Vector + filter | 3 | 0.84 [0.82–0.86] | 0.78 [0.74–0.81] | 0.31 [0.26–0.33] | 0.00 [0.00–0.00] | 0.19 [0.17–0.20] | 1.00 [1.00–1.00] |
| M4 Graph: structural | 3 | 0.85 [0.82–0.88] | 0.80 [0.74–0.85] | 0.30 [0.26–0.33] | 0.00 [0.00–0.00] | 0.19 [0.17–0.20] | 1.00 [1.00–1.00] |
| M5 Graph: semantic | 3 | 0.83 [0.80–0.84] | 0.75 [0.70–0.78] | 0.31 [0.26–0.33] | 0.00 [0.00–0.00] | 0.16 [0.13–0.17] | 1.00 [1.00–1.00] |
| M6 Graph: both layers | 3 | 0.85 [0.82–0.88] | 0.80 [0.74–0.85] | 0.30 [0.26–0.33] | 0.00 [0.00–0.00] | 0.19 [0.17–0.20] | 1.00 [1.00–1.00] |

Answers: claude-opus-5-5 (effort medium), top 5 articles, text only. Judge: claude-fable-5-2 (effort low).

Spend (ledger, from 2026-11-18):
```
  agent_M9               claude-opus-5-5     182 calls  $  1.24
  agent_M9s              claude-opus-5-5     164 calls  $  1.42
  agent_dev              claude-opus-5-5       3 calls  $  0.03
  answers                claude-opus-5-5     327 calls  $  3.51
  answers_v2             claude-opus-5-5     159 calls  $  2.07
  extract_semantic       claude-opus-5-5      68 calls  $  0.85
  judge                  claude-fable-5-2    606 calls  $  5.52
  total $14.63 of $50.00
```
