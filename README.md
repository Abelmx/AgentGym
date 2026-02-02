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

1. Clone target repos (e.g. `opencompass`, `mmengine`, `internlm`)
2. Run tasks one by one: the model acts via tool calls (terminal/file operations)
3. Oracle computes expected outputs and scores the model’s outputs
4. Produce results and artifacts (reports, per-task JSON, model-written `answer.json`/`answer.md`)
5. (Recommended) In GitHub Actions, open a PR to write results back to your chosen branch

---

## Quick Start (GitHub Actions recommended; local supported)

### Option A: GitHub Actions (recommended sandbox)

1. **Fork** this repo to your GitHub account (you need permissions to create branches/PRs).
2. In your fork: **Settings → Secrets and variables → Actions** → add `OPENAI_API_KEY`.
3. Go to **Actions** → `l1-eval` → **Run workflow**.
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

