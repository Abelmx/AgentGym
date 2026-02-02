# 使用自定义 repos 评测

本页介绍如何把 GitHub 上**任意公开仓库**作为 AgentGym 的数据源来评测。

---

## 你需要准备什么？

- 一个 repo 的 **git URL**（例如 `https://github.com/OWNER/REPO.git`）
- 一个 **ref**（分支/标签/commit sha，例如 `main` / `v1.2.3` / `a1b2c3...`）
- 一个你自定义的 `repo_id`（建议短、可读、全小写，比如 `myrepo`）

---

## Step 1：在 `repos/` 下新增 repo 配置

新增文件：`repos/<repo_id>.yaml`

示例：

```yaml
id: myrepo
url: https://github.com/OWNER/REPO.git
ref: main
initial_working_dir: .
```

字段说明：

- **id**：repo 的唯一标识（后续 `--repos` 参数、任务目录名都用它）
- **url**：git clone 的地址
- **ref**：分支/标签/commit sha
- **initial_working_dir**：保留字段（当前 L1 默认从 repo 根目录开始）

---

## Step 2：为该 repo 准备 L1 tasks（使用项目默认 L1 题库）

运行：

```bash
python3 scripts/generate_l1_tasks.py --repo-id myrepo --repo-root .
```

会生成：

- `tasks/l1/myrepo/task_001.yaml ... task_010.yaml`

你可以先用这套“通用 L1 题”跑通流程，然后再针对该 repo 做定制题（见后续文档）。

---

## Step 3：运行评测

本地运行：

```bash
python3 -m evaluator.run --repos myrepo --runs-root ~/sandbox/runs
```

如果你要显式指定模型/网关：

```bash
python3 -m evaluator.run --repos myrepo --runs-root ~/sandbox/runs --model "$MODEL_NAME" --base-url "$BASE_URL"
```

---

## 常见问题 / 注意事项

### 1) 目前仅支持公开仓库（Public GitHub repos）

当前实现通过 `git clone <url>` 拉取 repo，**不包含私有仓库鉴权**。

如果你要测私有仓库，通常有两种做法（未来可以在 AgentGym 内集成）：

- **GitHub Actions**：用 `actions/checkout` 配合 `token` 或 deploy key
- **本地**：提前配置好 git 凭据（例如 `~/.git-credentials` 或 ssh key）

### 2) 默认任务可能不适配所有 repo

例如目标 repo 没有 `README.md` 或没有 `docs/`，默认某些题会天然失败。

处理方式：

- 删除/替换这些 task（直接改 `tasks/l1/<repo_id>/task_*.yaml`）
- 或者扩展 generator（见后续文档）

### 3) 建议把 `eval_artifacts/` 从统计类题目中排除

因为 runner 会创建 `eval_artifacts/`，如果你的统计类 oracle 不排除它，会导致“模型写入答案反过来影响统计结果”。

