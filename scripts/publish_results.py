from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Allow running as `python3 scripts/publish_results.py` from repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluator.utils import safe_name  # noqa: E402


def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def aggregate_run(run_results_dir: Path) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}

    run_cfg = run_results_dir / "run_config.json"
    if run_cfg.exists():
        payload["run_config"] = _read_json(run_cfg)

    report_md = run_results_dir / "REPORT.md"
    if report_md.exists():
        payload["report_markdown"] = report_md.read_text(encoding="utf-8")

    repos: Dict[str, Any] = {}
    for repo_dir in sorted([p for p in run_results_dir.iterdir() if p.is_dir()]):
        repo_id = repo_dir.name
        tasks: List[Dict[str, Any]] = []
        for task_json in sorted(repo_dir.glob("*.json")):
            if task_json.name == "index.json":
                continue
            try:
                tasks.append(_read_json(task_json))
            except Exception:
                continue
        repos[repo_id] = {"tasks": tasks}

    payload["repos"] = repos
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True, help="The evaluator run directory (contains results/).")
    ap.add_argument("--out-root", default="results", help="Repo output root dir (default: results/).")
    ap.add_argument("--date", default=None, help="UTC date folder (YYYYMMDD). Default: today.")
    ap.add_argument("--model-name", required=True, help="Model name used for this run (folder name).")
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    run_results_dir = run_dir / "results"
    if not run_results_dir.exists():
        raise SystemExit(f"Missing results/ under run dir: {run_dir}")

    date = args.date or _utc_date()
    model = safe_name(args.model_name)

    out_root = Path(args.out_root).resolve()
    out_dir = out_root / date / model
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = aggregate_run(run_results_dir)
    (out_dir / "run_aggregate.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Also write REPORT.md as a standalone file for convenience.
    report_md = run_results_dir / "REPORT.md"
    if report_md.exists():
        (out_dir / "REPORT.md").write_text(report_md.read_text(encoding="utf-8"), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

