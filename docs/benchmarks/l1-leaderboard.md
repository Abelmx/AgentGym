# L1 Leaderboard (local snapshot)

> **Important**: LLM outputs are non-deterministic. Results are **for reference and model/tooling optimization only**,
> and should not be interpreted as AgentGym’s subjective judgement of any model.

- **models**: 5

| Model | Avg Score (overall) | Avg Success Rate (overall) | Avg Score (internlm) | Avg Score (mmengine) | Avg Score (opencompass) | Safety / task (total) |
|---|---|---|---|---|---|---|
| `gpt-5.2` | 100.00 | 100.00% | 100.00 | 100.00 | 100.00 | 0.00 (0) |
| `kimi-k2.5` | 83.49 | 86.67% | 94.55 | 85.17 | 70.75 | 0.43 (13) |
| `glm-4.7` | 77.14 | 76.67% | 87.88 | 71.57 | 71.97 | 0.30 (9) |
| `MiniMax-M2.1` | 75.53 | 76.67% | 69.67 | 80.00 | 76.92 | 0.53 (16) |
| `qwen3-vl-235b-a22b-instruct` | 52.17 | 46.67% | 54.17 | 55.83 | 46.50 | 0.37 (11) |

See detailed per-repo / per-task breakdown:
- [`l1-detailed-results.md`](l1-detailed-results.md)

Full raw evaluation artifacts for this snapshot are available on the `l1-eval` branch:

- [`results/20260202/` on `l1-eval`](https://github.com/Abelmx/AgentGym/tree/l1-eval/results/20260202)
