# Evaluate custom repos

This page explains how to use **any public GitHub repository** as a data source in AgentGym.

---

## What you need

- A repo **git URL** (e.g. `https://github.com/OWNER/REPO.git`)
- A **ref** (branch/tag/commit sha, e.g. `main` / `v1.2.3` / `a1b2c3...`)
- A `repo_id` you choose (short and readable, e.g. `myrepo`)

---

## Step 1: add a repo entry under `repos/`

Create `repos/<repo_id>.yaml`:

示例：

```yaml
id: myrepo
url: https://github.com/OWNER/REPO.git
ref: main
initial_working_dir: .
```

Field notes:

- **id**: the repo identifier used by `--repos` and task folder names
- **url**: git clone URL
- **ref**: branch/tag/commit sha
- **initial_working_dir**: reserved; L1 currently starts at repo root

---

## Step 2: generate a default L1 task set for this repo

运行：

```bash
python3 scripts/generate_l1_tasks.py --repo-id myrepo --repo-root .
```

This generates:

- `tasks/l1/myrepo/task_001.yaml ... task_010.yaml`

Start with this default set to validate the pipeline, then customize tasks for the repo if needed.

---

## Step 3: run an evaluation

Local run:

```bash
python3 -m evaluator.run --repos myrepo --runs-root ~/sandbox/runs
```

If you want to explicitly specify model / gateway:

```bash
python3 -m evaluator.run --repos myrepo --runs-root ~/sandbox/runs --model "$MODEL_NAME" --base-url "$BASE_URL"
```

---

## Notes & limitations

### 1) Public repos only (for now)

AgentGym uses `git clone <url>` and currently does **not** include private-repo authentication.

For private repos, common options (not yet integrated) are:

- **GitHub Actions**: `actions/checkout` with a token or deploy key
- **Local**: configure git credentials (e.g. `~/.git-credentials` or SSH keys)

### 2) Default tasks may not fit every repo

If the repo has no `README.md` or no `docs/`, some default tasks will fail by design.

Options:

- delete/replace tasks under `tasks/l1/<repo_id>/task_*.yaml`
- or extend the generator (see other docs)

### 3) Always exclude `eval_artifacts/` in stats tasks

The runner creates `eval_artifacts/`. If your oracle counts it, the model’s outputs can contaminate the ground truth.

