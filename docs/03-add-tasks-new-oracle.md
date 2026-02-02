# Add tasks + implement a custom oracle function

If existing oracles are not enough (e.g. you need parsing/stat/validation), extend `evaluator/oracles.py` and reference your oracle in task YAML.

This page provides a copy-paste template to add a new oracle and wire it into a task.

---

## Step 1: add a function to `evaluator/oracles.py`

### Oracle function rules

- Single entrypoint: `evaluator/oracles.py`
- Use keyword-only params and include `repo_root: Path`:

```python
def my_oracle(*, repo_root: Path, ...) -> Any:
    ...
```

- Return value must be **JSON-serializable** (int/str/bool/dict/list, etc.)
- For file walking/stats, prefer an `exclude_dirs` parameter and default to excluding `.git` and `eval_artifacts`

### Template example: total Python LOC under a directory

Add this to `evaluator/oracles.py`:

```python
from pathlib import Path
from typing import List, Optional
import os

def total_py_loc(*, repo_root: Path, under: str, exclude_dirs: Optional[List[str]] = None) -> int:
    exclude_dirs = exclude_dirs or [".git", "eval_artifacts"]
    base = (repo_root / under)
    if not base.exists():
        return 0
    total = 0
    for root, dirs, files in os.walk(base):
        # prune excluded dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = Path(root) / fn
            try:
                total += len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
            except Exception:
                continue
    return total
```

---

## Step 2: register it in `FN_REGISTRY`

Add one line to `FN_REGISTRY`:

```python
FN_REGISTRY["total_py_loc"] = total_py_loc
```

If you forget this, evaluation will fail with:

- `Unknown oracle fn: total_py_loc`

---

## Step 3: reference it from a task YAML

Create `tasks/l1/<repo_id>/task_XXX.yaml`:

```yaml
id: myrepo_task_011
repo: myrepo
difficulty: easy
initial_working_dir: .
instruction: >
  Compute total lines of Python code under my_package/ (recursive).
  Write to eval_artifacts/answer.json: {"py_loc": <int>}.
command_policy:
  allowed: [ls, cat, head, tail, wc, grep, rg, sed, python3]
  prohibited: [rm, sudo, curl, wget, ssh, scp]
  write_paths_allowed: [eval_artifacts/, /tmp/]
outputs:
  - key: py_loc
    type: int
    oracle:
      fn: total_py_loc
      args:
        under: my_package
        exclude_dirs: [".git", "eval_artifacts"]
max_commands: 12
timeout_seconds: 180
```

---

## Step 4: quick validation (recommended)

1) Run a dry-run to validate YAML and oracle registration

```bash
python3 -m evaluator.run --dry-run --repos myrepo
```

2) If you want to validate oracle output directly (faster), run a snippet:

```bash
python3 - <<'PY'
from pathlib import Path
from evaluator.oracles import compute_oracle
repo_root = Path("runs/<run_id>/work/repos/myrepo")  # 换成你实际 clone 的路径
print(compute_oracle(repo_root, "total_py_loc", {"under": "my_package", "exclude_dirs": [".git", "eval_artifacts"]}))
PY
```

---

## Tip: make tasks feel like real dev work

The goal of adding oracles is usually not “evaluation for evaluation’s sake”, but enabling tasks closer to real engineering workflows, such as:

- Parse metadata from `pyproject.toml` / `setup.cfg` (CI-style checks)
- Identify CLI entrypoints and summarize available commands/flags
- Validate repo conventions (e.g. `docs/` layout, `configs/` naming)

These are great fits for deterministic oracle-based scoring.

