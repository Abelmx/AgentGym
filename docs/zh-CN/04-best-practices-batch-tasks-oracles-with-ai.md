# 最佳实践：批量扩展 tasks & oracles（推荐用 AI-native 工具）

当你准备为 AgentGym 批量增加题目（tasks）并实现对应判分逻辑（oracles）时，推荐把它当作一个“工程交付”来做：**需求定义清晰 → 小步实现 → 多模型交叉验证 → 批量生成 YAML → 复跑验证**。

本页给出一个社区贡献者容易上手、且能最大化客观正确性的工作流。

---

## 为什么推荐用 Cursor / Claude Code 这类 AI-native 工具？

因为新增 tasks/oracles 往往需要：

- 在多个文件间改动（新增/修改 `tasks/`、`scripts/`、`evaluator/oracles.py`）
- 快速跑 dry-run / 计算 oracle 输出做 sanity check
- 迭代修订题面，避免歧义、避免被 `eval_artifacts/` 污染

AI-native 工具非常适合把这些重复劳动压缩掉，让贡献者更专注于“题目是否合理、判分是否客观”。

---

## 重要提醒（请务必遵守）

- **使用 SOTA 模型写 oracle**  
  oracle 函数直接影响评测是否客观正确，建议至少使用：`gpt-5.2` / `claude-4.5-sonnet` / `gemini-3.0-pro` 及以上级别模型来辅助编写与审阅。

- **用不同模型交叉验证 oracle 输出**  
  不要只相信一个模型写出来的 oracle。最少做一次交叉验证：  
  用 2 个不同体系的模型（例如 `gpt-5.2` 和 `gemini-3.0-pro`）分别写出 oracle（或分别复核同一 oracle），并在多个 repos 上跑 oracle，确保输出一致或差异可解释。

- **把“无歧义”写进题面**  
  任何统计类题目（文件数量、token 计数、largest file 等）都必须明确：  
  - 排除哪些目录（建议固定排除 `.git/`、`eval_artifacts/`）  
  - 编码/二进制判断/文件大小阈值（必要时写死）  
  - 输出格式（写入 `answer.json` 的 key 名，或 `answer.md` 的固定字段）

---

## 推荐工作流（批量扩展）

### Step 0：选定扩展策略

你要做的是：

- **A. 只给某一个 repo 增加定制题**（手写 `tasks/l1/<repo_id>/task_*.yaml`）
- **B. 扩展“默认 L1 题库”让所有 repo 都生成新增题**（改 `scripts/generate_l1_tasks.py`）

批量扩展通常走 B。

---

### Step 1：先写题面草案（只写规则，不写实现）

建议先把每道题写成 4 行即可：

- 任务目标（用户要回答什么）
- 输入范围（哪些目录/文件，排除哪些目录）
- 计算规则（编码/阈值/边界条件）
- 输出格式（写到 `eval_artifacts/answer.json` 的 key 或 `answer.md` 的字段）

---

### Step 2：实现/扩展 oracle（并注册到 `FN_REGISTRY`）

实现位置：

- `evaluator/oracles.py`

新增函数并注册后，用一个小脚本在**多个 repos**上试跑它（见 Step 4）。

---

### Step 3：把题目落到 generator 或 YAML

如果是批量默认题库：

- 修改 `scripts/generate_l1_tasks.py` 的 `DEFAULT_TASKS`
- 然后对所有 repo 重新生成：

```bash
python3 scripts/generate_l1_tasks.py --repo-id opencompass --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id mmengine --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id internlm --repo-root .
```

---

### Step 4：多模型交叉验证 oracle 输出（关键！）

建议的最小验证方式（不跑完整评测也行）：

1) 让 evaluator 先 clone 两三个 repo（可以 dry-run）：

```bash
python3 -m evaluator.run --dry-run --repos opencompass,mmengine --runs-root ~/sandbox/runs
```

2) 在 clone 出来的 repo_root 上分别计算 oracle 输出，确认一致性。

> 如果输出在不同 repos 上不一致，优先检查：  
> `.git/` 与 `eval_artifacts/` 是否排除；编码规则是否一致；是否存在大文件截断。

---

## 给新用户的“Agent 指令参考”（可直接复制到 Cursor/Claude Code）

```text
你现在在 AgentGym 仓库根目录。

目标：为 repo_id=<repo_id> 扩展 2 道新的 L1 任务，并保证判分客观正确。

约束：
- 任务必须把答案写入 eval_artifacts/answer.json 或 eval_artifacts/answer.md
- 统计类任务必须排除 .git/ 与 eval_artifacts/
- 不要引入网络访问、不要修改评测框架的安全策略

任务 A（复用现有 oracle）：新增 tasks/l1/<repo_id>/task_011.yaml
- 题目要求：<写清楚规则与输出 key>
- oracle：优先复用 evaluator/oracles.py 里已有的函数

任务 B（需要新增 oracle）：新增 tasks/l1/<repo_id>/task_012.yaml，并在 evaluator/oracles.py 中新增 oracle fn
- oracle fn 名称：<your_oracle_fn_name>
- 请实现函数、注册到 FN_REGISTRY，并写一个最小的本地验证方式（在 opencompass/mmengine 两个 repo 上跑一遍，确保结果合理）

最后：
- 重新运行 scripts/generate_l1_tasks.py（如果你改了 generator）
- 给出你新增/修改的文件列表
- 给出一段“如何本地 dry-run 验证不会报 Unknown oracle fn”的命令
```

