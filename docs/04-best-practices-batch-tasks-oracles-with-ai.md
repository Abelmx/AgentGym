# Best practices: batch tasks & oracles (with AI-native tools)

When you extend AgentGym with new tasks and oracle functions, treat it like an engineering deliverable:

**clear spec → small changes → cross-model validation → batch YAML generation → rerun & review**

This page provides a contributor-friendly workflow that helps keep oracle scoring *objective and reproducible*.

---

## Why use AI-native tools (Cursor / Claude Code) here?

Adding tasks/oracles usually requires:

- editing multiple files (`tasks/`, `scripts/`, `evaluator/oracles.py`)
- running quick dry-runs and oracle sanity checks
- iterating on task wording to remove ambiguity and prevent evaluation artifacts from contaminating results

AI-native tools are great at accelerating this loop, so you can focus on what matters: **task quality and oracle correctness**.

---

## Non-negotiable checklist

- **Use a SOTA model for oracle authoring/review**  
  Oracle code *defines* the evaluation ground truth. Use a strong model to draft/review, e.g. `gpt-5.2`, `claude-4.5-sonnet`, `gemini-3.0-pro` (or higher).

- **Cross-validate oracle outputs across models**  
  Don’t trust a single model’s oracle implementation. At minimum:
  - have two different model families review or implement the same oracle
  - run it on multiple repos
  - confirm outputs match (or the differences are explainable and documented)

- **Write ambiguity out of the task statement**  
  For any counting/stat task (files/tokens/largest file), specify:
  - excluded dirs (recommended: always exclude `.git/` and `eval_artifacts/`)
  - decoding rules / binary rules / file size thresholds (if relevant)
  - the exact output schema (keys in `answer.json` or fields in `answer.md`)

---

## Recommended workflow for batch extensions

### Step 0: choose your extension mode

- **Repo-specific tasks**: write YAML directly under `tasks/l1/<repo_id>/task_*.yaml`
- **Default task set upgrades (batch)**: update `scripts/generate_l1_tasks.py` so all repos get the new tasks

Batch extensions typically mean the second option.

---

### Step 1: write the task spec first (no code yet)

For each task, draft 4 items:

- goal (what should the agent answer/do?)
- scope (which paths are in/out)
- rules (edge cases: encoding/binary/thresholds)
- output format (the exact key/fields)

---

### Step 2: implement or extend the oracle

Oracle functions live in:

- `evaluator/oracles.py`

After implementing and registering a new oracle, run a quick sanity check across multiple repos (see Step 4).

---

### Step 3: land tasks into generator or YAML

If you are upgrading the default task set, update `DEFAULT_TASKS` in `scripts/generate_l1_tasks.py`, then regenerate:

```bash
python3 scripts/generate_l1_tasks.py --repo-id opencompass --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id mmengine --repo-root .
python3 scripts/generate_l1_tasks.py --repo-id internlm --repo-root .
```

---

### Step 4: cross-model validation (the important part)

A minimal validation approach:

1) Let evaluator clone a couple of repos (dry-run is fine):

```bash
python3 -m evaluator.run --dry-run --repos opencompass,mmengine --runs-root ~/sandbox/runs
```

2) Compute oracle outputs on the cloned repos and compare results.

If results mismatch across repos unexpectedly, first check:
- `.git/` and `eval_artifacts/` exclusions
- decoding/binary rules
- file size thresholds / truncation

---

## A copy-paste agent instruction (for new contributors)

Paste this into Cursor / Claude Code after you clone AgentGym.

```text
You are in the AgentGym repository root.

Goal: extend repo_id=<repo_id> with 2 new L1 tasks, and keep scoring objective and reproducible.

Constraints:
- The agent must write answers to eval_artifacts/answer.json or eval_artifacts/answer.md.
- All counting/stat tasks must exclude .git/ and eval_artifacts/.
- Do not add network access or relax safety rules.

Task A (reuse existing oracle):
- Add tasks/l1/<repo_id>/task_011.yaml
- Write a clear instruction and output schema (keys).
- Reuse an existing oracle function from evaluator/oracles.py.

Task B (new oracle required):
- Add tasks/l1/<repo_id>/task_012.yaml
- Add a new oracle function to evaluator/oracles.py and register it in FN_REGISTRY.
- Provide a minimal local validation plan: run the oracle on at least two repos and confirm outputs.

Finally:
- If you changed scripts/generate_l1_tasks.py, regenerate YAML for all repos.
- List all changed files.
- Provide a dry-run command that ensures there is no "Unknown oracle fn" error.
```

