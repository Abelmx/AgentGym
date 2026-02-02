# AgentGym

AgentGym 是用于评测大语言模型（含多模态大模型）作为 **tool-based coding agent** 的“沙盒评测框架”。它把真实开发流程拆成一组可执行任务，让模型在受控环境里通过工具调用（例如终端命令、读写文件）完成任务，并由 Oracle 自动判分，产出可复现的报告与运行产物（artifacts）。

如果你是第一次接触本项目，你可以把它理解成：

- 你给 AgentGym 一个“待测模型” + 一批开源仓库（例如 OpenMMLab / InternLM）
- AgentGym 会在 GitHub Actions（或本地）里的受控环境内让模型执行一套任务
- 最终你会得到：**每个任务是否通过、得分、失败原因、终端日志、模型写出的文件**

---

## 你能用 AgentGym 做什么？

- **横向对比**：同一套任务对比多个模型/多个版本（成功率、得分、效率、安全违规）
- **回归监控**：模型升级后，哪些任务变好/变坏（适合持续评测）
- **工具接入评估**：模拟“模型 + 工具调用（tool calls）”的真实交互方式，关注模型操作 terminal 工作流能力

---

## L1 榜单（快照）

> **说明**：大模型输出具有非确定性（non-deterministic）。这些结果仅用于参考与模型/工具链优化，
> 不代表 AgentGym 对任何模型的主观看法。

| 模型 | 总体均分 | 总体成功率 | internlm 均分 | mmengine 均分 | opencompass 均分 | 安全违规/题（总数） |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-5.2` | 100.00 | 100.00% | 100.00 | 100.00 | 100.00 | 0.00 (0) |
| `kimi-k2.5` | 83.49 | 86.67% | 94.55 | 85.17 | 70.75 | 0.43 (13) |
| `glm-4.7` | 77.14 | 76.67% | 87.88 | 71.57 | 71.97 | 0.30 (9) |
| `MiniMax-M2.1` | 75.53 | 76.67% | 69.67 | 80.00 | 76.92 | 0.53 (16) |
| `qwen3-vl-235b-a22b-instruct` | 52.17 | 46.67% | 54.17 | 55.83 | 46.50 | 0.37 (11) |

更详细的分 repo / 分 task 数据：

- [`docs/benchmarks/zh-CN/l1-leaderboard.md`](docs/benchmarks/zh-CN/l1-leaderboard.md)
- [`docs/benchmarks/zh-CN/l1-detailed-results.md`](docs/benchmarks/zh-CN/l1-detailed-results.md)

本次快照对应的**完整评测产物**（可用于复核与二次统计）请见 `l1-eval` 分支：

- [`l1-eval` 分支的 `results/20260202/`](https://github.com/Abelmx/AgentGym/tree/l1-eval/results/20260202)

---

## 一次评测会发生什么？

1. 拉取需要评测的仓库（如 `opencompass/mmengine/internlm`）
2. 逐题运行：模型只能通过工具调用执行 terminal 命令、读取文件、写入答案
3. Oracle 自动判分：对照预定义规则计算期望结果，并判断模型输出是否匹配
4. 生成结果与产物：
   - `REPORT.md`：汇总报告（repo 维度、task 维度）
   - 每题 `*.json`：结构化结果
   - 每题 artifacts：模型写出的 `answer.json` / `answer.md` 等
5.（可选，推荐）在 GitHub Actions 中自动创建 PR，把结果写回到你指定的分支

---

## Quick Start（推荐：GitHub Actions；也支持本地运行）

### 方式 A：GitHub Actions（推荐，作为沙箱）

#### GitHub Actions 是什么？

GitHub Actions 是 GitHub 自带的自动化运行环境。你可以把它理解成“云端帮你跑脚本的 CI”：

- **在哪里看**：仓库页面顶部的 **Actions** 标签页
- **怎么触发**：手动点击 Run workflow（本项目用的是手动触发）
- **你能获得什么**：运行日志（每一步的输出）+ 可下载的 artifacts（本项目会打包评测产物）

#### 推荐用法：在独立分支上集中管理结果

为了保证你有权限创建分支/PR，并保持主分支清爽，建议按下面流程使用：

1. **Fork 本项目到你的 GitHub 账户**（在页面右上角点击 Fork）
2. 在你的 fork 仓库里新建一个分支（例如 `L1-Eval`）
3. 切到该分支后触发 GitHub Actions workflow（可以多次评测不同模型）
4. 每次运行都会创建一个 PR：**base = 触发 workflow 的分支**（例如 `L1-Eval`）  
   你可以在这个分支上集中审阅/合并所有评测结果

#### 配置 Secrets

在你 fork 出来的仓库中，进入 **Settings → Secrets and variables → Actions**，配置：

- `OPENAI_API_KEY`

#### 触发评测

在你的 fork 仓库中：

Actions → `l1-eval` → Run workflow：

- `model_name`：例如 `gpt-5.2`
- `base_url`：可选（OpenAI-compatible endpoint）
- `repos`：默认 `opencompass,mmengine,internlm`

#### 查看 artifacts（运行产物）

进入该次 workflow run 页面底部 **Artifacts**：

- 下载 `l1-eval-<model_name>`（包含 `results/` 与 `artifacts/`）

### 方式 B：本地运行（便于调试）

```bash
python3 -m pip install -r requirements.txt

# 可选：使用 .env（会被自动加载，不会提交到 git）
cp .env.example .env
# 编辑 .env：OPENAI_API_KEY / BASE_URL / MODEL_NAME

# Dry run：只拉 repo + 运行 oracle/评分流程（不调用模型）
python3 -m evaluator.run --dry-run --repos opencompass

# 实际评测
python3 -m evaluator.run --repos opencompass,mmengine --model "$MODEL_NAME" --base-url "$BASE_URL"
```

---

## 本地多模型并行评测（tmux）

如果你想在本地一次性跑多个模型（并行），推荐用 tmux 开多个窗口来管理每个模型的评测进程。

1. 复制一份配置模板：

```bash
cp tools/parallel_eval_config.example.json _local/parallel_eval_config.json
```

2. 编辑 `_local/parallel_eval_config.json`，通常你只需要改 `models[].model_id`（base_url/key/temperature/max_output_tokens 都可选覆盖）。

3. 启动 tmux 并行评测：

```bash
python3 tools/run_parallel_eval_tmux.py --config _local/parallel_eval_config.json --attach
```

---

## 下一步（深入使用 / 参与贡献）

如果你想把任意 GitHub repo 加入评测、扩展题库，或者贡献新的 oracle 判分函数，可以从下面 3 篇文档开始：

- [使用自定义 repos 评测](docs/zh-CN/01-custom-repos.md)
- [添加新 task（复用现有 oracle）](docs/zh-CN/02-add-tasks-existing-oracles.md)
- [添加新 task + 自定义 Oracle function](docs/zh-CN/03-add-tasks-new-oracle.md)
- [最佳实践：批量扩展 tasks & oracles（推荐用 AI-native 工具）](docs/zh-CN/04-best-practices-batch-tasks-oracles-with-ai.md)

---

## 输出结构（结果在哪里看？）

一次评测 run 的输出在 `runs/<model_id>-<run_id>/` 下：

- `results/REPORT.md`：汇总报告
- `results/<repo_id>/<task_id>.json`：每题结构化结果（包含 tool 调用日志、first_failure、得分）
- `artifacts/<repo_id>/<task_id>/answer.json|answer.md|task_result.json`：模型实际写出的文件（用于复核）

如果你用 GitHub Actions：

- 结果会以 PR 的形式写入 `results/<YYYYMMDD>/<model>/...`
- 运行产物（artifacts）可在 workflow run 页面下载

---

## 分数是怎么计算的？

每题都会有两个核心指标：

- **success**：是否满足该题所有 Oracle 断言（硬通过/不通过）
- **score_0_100**：综合分（考虑通过情况 + 效率 + 命令正确性 + 安全扣分）

你可以把综合分理解成：

- 通过题目会得到一部分“通过基础分”
- 即使没完全通过，也可能因为命令很少、命令都能正常执行而拿到一些分
- 如果触发了危险命令或越权写入，会被扣分

权重配置：`scoring/weights.yaml`（如果你希望强调“通过率”或“安全性”，可以调整这里）

---

## L1 阶段主要评测什么能力？

当前版本实现的是 **L1（MVP）**：最基础但最核心的 terminal 工作流能力。

主要衡量：

- **项目探索**：读 README、看目录结构、做统计、检索关键字
- **结果写入**：按题目要求把结果写到 `eval_artifacts/`
- **命令使用质量**：命令是否正确、是否高效
- **安全性**：是否尝试执行禁止命令或越权写文件

难度定位：**easy**（但能很好地反映“终端工具使用能力”的基本能力）。

---

## L1 题目列表（默认 10 题 / repo）

L1 默认题目由脚本生成（`scripts/generate_l1_tasks.py`），每个 repo 10 题：

1. 统计顶层可见条目数量（排除 `.git/`、`eval_artifacts/`）→ `answer.json`
2. 读取 README 首个非空行 → `answer.json`
3. 统计 Markdown 文件数量（递归）→ `answer.json`
4. 找到仓库内最大文件（路径+大小）→ `answer.json`
5. 统计 YAML 文件数量 → `answer.json`
6. 按固定规则统计 `pytest` token 次数（排除 `.git/`、`eval_artifacts/`）→ `answer.json`
7. 判断是否存在 LICENSE / LICENSE.md → `answer.json`
8. 统计 Python 文件数量 → `answer.json`
9. 统计 `docs/` 顶层条目数（不存在则 0）→ `answer.json`
10. 生成结构化摘要 `answer.md`（repo_id / top_level_entries / has_license）→ Oracle 校验

