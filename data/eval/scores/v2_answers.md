# Answer eval, gold v2

Mean over the runs, [lowest–highest run]. Facts: judged by Fable 5.2 by meaning. List items: from the answer's `items`, mapped to keys in code (D-035). KB-conflict article: v2c06/v2c07, where a current article still names a retired form. $ per answer: answer + judge, the cost of a shared RAG answer counted once per method.

| method | runs | facts found (20) | all facts (20) | facts, chain (12) | list items found (8) | list items correct (8) | exact list (8) | cites the KB-conflict article ↓ (2) | says not covered ↓ | tool calls | $ per answer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M3 Vector + filter | 3 | 0.64 [0.64–0.64] | 0.55 [0.55–0.55] | 0.82 [0.82–0.82] | 0.38 [0.38–0.38] | 0.38 [0.38–0.38] | 0.38 [0.38–0.38] | 1.00 [1.00–1.00] | 0.35 [0.35–0.35] | – | 0.023 [0.023–0.023] |
| M4 Graph: structural | 3 | 0.64 [0.63–0.66] | 0.57 [0.55–0.60] | 0.82 [0.81–0.85] | 0.38 [0.38–0.38] | 0.38 [0.38–0.38] | 0.38 [0.38–0.38] | 1.00 [1.00–1.00] | 0.43 [0.40–0.45] | – | 0.015 [0.015–0.015] |
| M7 Graph: + names | 3 | 0.64 [0.63–0.66] | 0.57 [0.55–0.60] | 0.82 [0.81–0.85] | 0.38 [0.38–0.38] | 0.38 [0.38–0.38] | 0.38 [0.38–0.38] | 1.00 [1.00–1.00] | 0.43 [0.40–0.45] | – | 0.000 [0.000–0.000] |
| M8 Wide -> narrow | 3 | 0.74 [0.72–0.75] | 0.63 [0.60–0.65] | 0.83 [0.81–0.85] | 0.60 [0.60–0.60] | 0.75 [0.75–0.75] | 0.50 [0.50–0.50] | 0.83 [0.50–1.00] | 0.33 [0.30–0.40] | – | 0.023 [0.022–0.023] |
| M8n Wide -> narrow, no graph | 3 | 0.74 [0.72–0.75] | 0.63 [0.60–0.65] | 0.83 [0.81–0.85] | 0.60 [0.60–0.60] | 0.75 [0.75–0.75] | 0.50 [0.50–0.50] | 0.83 [0.50–1.00] | 0.33 [0.30–0.40] | – | 0.001 [0.001–0.001] |
| M9s Agent: search only | 3 | 0.88 [0.88–0.88] | 0.85 [0.85–0.85] | 0.94 [0.94–0.94] | 0.79 [0.79–0.79] | 0.88 [0.88–0.88] | 0.75 [0.75–0.75] | 0.50 [0.50–0.50] | 0.15 [0.10–0.20] | 2.5 [2.5–2.5] | 0.034 [0.030–0.040] |
| M9 Agent: search + graph tools | 3 | 0.98 [0.97–0.98] | 0.95 [0.95–0.95] | 0.96 [0.94–0.97] | 1.00 [1.00–1.00] | 1.00 [1.00–1.00] | 1.00 [1.00–1.00] | 0.50 [0.50–0.50] | 0.03 [0.00–0.05] | 2.8 [2.7–2.8] | 0.031 [0.026–0.038] |

Answers: claude-opus-5-5 (effort medium). RAG: top 5 articles, text only. Agents: at most 8 tool calls, fixed AQL templates (`cookbook/tools.py`). Judge: Fable 5.2 (effort low).

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
