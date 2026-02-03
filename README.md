# AgentGym

AgentGym is a **sandbox evaluation framework** for measuring large language models (including mLLMs) as **tool-based coding agents**.
It turns real developer workflows into executable tasks, runs them in a controlled environment (GitHub Actions or local), and uses deterministic **oracles** to score results and produce reproducible artifacts.

- Chinese README: [`README_zh-CN.md`](README_zh-CN.md)
- Docs (EN): [`docs/README.md`](docs/README.md)
- Docs (中文): [`docs/zh-CN/README.md`](docs/zh-CN/README.md)

---

## What you can do with AgentGym

- **Compare models**: success rate, scores, efficiency, safety violations, and failure reasons
- **Track regressions**: detect changes across model versions
- **Evaluate tool integration**: measure the core “tool-call loop” behind AI-native coding tools (Claude Code / Cursor / OpenCode, etc.)

---

## What happens in one evaluation run (high level)

![AgentGym overview](docs/assets/agentgym_intro.png)

1. Clone target repos (e.g. `opencompass`, `mmengine`, `internlm`)
2. Run tasks one by one: the model acts via tool calls (terminal/file operations)
3. Oracle computes expected outputs and scores the model’s outputs
4. Produce results and artifacts (reports, per-task JSON, model-written `answer.json`/`answer.md`)
5. (Recommended) In GitHub Actions, open a PR to write results back to your chosen branch

<details>
<summary><strong>Example (single task): Task spec (instruction + command policy)</strong></summary>

From one L1 task (`mmengine_task_001`):

```json
{
  "id": "mmengine_task_001",
  "repo": "mmengine",
  "instruction": "Count the number of visible (non-dot) top-level entries in the repo root, excluding `.git/` and `eval_artifacts/` if present. This should match what you would see from `ls -1` after removing `eval_artifacts`. Write to eval_artifacts/answer.json: {\"top_level_entries\": <int>} .",
  "command_policy": {
    "allowed": ["ls", "pwd", "cd", "cat", "head", "tail", "wc", "grep", "rg", "sed", "python", "python3", "pytest"],
    "prohibited": ["rm", "sudo", "curl", "wget", "ssh", "scp", "dd", "mkfs", "mount", "umount", "chmod", "chown"],
    "write_paths_allowed": ["eval_artifacts/", "/tmp/"]
  }
}
```

</details>

<details>
<summary><strong>Example: Tools available in the sandbox (OpenAI tools format)</strong></summary>

AgentGym exposes a small tool surface (OpenAI tool schema style):

```json
[
  {
    "type": "function",
    "function": {
      "name": "run_command",
      "description": "Run a terminal command in the repo workspace.",
      "parameters": {
        "type": "object",
        "properties": {
          "command": { "type": "string", "description": "Shell command to run." },
          "cwd": { "type": "string", "description": "Working directory relative to repo root.", "nullable": true },
          "timeout_seconds": { "type": "integer", "description": "Timeout for this command.", "nullable": true }
        },
        "required": ["command"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_file",
      "description": "Read a UTF-8 text file under the repo root.",
      "parameters": {
        "type": "object",
        "properties": { "path": { "type": "string" }, "max_bytes": { "type": "integer", "nullable": true } },
        "required": ["path"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "list_dir",
      "description": "List directory entries under the repo root.",
      "parameters": { "type": "object", "properties": { "path": { "type": "string" } }, "required": ["path"] }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "write_file",
      "description": "Write a UTF-8 text file. Only allowed under eval_artifacts/ or /tmp/.",
      "parameters": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "content": { "type": "string" },
          "mode": { "type": "string", "enum": ["overwrite", "append"], "nullable": true }
        },
        "required": ["path", "content"]
      }
    }
  }
]
```

</details>

<details>
<summary><strong>Example (same task): Oracle spec + oracle function</strong></summary>

This task’s expected output is computed by an oracle:

```json
{
  "key": "top_level_entries",
  "oracle": {
    "fn": "top_level_entry_count",
    "args": { "exclude": [".git", "eval_artifacts"], "exclude_hidden": true }
  }
}
```

Oracle function (implementation sketch):

```python
def top_level_entry_count(*, repo_root: Path, exclude: Optional[List[str]] = None, exclude_hidden: bool = True) -> int:
    exclude = exclude or []
    names = []
    for p in repo_root.iterdir():
        if p.name in exclude:
            continue
        if exclude_hidden and p.name.startswith("."):
            continue
        names.append(p.name)
    return len(names)
```

</details>

<details>
<summary><strong>Example (gpt-5.2): Prompt messages + tool calls</strong></summary>

We record the exact OpenAI-style `messages` used to start the task, plus the executed `tool_calls`.

```json
{
  "prompt_messages": [
    { "role": "system", "content": "<system prompt...>" },
    { "role": "user", "content": "Repo: mmengine\\nTask: mmengine_task_001\\n\\nInstruction: ...\\n\\nCommand policy: ..." }
  ],
  "tool_calls": [
    { "tool_name": "run_command", "tool_input": { "command": "ls -1" } },
    { "tool_name": "run_command", "tool_input": { "command": "python3 - <<'PY' ... PY" } },
    { "tool_name": "write_file", "tool_input": { "path": "eval_artifacts/answer.json", "mode": "overwrite" } }
  ]
}
```

</details>

---

## L1 leaderboard (snapshot)

> **Important**: LLM outputs are non-deterministic. Results are **for reference and model/tooling optimization only**,
> and should not be interpreted as AgentGym’s subjective judgement of any model.

> `gpt-5.2` is a **closed-source reference baseline** here (an “ideal output” target to sanity-check the evaluation design).

| Model | Avg Score | Avg Success Rate | Avg Commands / task | Safety / task (total) |
|---|---:|---:|---:|---:|
| `gpt-5.2` (closed-source reference) | 100.00 | 100.00% | 1.00 | 0.00 (0) |
| `kimi-k2.5` | 83.49 | 86.67% | 2.03 | 0.43 (13) |
| `glm-4.7` | 77.14 | 76.67% | 2.93 | 0.30 (9) |
| `MiniMax-M2.1` | 75.53 | 76.67% | 2.03 | 0.53 (16) |
| `qwen3-vl-235b-a22b-instruct` | 52.17 | 46.67% | 1.57 | 0.37 (11) |

Detailed breakdown (per repo / per task):

- [`docs/benchmarks/L1-leaderboard.md`](docs/benchmarks/L1-leaderboard.md)
- [`docs/benchmarks/L1-detailed-results.md`](docs/benchmarks/L1-detailed-results.md)
- Scoring rules (how points are computed): [`docs/05-scoring-rules.md`](docs/05-scoring-rules.md)

Full raw evaluation artifacts for this snapshot are available on the `L1-eval` branch:

- [`results/20260202/` on `L1-eval`](https://github.com/Abelmx/AgentGym/tree/L1-eval/results/20260202)

---

## Quick Start (GitHub Actions recommended; local supported)

### Option A: GitHub Actions (recommended sandbox)

1. **Fork** this repo to your GitHub account (you need permissions to create branches/PRs).
2. In your fork: **Settings → Secrets and variables → Actions** → add `OPENAI_API_KEY`.
3. Go to **Actions** → `L1-eval` → **Run workflow**.
4. Download artifacts at the bottom of the run page (includes `results/` and `artifacts/`).

### Option B: Local run (for debugging)

```bash
python3 -m pip install -r requirements.txt

# Optional: local env (auto-loaded, never committed)
cp .env.example .env
# edit .env: OPENAI_API_KEY / BASE_URL / MODEL_NAME

python3 -m evaluator.run --repos opencompass,mmengine --runs-root ~/sandbox/runs
```

### Local multi-model parallel runs (tmux)

```bash
cp tools/parallel_eval_config.example.json _local/parallel_eval_config.json
python3 tools/run_parallel_eval_tmux.py --config _local/parallel_eval_config.json --attach
```

---

## Output layout

Each run is written under `runs/<model_id>-<timestamp>/`:

- `results/REPORT.md`: summary report
- `results/<repo_id>/<task_id>.json`: per-task results (incl. tool-call transcript)
- `transcripts/<repo_id>.jsonl`: per-repo debug log (requests/responses/tool results)
- `artifacts/<repo_id>/<task_id>/answer.json|answer.md|task_result.json`: model-produced files for review

---

## Next steps (docs)

- Evaluate custom repos: [`docs/01-custom-repos.md`](docs/01-custom-repos.md)
- Add tasks using existing oracles: [`docs/02-add-tasks-existing-oracles.md`](docs/02-add-tasks-existing-oracles.md)
- Add tasks + implement a new oracle: [`docs/03-add-tasks-new-oracle.md`](docs/03-add-tasks-new-oracle.md)
- Best practices for batch extensions: [`docs/04-best-practices-batch-tasks-oracles-with-ai.md`](docs/04-best-practices-batch-tasks-oracles-with-ai.md)
- Scoring rules (0–100) + how to tune weights: [`docs/05-scoring-rules.md`](docs/05-scoring-rules.md)

