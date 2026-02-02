# 添加新的 task（复用现有 oracle function）

本页介绍两种常见需求：

1. **只给某一个 repo 增加几道定制题**（推荐手写 YAML）
2. **升级“默认 L1 题库”**（让所有 repo 都批量生成包含新题）

---

## A. 只给某个 repo 定制新增 task（推荐）

### Step 1：新建 task YAML

在目录 `tasks/l1/<repo_id>/` 下新建 `task_011.yaml`（或任意未占用编号）。

一个最小可用的 task 包含：

- `instruction`：用户要模型做什么（明确输出格式）
- `command_policy`：允许/禁止命令、允许写路径
- `outputs`：定义 oracle 如何计算期望值，以及要从 `answer.json` 里取哪个 key

示例（统计 `docs/` 下 Markdown 文件数量）：

```yaml
id: opencompass_task_011
repo: opencompass
difficulty: easy
initial_working_dir: .
instruction: >
  Count how many markdown files exist under docs/ (recursive),
  excluding .git/ and eval_artifacts/. Write to eval_artifacts/answer.json:
  {"docs_md_count": <int>}.
command_policy:
  allowed: [ls, cat, head, tail, wc, grep, rg, sed, python3]
  prohibited: [rm, sudo, curl, wget, ssh, scp]
  write_paths_allowed: [eval_artifacts/, /tmp/]
outputs:
  - key: docs_md_count
    type: int
    oracle:
      fn: glob_count
      args:
        glob: docs/**/*.md
        exclude_dirs: [".git", "eval_artifacts"]
max_commands: 12
timeout_seconds: 180
```

### Step 2：运行验证

```bash
python3 -m evaluator.run --repos opencompass --runs-root ~/sandbox/runs --dry-run
```

> dry-run 不会调用模型，但会把 repo 拉下来，并跑完整的“任务加载 → oracle → 评分”流程。  
> 对新增题来说，dry-run 会失败（因为没有模型写 `answer.json`），但你可以先确认“不会报 Unknown oracle fn / YAML 解析错误”。

---

## B. 批量扩展默认 L1 题库（所有 repo 一起升级）

如果你的新题是“通用题”（大多数 repo 都适用），你可以把它加入生成脚本：

- `scripts/generate_l1_tasks.py` 里的 `DEFAULT_TASKS`

然后对所有 repo 重新生成：

```bash
python3 scripts/generate_l1_tasks.py --repo-id opencompass --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id mmengine --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id internlm --repo-root .
```

### 什么时候应该用 generator？

- 你希望“每个 repo 都有同样结构的一套题”
- 你希望维护成本低（改一处，批量更新）

### 什么时候不该用 generator？

- 题目强依赖某个 repo 的目录结构/入口脚本
- 题面里包含 repo-specific 的路径或约束

这种更适合手写 `tasks/l1/<repo_id>/task_*.yaml`。

---

## 复用现有 oracle：我能用哪些 fn？

所有 oracle 都在：

- `evaluator/oracles.py`（并通过 `FN_REGISTRY` 注册）

你可以先从现有函数开始复用（例如 `glob_count`, `largest_file`, `repo_token_count`, `dir_top_entry_count`, `has_license_file` 等）。

> 建议：统计类题目尽量排除 `.git/` 与 `eval_artifacts/`，避免结果被评测过程污染。

