from __future__ import annotations

import argparse
from pathlib import Path

import yaml


DEFAULT_TASKS = [
    (
        "task_001.yaml",
        "Count the number of visible (non-dot) top-level entries in the repo root, excluding `.git/` and `eval_artifacts/` if present. "
        "This should match what you would see from `ls -1` after removing `eval_artifacts`. "
        "Write to eval_artifacts/answer.json: {\"top_level_entries\": <int>} .",
        [
            {
                "key": "top_level_entries",
                "type": "int",
                "oracle": {"fn": "top_level_entry_count", "args": {"exclude": [".git", "eval_artifacts"], "exclude_hidden": True}},
            },
        ],
    ),
    (
        "task_002.yaml",
        "Read README.md and extract its first non-empty line. Write to eval_artifacts/answer.json: {\"readme_first_line\": <string>} .",
        [
            {"key": "readme_first_line", "type": "str", "oracle": {"fn": "readme_first_nonempty_line", "args": {"path": "README.md"}}},
        ],
    ),
    (
        "task_003.yaml",
        "Count how many Markdown files exist in the repo (recursive, excluding .git). Write to eval_artifacts/answer.json: {\"markdown_file_count\": <int>} .",
        [
            {"key": "markdown_file_count", "type": "int", "oracle": {"fn": "glob_count", "args": {"glob": "**/*.md", "exclude_dirs": [".git"]}}},
        ],
    ),
    (
        "task_004.yaml",
        "Find the relative path of the largest file (by bytes) in the repo (excluding .git). Write to eval_artifacts/answer.json: {\"largest_file\": {\"path\": <string>, \"size\": <int>}} .",
        [
            {"key": "largest_file", "type": "json", "oracle": {"fn": "largest_file", "args": {"exclude_dirs": [".git"]}}},
        ],
    ),
    (
        "task_005.yaml",
        "Count YAML files in the repo (recursive, excluding .git). Write to eval_artifacts/answer.json: {\"yaml_file_count\": <int>} .",
        [
            {"key": "yaml_file_count", "type": "int", "oracle": {"fn": "glob_count", "args": {"glob": "**/*.{yml,yaml}", "exclude_dirs": [".git"]}}},
        ],
    ),
    (
        "task_006.yaml",
        "Write a short Python script (python3) to count how many times the substring `pytest` appears across the repo (case-insensitive). "
        "Rules:\n"
        "- Exclude directories: `.git/` and `eval_artifacts/`\n"
        "- Consider only files with size <= 1,000,000 bytes\n"
        "- Skip any file that contains a NUL byte (0x00) anywhere\n"
        "- Decode bytes as UTF-8 with errors='ignore'\n"
        "- Count occurrences using `text.lower().count('pytest')`\n"
        "Write to eval_artifacts/answer.json: {\"token_pytest_count\": <int>} .",
        [
            {
                "key": "token_pytest_count",
                "type": "int",
                "oracle": {
                    "fn": "repo_token_count",
                    "args": {"token": "pytest", "case_insensitive": True, "exclude_dirs": [".git", "eval_artifacts"], "max_bytes": 1000000},
                },
            },
        ],
    ),
    (
        "task_007.yaml",
        "Determine whether a LICENSE file exists at repo root (LICENSE or LICENSE.md). Write to eval_artifacts/answer.json: {\"has_license\": <true|false>} .",
        [
            {"key": "has_license", "type": "json", "oracle": {"fn": "has_license_file", "args": {"paths": ["LICENSE", "LICENSE.md"]}}},
        ],
    ),
    (
        "task_008.yaml",
        "Count Python files in the repo (recursive, excluding .git). Write to eval_artifacts/answer.json: {\"python_file_count\": <int>} .",
        [
            {"key": "python_file_count", "type": "int", "oracle": {"fn": "glob_count", "args": {"glob": "**/*.py", "exclude_dirs": [".git"]}}},
        ],
    ),
    (
        "task_009.yaml",
        "Find how many entries are in the top-level \"docs\" directory. If it doesn't exist, return 0. Write to eval_artifacts/answer.json: {\"docs_top_entries\": <int>} .",
        [
            {"key": "docs_top_entries", "type": "int", "oracle": {"fn": "dir_top_entry_count", "args": {"path": "docs", "exclude_hidden": True}}},
        ],
    ),
    (
        "task_010.yaml",
        "Create a short structured summary file at eval_artifacts/answer.md using EXACTLY these keys (one per line):\n"
        "repo_id: <repo_id>\n"
        "top_level_entries: <int>\n"
        "has_license: <true|false>\n\n"
        "Definitions:\n"
        "- `top_level_entries`: same as task_001 (visible/non-dot entries in repo root excluding `.git/` and `eval_artifacts/`).\n"
        "- `has_license`: true iff LICENSE or LICENSE.md exists at repo root.\n",
        [
            {
                "key": "answer_md_valid",
                "type": "oracle_bool",
                "oracle": {
                    "fn": "answer_md_kv_matches",
                    "args": {"path": "eval_artifacts/answer.md", "repo_id": "__REPO_ID__", "exclude_top_level": [".git", "eval_artifacts"], "exclude_hidden": True},
                },
            },
        ],
    ),
]


def load_default_command_policy(repo_root: Path) -> dict:
    p = repo_root / "tasks" / "l1" / "_shared" / "default_command_policy.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def write_repo_tasks(repo_root: Path, repo_id: str) -> None:
    policy = load_default_command_policy(repo_root)
    out_dir = repo_root / "tasks" / "l1" / repo_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename, instruction, outputs in DEFAULT_TASKS:
        task_name = filename
        if task_name.endswith(".yaml"):
            task_name = task_name[: -len(".yaml")]
        spec = {
            "id": f"{repo_id}_{task_name}",
            "repo": repo_id,
            "difficulty": "easy",
            "initial_working_dir": ".",
            "instruction": instruction,
            "command_policy": policy,
            "outputs": _rewrite_outputs(outputs, repo_id),
            "max_commands": 12,
            "timeout_seconds": 180,
        }
        (out_dir / filename).write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _rewrite_outputs(outputs: list, repo_id: str) -> list:
    """
    Replace placeholders inside output oracle args.
    """
    rewritten = []
    for o in outputs:
        o2 = dict(o)
        oracle = dict(o2.get("oracle") or {})
        args = dict(oracle.get("args") or {})
        for k, v in list(args.items()):
            if v == "__REPO_ID__":
                args[k] = repo_id
        oracle["args"] = args
        o2["oracle"] = oracle
        rewritten.append(o2)
    return rewritten


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-id", required=True)
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    write_repo_tasks(repo_root, args.repo_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

