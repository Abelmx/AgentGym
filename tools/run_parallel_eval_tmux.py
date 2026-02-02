#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Allow running as `python3 tools/run_parallel_eval_tmux.py` from repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluator.utils import safe_name  # noqa: E402


@dataclass(frozen=True)
class ModelEntry:
    model_id: str
    base_url: Optional[str]
    api_key: Optional[str]
    temperature: Optional[float]
    max_output_tokens: Optional[int]
    include_reasoning_content: Optional[bool]


def _run_tmux(args: List[str]) -> None:
    subprocess.run(["tmux", *args], check=True)


def _tmux_exists() -> bool:
    try:
        subprocess.run(["tmux", "-V"], check=True, capture_output=True, text=True)
        return True
    except Exception:
        return False


def _session_exists(session_name: str) -> bool:
    r = subprocess.run(["tmux", "has-session", "-t", session_name], check=False, capture_output=True, text=True)
    return r.returncode == 0


def _load_config(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _must_str(d: Dict[str, Any], k: str) -> str:
    v = d.get(k)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"Missing/invalid `{k}`")
    return v.strip()


def _opt_str(d: Dict[str, Any], k: str) -> Optional[str]:
    v = d.get(k)
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError(f"Invalid `{k}` (must be string)")
    v = v.strip()
    return v or None


def _opt_float(d: Dict[str, Any], k: str) -> Optional[float]:
    v = d.get(k)
    if v is None:
        return None
    try:
        return float(v)
    except Exception as e:
        raise ValueError(f"Invalid `{k}` (must be number)") from e


def _opt_int(d: Dict[str, Any], k: str) -> Optional[int]:
    v = d.get(k)
    if v is None:
        return None
    try:
        return int(v)
    except Exception as e:
        raise ValueError(f"Invalid `{k}` (must be int)") from e


def _opt_bool(d: Dict[str, Any], k: str) -> Optional[bool]:
    v = d.get(k)
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "1", "yes", "y", "on"):
            return True
        if s in ("false", "0", "no", "n", "off"):
            return False
    raise ValueError(f"Invalid `{k}` (must be boolean)")


def _models(cfg: Dict[str, Any]) -> List[ModelEntry]:
    ms = cfg.get("models")
    if not isinstance(ms, list) or not ms:
        raise ValueError("`models` must be a non-empty list")
    out: List[ModelEntry] = []
    for m in ms:
        if not isinstance(m, dict):
            raise ValueError("Each model entry must be an object")
        out.append(
            ModelEntry(
                model_id=_must_str(m, "model_id"),
                base_url=_opt_str(m, "base_url"),
                api_key=_opt_str(m, "api_key"),
                temperature=_opt_float(m, "temperature"),
                max_output_tokens=_opt_int(m, "max_output_tokens"),
                include_reasoning_content=_opt_bool(m, "include_reasoning_content"),
            )
        )
    return out


def _bash_cmd(repo_root: Path, *, repos_csv: str, task_set: str, runs_root: Path, dry_run: bool, model: ModelEntry) -> str:
    exports: List[str] = []
    # Always set model id per-window; everything else falls back to existing env / .env.
    exports.append(f"MODEL_NAME={shlex.quote(model.model_id)}")
    if model.base_url:
        exports.append(f"BASE_URL={shlex.quote(model.base_url)}")
    if model.api_key:
        exports.append(f"OPENAI_API_KEY={shlex.quote(model.api_key)}")
    if model.temperature is not None:
        exports.append(f"OPENAI_TEMPERATURE={shlex.quote(str(model.temperature))}")
    if model.max_output_tokens is not None:
        exports.append(f"OPENAI_MAX_OUTPUT_TOKENS={shlex.quote(str(model.max_output_tokens))}")

    eval_cmd = (
        "python3 -m evaluator.run"
        + (" --dry-run" if dry_run else "")
        + (" --include-reasoning-content" if model.include_reasoning_content else "")
        + f" --task-set {shlex.quote(task_set)}"
        + f" --repos {shlex.quote(repos_csv)}"
        + f" --runs-root {shlex.quote(str(runs_root))}"
    )

    # For debugging, keep the pane/window open even if the process exits.
    script = " && ".join(
        [
            f"cd {shlex.quote(str(repo_root))}",
            # Load .env into this shell so per-model env-var references work.
            "if [ -f .env ]; then set -a; . ./.env; set +a; fi",
            "export " + " ".join(exports),
            eval_cmd,
        ]
    )
    return "bash -lc " + shlex.quote(script)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run AgentGym evaluation for multiple models in parallel using tmux windows.")
    ap.add_argument("--config", required=True, help="Path to JSON config (see tools/parallel_eval_config.example.json).")
    ap.add_argument("--attach", action="store_true", help="Attach to the tmux session after creating windows.")
    ap.add_argument("--kill-existing", action="store_true", help="Kill an existing session with the same name first.")
    args = ap.parse_args()

    if not _tmux_exists():
        raise SystemExit("tmux not found. Please install tmux first (e.g. `sudo apt-get install -y tmux`).")

    cfg_path = Path(args.config).expanduser().resolve()
    cfg = _load_config(cfg_path)

    session_name = safe_name(str(cfg.get("session_name", "agentgym")))
    repo_root = Path(str(cfg.get("repo_root", "."))).expanduser().resolve()
    runs_root = Path(str(cfg.get("runs_root", "./runs"))).expanduser().resolve()

    repos = cfg.get("repos")
    if isinstance(repos, list):
        repos_csv = ",".join([str(x).strip() for x in repos if str(x).strip()])
    elif isinstance(repos, str):
        repos_csv = repos.strip()
    else:
        repos_csv = "opencompass,mmengine,internlm"

    task_set = str(cfg.get("task_set", "l1")).strip() or "l1"
    dry_run = bool(cfg.get("dry_run", False))

    models = _models(cfg)

    # Handle existing session early to avoid hard crashes.
    if _session_exists(session_name):
        if args.kill_existing:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False)
        else:
            print(f"tmux session already exists: {session_name}")
            print("Either attach to it, kill it, or change `session_name` in your config.")
            print(f"- attach: tmux attach -t {session_name}")
            print(f"- kill:   tmux kill-session -t {session_name}")
            print(f"- or rerun with: python3 tools/run_parallel_eval_tmux.py --config {cfg_path} --kill-existing")
            if args.attach:
                subprocess.run(["tmux", "attach", "-t", session_name], check=False)
            return 0

    # Create session + first window
    first = models[0]
    first_win = safe_name(first.model_id)
    cmd0 = _bash_cmd(repo_root, repos_csv=repos_csv, task_set=task_set, runs_root=runs_root, dry_run=dry_run, model=first)
    _run_tmux(["new-session", "-d", "-s", session_name, "-n", first_win, cmd0])
    # Keep panes visible for debugging (default).
    _run_tmux(["set-option", "-t", session_name, "remain-on-exit", "on"])

    # Additional windows
    for m in models[1:]:
        win = safe_name(m.model_id)
        cmd = _bash_cmd(repo_root, repos_csv=repos_csv, task_set=task_set, runs_root=runs_root, dry_run=dry_run, model=m)
        _run_tmux(["new-window", "-t", session_name, "-n", win, cmd])

    print(f"tmux session created: {session_name}")
    print("windows:", ", ".join([safe_name(m.model_id) for m in models]))
    if args.attach:
        subprocess.run(["tmux", "attach", "-t", session_name], check=False)
    else:
        print(f"attach with: tmux attach -t {session_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

