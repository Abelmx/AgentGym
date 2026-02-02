# 添加新的 task + 实现自定义 Oracle function

当现有 oracle 不够用（例如你想做更复杂的解析/统计/验证），你可以扩展 `evaluator/oracles.py` 并在 task YAML 中引用它。

本页会给一个可复制的模板，帮助你快速新增 oracle 并写入 task。

---

## Step 1：在 `evaluator/oracles.py` 新增函数

### Oracle 函数的基本规则

- 统一入口：`evaluator/oracles.py`
- 函数签名使用 keyword-only 参数，并包含 `repo_root: Path`：

```python
def my_oracle(*, repo_root: Path, ...) -> Any:
    ...
```

- 返回值必须是**可 JSON 序列化**的类型（int/str/bool/dict/list 等）
- 如果是统计/遍历文件，建议支持 `exclude_dirs`，并默认排除 `.git`、`eval_artifacts`

### 模板示例：统计某目录下 `.py` 文件总行数

在 `evaluator/oracles.py` 添加：

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

## Step 2：注册到 `FN_REGISTRY`

在 `evaluator/oracles.py` 底部的 `FN_REGISTRY` 里加入一行：

```python
FN_REGISTRY["total_py_loc"] = total_py_loc
```

如果你忘了这一步，评测会报：

- `Unknown oracle fn: total_py_loc`

---

## Step 3：在 task YAML 中引用新 oracle

新增 `tasks/l1/<repo_id>/task_XXX.yaml`：

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

## Step 4：快速自检（推荐）

1) 先跑一次 dry-run（验证 oracle 名称与 YAML 格式）

```bash
python3 -m evaluator.run --dry-run --repos myrepo
```

2) 如果你想直接验证 oracle 输出是否如预期（更快），可以在本地跑一个小 snippet：

```bash
python3 - <<'PY'
from pathlib import Path
from evaluator.oracles import compute_oracle
repo_root = Path("runs/<run_id>/work/repos/myrepo")  # 换成你实际 clone 的路径
print(compute_oracle(repo_root, "total_py_loc", {"under": "my_package", "exclude_dirs": [".git", "eval_artifacts"]}))
PY
```

---

## 建议：让题目“更像真实开发任务”

新增 oracle 的目的通常不是“为了评测而评测”，而是让任务更贴近真实工程场景，例如：

- 从 `pyproject.toml/setup.cfg` 解析项目元信息并输出（类似 CI 检查）
- 从 CLI 入口文件解析可用命令/参数并汇总成结构化说明
- 检查某目录是否满足约定（例如 `docs/` 结构、`configs/` 命名规则）

这些都适合用 oracle 做确定性判分。

