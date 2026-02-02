# L1 Leaderboard（本地快照）

> **说明**：大模型输出具有非确定性（non-deterministic）。这些结果仅用于参考与模型/工具链优化，
> 不代表 AgentGym 对任何模型的主观看法。

- **models**: 5

| Model | 总体均分 | 总体成功率 | internlm 均分 | mmengine 均分 | opencompass 均分 | 安全违规/题（总数） |
|---|---|---|---|---|---|---|
| `gpt-5.2` | 100.00 | 100.00% | 100.00 | 100.00 | 100.00 | 0.00 (0) |
| `kimi-k2.5` | 83.49 | 86.67% | 94.55 | 85.17 | 70.75 | 0.43 (13) |
| `glm-4.7` | 77.14 | 76.67% | 87.88 | 71.57 | 71.97 | 0.30 (9) |
| `MiniMax-M2.1` | 75.53 | 76.67% | 69.67 | 80.00 | 76.92 | 0.53 (16) |
| `qwen3-vl-235b-a22b-instruct` | 52.17 | 46.67% | 54.17 | 55.83 | 46.50 | 0.37 (11) |

更详细的分 repo / 分 task 数据：
- [`l1-detailed-results.md`](l1-detailed-results.md)

本次快照对应的**完整评测产物**请见 `l1-eval` 分支：

- [`l1-eval` 分支的 `results/20260202/`](https://github.com/Abelmx/AgentGym/tree/l1-eval/results/20260202)
