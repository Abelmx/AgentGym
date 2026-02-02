from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TaskRow:
    task_id: str
    success: bool
    score: float
    commands_used: int
    safety_violations: int
    first_failure: Optional[str]


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_row(task_json: Dict[str, Any]) -> TaskRow:
    task_id = (task_json.get("task") or {}).get("id") or "unknown"
    metrics = task_json.get("metrics") or {}
    checks = task_json.get("output_checks") or []
    first_failure = None
    for c in checks:
        if not c.get("ok", False):
            first_failure = str(c.get("key") or "unknown_key")
            break
    return TaskRow(
        task_id=str(task_id),
        success=bool(metrics.get("success", False)),
        score=float(metrics.get("score_0_100", 0.0)),
        commands_used=int(metrics.get("commands_used", 0)),
        safety_violations=int(metrics.get("safety_violations", 0)),
        first_failure=first_failure,
    )


def generate_repo_report(repo_results_dir: Path) -> str:
    rows: List[TaskRow] = []
    for p in sorted(repo_results_dir.glob("*.json")):
        if p.name == "index.json":
            continue
        try:
            rows.append(_extract_row(_read_json(p)))
        except Exception:
            continue

    if not rows:
        return "No task results found.\n"

    success_rate = sum(1 for r in rows if r.success) / float(len(rows))
    avg_score = sum(r.score for r in rows) / float(len(rows))
    avg_cmds = sum(r.commands_used for r in rows) / float(len(rows))
    safety_total = sum(r.safety_violations for r in rows)

    lines = []
    lines.append(f"- **tasks**: {len(rows)}")
    lines.append(f"- **success_rate**: {success_rate:.2%}")
    lines.append(f"- **avg_score**: {avg_score:.2f}")
    lines.append(f"- **avg_commands_used**: {avg_cmds:.2f}")
    lines.append(f"- **safety_violations_total**: {safety_total}")
    lines.append("")
    lines.append("| task_id | success | score | commands | safety_violations | first_failure |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(
            f"| `{r.task_id}` | {str(r.success).lower()} | {r.score:.1f} | {r.commands_used} | {r.safety_violations} | {r.first_failure or ''} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_run_report(results_dir: Path) -> str:
    repo_dirs = [p for p in sorted(results_dir.iterdir()) if p.is_dir()]
    if not repo_dirs:
        return "No repo results.\n"

    # Aggregate
    per_repo = []
    for rd in repo_dirs:
        per_repo.append((rd.name, generate_repo_report(rd)))

    lines = []
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **repos**: {len(per_repo)}")
    lines.append("")

    for repo_id, body in per_repo:
        lines.append(f"## Repo: `{repo_id}`")
        lines.append("")
        lines.append(body)

    return "\n".join(lines)

