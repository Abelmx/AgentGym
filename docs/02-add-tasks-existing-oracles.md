# Add tasks (using existing oracle functions)

This page covers two common workflows:

1. **Add a few repo-specific tasks** (recommended: write YAML directly)
2. **Upgrade the default L1 task set** (batch-generate tasks for all repos)

---

## A. Add repo-specific tasks (recommended)

### Step 1: create a new task YAML

Create `task_011.yaml` (or any unused number) under `tasks/l1/<repo_id>/`.

A minimal task includes:

- `instruction`: what the agent should do (be explicit about output format)
- `command_policy`: allowed/prohibited commands and allowed write paths
- `outputs`: how oracle computes expected outputs, and which key to read from `answer.json`

Example (count markdown files under `docs/`):

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

### Step 2: validate the spec

```bash
python3 -m evaluator.run --repos opencompass --runs-root ~/sandbox/runs --dry-run
```

> `--dry-run` does not call the model. It still clones repos and executes the full “load tasks → compute oracle → score” pipeline.  
> For a new task, dry-run will usually fail (no model writes `answer.json`), but it ensures there is no YAML parsing error and no “Unknown oracle fn”.

---

## B. Batch-upgrade the default L1 task set (all repos)

If your task is “generic” (works for most repos), add it to:

- `scripts/generate_l1_tasks.py` 里的 `DEFAULT_TASKS`

Then regenerate for each repo:

```bash
python3 scripts/generate_l1_tasks.py --repo-id opencompass --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id mmengine --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id internlm --repo-root .
```

### When to use the generator

- You want the same task set structure for every repo
- You want low maintenance (one change, regenerate everywhere)

### When not to use the generator

- Tasks strongly depend on a specific repo layout/entrypoint
- Repo-specific paths or constraints are required

In those cases, write YAML directly under `tasks/l1/<repo_id>/`.

---

## Which oracle functions can I reuse?

All oracles live in:

- `evaluator/oracles.py`（并通过 `FN_REGISTRY` 注册）

Start by reusing existing functions such as `glob_count`, `largest_file`, `repo_token_count`, `dir_top_entry_count`, `has_license_file`, etc.

> Tip: for stats tasks, always exclude `.git/` and `eval_artifacts/` to avoid contaminating ground truth.

