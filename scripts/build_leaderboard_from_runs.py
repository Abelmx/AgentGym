#!/usr/bin/env python3
"""
Build an L1 leaderboard + detailed per-task tables from existing run outputs.

This script is meant for *local* aggregation (e.g. ~/sandbox/runs).
It reads per-task JSON results produced by evaluator and writes markdown docs
into the AgentGym repo (default: docs/benchmarks/).
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class TaskRow:
    repo: str
    task_id: str
    success: bool
    score: float
    commands_used: int
    command_valid_rate: float
    safety_violations: int
    hallucination_signals: int
    first_failure: str


@dataclass
class RunInfo:
    run_dir: Path
    run_id: str  # directory name
    model_id: str
    timestamp: str
    tasks: List[TaskRow]


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _fmt_pct(x: float) -> str:
    return f"{x*100:.2f}%"


def _safe_mean(vals: List[float]) -> float:
    if not vals:
        return 0.0
    return sum(vals) / float(len(vals))


def _first_failure(task_json: Dict[str, Any]) -> str:
    metrics = task_json.get("metrics") or {}
    if bool(metrics.get("success")):
        return ""

    # Prefer failing output check key (matches REPORT.md semantics).
    for chk in task_json.get("output_checks") or []:
        try:
            if not bool(chk.get("ok")):
                return str(chk.get("key") or "output_check_failed")
        except Exception:
            continue

    # Fall back to safety event type.
    transcript = task_json.get("transcript") or {}
    se = transcript.get("safety_events") or []
    if se:
        kind = (se[0] or {}).get("kind")
        return f"safety:{kind or 'violation'}"

    return "unknown"


def _iter_task_result_jsons(results_dir: Path) -> Iterable[Path]:
    # results/<repo>/*.json (skip index.json)
    for repo_dir in sorted([p for p in results_dir.iterdir() if p.is_dir()]):
        for p in sorted(repo_dir.glob("*.json")):
            if p.name == "index.json":
                continue
            yield p


def _parse_run_dir(run_dir: Path) -> Optional[RunInfo]:
    if not run_dir.is_dir():
        return None
    results_dir = run_dir / "results"
    if not results_dir.exists():
        return None

    name = run_dir.name
    if "-" not in name:
        return None
    model_id, ts = name.rsplit("-", 1)
    if not ts.endswith("Z"):
        # keep it permissive; still accept
        pass

    tasks: List[TaskRow] = []
    for p in _iter_task_result_jsons(results_dir):
        tj = _read_json(p)
        metrics = tj.get("metrics") or {}
        task = tj.get("task") or {}
        tasks.append(
            TaskRow(
                repo=str(task.get("repo") or p.parent.name),
                task_id=str(task.get("id") or p.stem),
                success=bool(metrics.get("success")),
                score=float(metrics.get("score_0_100") or 0.0),
                commands_used=int(metrics.get("commands_used") or 0),
                command_valid_rate=float(metrics.get("command_valid_rate") or 0.0),
                safety_violations=int(metrics.get("safety_violations") or 0),
                hallucination_signals=int(metrics.get("hallucination_signals") or 0),
                first_failure=_first_failure(tj),
            )
        )

    return RunInfo(run_dir=run_dir, run_id=name, model_id=model_id, timestamp=ts, tasks=tasks)


def _normalize_model_id(model_id: str) -> str:
    return model_id.strip().lower().replace("-", "_")


def _exclude_model(model_id: str, exclude_models: List[str]) -> bool:
    mid = _normalize_model_id(model_id)
    for x in exclude_models:
        if mid == _normalize_model_id(x):
            return True
    return False


def _group_by(items: Iterable[TaskRow], key_fn) -> Dict[str, List[TaskRow]]:
    out: Dict[str, List[TaskRow]] = {}
    for it in items:
        k = str(key_fn(it))
        out.setdefault(k, []).append(it)
    return out


def _md_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_docs(*, runs: List[RunInfo], out_dir: Path, title_suffix: str, runs_root: Path) -> Tuple[Path, Path]:
    # Flatten into per-model grouping (across multiple runs).
    by_model: Dict[str, List[RunInfo]] = {}
    for r in runs:
        by_model.setdefault(r.model_id, []).append(r)

    # Aggregate per-model metrics (overall + per-repo).
    model_summaries: Dict[str, Dict[str, Any]] = {}
    model_repo_summaries: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for model_id, m_runs in sorted(by_model.items(), key=lambda kv: kv[0].lower()):
        tasks = [t for rr in m_runs for t in rr.tasks]
        total = len(tasks)
        succ = sum(1 for t in tasks if t.success)
        avg_score = _safe_mean([t.score for t in tasks])
        avg_cmds = _safe_mean([float(t.commands_used) for t in tasks])
        avg_valid = _safe_mean([t.command_valid_rate for t in tasks])
        safety_total = sum(t.safety_violations for t in tasks)
        safety_per_task = (float(safety_total) / float(total)) if total else 0.0
        hall_total = sum(t.hallucination_signals for t in tasks)
        hall_per_task = (float(hall_total) / float(total)) if total else 0.0

        model_summaries[model_id] = {
            "runs": len(m_runs),
            "tasks": total,
            "success_rate": (float(succ) / float(total)) if total else 0.0,
            "avg_score": avg_score,
            "avg_commands": avg_cmds,
            "avg_command_valid_rate": avg_valid,
            "safety_total": safety_total,
            "safety_per_task": safety_per_task,
            "hall_total": hall_total,
            "hall_per_task": hall_per_task,
        }

        # Per-repo metrics.
        by_repo = _group_by(tasks, lambda t: t.repo)
        repo_stats: Dict[str, Dict[str, Any]] = {}
        for repo_id, rtasks in by_repo.items():
            rtotal = len(rtasks)
            rsucc = sum(1 for t in rtasks if t.success)
            repo_stats[repo_id] = {
                "tasks": rtotal,
                "avg_score": _safe_mean([t.score for t in rtasks]),
                "success_rate": (float(rsucc) / float(rtotal)) if rtotal else 0.0,
                "avg_commands": _safe_mean([float(t.commands_used) for t in rtasks]),
                "safety_total": sum(t.safety_violations for t in rtasks),
                "hall_total": sum(t.hallucination_signals for t in rtasks),
            }
        model_repo_summaries[model_id] = repo_stats

    # Sort leaderboard by avg_score desc, then success_rate desc.
    sorted_models = sorted(
        model_summaries.items(),
        key=lambda kv: (kv[1]["avg_score"], kv[1]["success_rate"]),
        reverse=True,
    )

    # Leaderboard rows (avoid duplicating README; include per-repo scores).
    def repo_score(repo_stats: Dict[str, Dict[str, Any]], repo_id: str) -> str:
        if repo_id not in repo_stats:
            return "-"
        return f'{float(repo_stats[repo_id]["avg_score"]):.2f}'

    def model_cell_en(model_id: str) -> str:
        if model_id == "gpt-5.2":
            return "`gpt-5.2` (closed-source reference)"
        return f"`{model_id}`"

    def model_cell_zh(model_id: str) -> str:
        if model_id == "gpt-5.2":
            return "`gpt-5.2`（闭源参考标杆）"
        return f"`{model_id}`"

    lb_rows_en: List[List[str]] = []
    lb_rows_zh: List[List[str]] = []
    for model_id, s in sorted_models:
        repo_stats = model_repo_summaries.get(model_id, {})
        common = [
            f'{s["avg_score"]:.2f}',
            _fmt_pct(float(s["success_rate"])),
            repo_score(repo_stats, "internlm"),
            repo_score(repo_stats, "mmengine"),
            repo_score(repo_stats, "opencompass"),
            f'{float(s["safety_per_task"]):.2f} ({s["safety_total"]})',
        ]
        lb_rows_en.append([model_cell_en(model_id), *common])
        lb_rows_zh.append([model_cell_zh(model_id), *common])

    leaderboard_md = "\n".join(
        [
            f"# L1 Leaderboard {title_suffix}".rstrip(),
            "",
            "> **Important**: LLM outputs are non-deterministic. Results are **for reference and model/tooling optimization only**,",
            "> and should not be interpreted as AgentGym’s subjective judgement of any model.",
            ">",
            "> `gpt-5.2` is a **closed-source reference baseline** here (an “ideal output” target to sanity-check the evaluation design).",
            "",
            f"- **models**: {len(sorted_models)} (some models may be excluded; e.g. `intern-s1-pro` beta results are not shown)",
            "",
            _md_table(
                headers=[
                    "Model",
                    "Avg Score (overall)",
                    "Avg Success Rate (overall)",
                    "Avg Score (internlm)",
                    "Avg Score (mmengine)",
                    "Avg Score (opencompass)",
                    "Safety / task (total)",
                ],
                rows=lb_rows_en,
            ),
            "",
            "See detailed per-repo / per-task breakdown:",
            f"- [`L1-detailed-results.md`](L1-detailed-results.md)",
            "",
            "Full raw evaluation artifacts for this snapshot are available on the `L1-eval` branch:",
            "- [`results/20260202/` on `L1-eval`](https://github.com/Abelmx/AgentGym/tree/L1-eval/results/20260202)",
            "",
        ]
    )

    # Detailed results page.
    detail_lines: List[str] = []
    detail_lines.append(f"# L1 Detailed Results {title_suffix}".rstrip())
    detail_lines.append("")
    detail_lines.append(
        "> **Note**: LLM outputs are non-deterministic. These results are a snapshot for reference and optimization."
    )
    detail_lines.append("")
    detail_lines.append("- Some models may be excluded (e.g. `intern-s1-pro` beta results are not shown).")
    detail_lines.append("")

    for model_id, _ in sorted_models:
        s = model_summaries[model_id]
        detail_lines.append(f"## Model: `{model_id}`")
        detail_lines.append("")
        detail_lines.append(
            _md_table(
                headers=["Runs", "Tasks", "Avg Score", "Avg Success Rate", "Avg Commands / task", "Safety (total)", "Hallucination (total)"],
                rows=[
                    [
                        str(s["runs"]),
                        str(s["tasks"]),
                        f'{s["avg_score"]:.2f}',
                        _fmt_pct(float(s["success_rate"])),
                        f'{float(s["avg_commands"]):.2f}',
                        str(s["safety_total"]),
                        str(s["hall_total"]),
                    ]
                ],
            )
        )
        detail_lines.append("")

        tasks_all = [t for rr in by_model[model_id] for t in rr.tasks]
        by_repo = _group_by(tasks_all, lambda t: t.repo)

        # Per-repo summary table.
        repo_rows: List[List[str]] = []
        for repo_id in sorted(by_repo.keys()):
            rtasks = by_repo[repo_id]
            total = len(rtasks)
            succ = sum(1 for t in rtasks if t.success)
            repo_rows.append(
                [
                    f"`{repo_id}`",
                    str(total),
                    f"{_safe_mean([t.score for t in rtasks]):.2f}",
                    _fmt_pct(float(succ) / float(total) if total else 0.0),
                    f"{_safe_mean([float(t.commands_used) for t in rtasks]):.2f}",
                    str(sum(t.safety_violations for t in rtasks)),
                    str(sum(t.hallucination_signals for t in rtasks)),
                ]
            )
        detail_lines.append("### Per-repo metrics")
        detail_lines.append("")
        detail_lines.append(
            _md_table(
                headers=["Repo", "Tasks", "Avg Score", "Success Rate", "Avg Commands / task", "Safety Violations", "Hallucination Signals"],
                rows=repo_rows,
            )
        )
        detail_lines.append("")

        # Per-repo per-task tables.
        for repo_id in sorted(by_repo.keys()):
            detail_lines.append(f"### Repo: `{repo_id}` (per-task)")
            detail_lines.append("")
            rtasks = sorted(by_repo[repo_id], key=lambda t: t.task_id)
            rows: List[List[str]] = []
            for t in rtasks:
                rows.append(
                    [
                        f"`{t.task_id}`",
                        "true" if t.success else "false",
                        f"{t.score:.1f}",
                        str(t.commands_used),
                        f"{t.command_valid_rate:.2f}",
                        str(t.safety_violations),
                        str(t.hallucination_signals),
                        t.first_failure,
                    ]
                )
            detail_lines.append(
                _md_table(
                    headers=[
                        "task_id",
                        "success",
                        "score",
                        "commands",
                        "cmd_valid_rate",
                        "safety",
                        "hallucination",
                        "first_failure",
                    ],
                    rows=rows,
                )
            )
            detail_lines.append("")

    details_md = "\n".join(detail_lines).rstrip() + "\n"

    leaderboard_path = out_dir / "L1-leaderboard.md"
    details_path = out_dir / "L1-detailed-results.md"
    _write_text(leaderboard_path, leaderboard_md)
    _write_text(details_path, details_md)

    # Also write a Chinese version under out_dir/zh-CN/ (tables remain the same; headings/disclaimer localized).
    out_dir_zh = out_dir / "zh-CN"
    leaderboard_path_zh = out_dir_zh / "L1-leaderboard.md"
    details_path_zh = out_dir_zh / "L1-detailed-results.md"

    leaderboard_md_zh = "\n".join(
        [
            f"# L1 Leaderboard（本地快照）".rstrip(),
            "",
            "> **说明**：大模型输出具有非确定性（non-deterministic）。这些结果仅用于参考与模型/工具链优化，",
            "> 不代表 AgentGym 对任何模型的主观看法。",
            ">",
            "> 其中 `gpt-5.2` 作为**闭源参考标杆**（“理想输出”的参考线），用于帮助校验评测流程与题目设计是否合理。",
            "",
            f"- **models**: {len(sorted_models)}（部分模型可能被排除；例如 `intern-s1-pro` beta/未开源结果暂不展示）",
            "",
            _md_table(
                headers=[
                    "Model",
                    "总体均分",
                    "总体成功率",
                    "internlm 均分",
                    "mmengine 均分",
                    "opencompass 均分",
                    "安全违规/题（总数）",
                ],
                rows=lb_rows_zh,
            ),
            "",
            "更详细的分 repo / 分 task 数据：",
            f"- [`L1-detailed-results.md`](L1-detailed-results.md)",
            "",
            "本次快照对应的**完整评测产物**请见 `L1-eval` 分支：",
            "- [`L1-eval` 分支的 `results/20260202/`](https://github.com/Abelmx/AgentGym/tree/L1-eval/results/20260202)",
            "",
        ]
    )

    # For detailed results, reuse the English markdown but translate section headers lightly.
    # We keep tables/ids as-is to preserve readability and copy/paste fidelity.
    details_md_zh = details_md
    details_md_zh = details_md_zh.replace("# L1 Detailed Results", "# L1 详细结果")
    details_md_zh = details_md_zh.replace("## Model:", "## 模型：")
    details_md_zh = details_md_zh.replace("### Per-repo metrics", "### 各 repo 指标汇总")
    details_md_zh = details_md_zh.replace("### Repo:", "### Repo：")
    details_md_zh = details_md_zh.replace("> **Note**:", "> **说明**：")
    details_md_zh = details_md_zh.replace("Some models may be excluded", "部分模型可能被排除")

    _write_text(leaderboard_path_zh, leaderboard_md_zh)
    _write_text(details_path_zh, details_md_zh)

    return leaderboard_path, details_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", default="/home/maoxin/sandbox/runs", help="Path containing <model>-<timestamp>/ run dirs")
    ap.add_argument("--out-dir", default="docs/benchmarks", help="Output directory inside this repo")
    ap.add_argument(
        "--exclude-model",
        action="append",
        default=["intern-s1-pro", "intern_s1_pro"],
        help="Model id to exclude (repeatable). Default excludes intern-s1-pro variants.",
    )
    ap.add_argument("--title-suffix", default="(from local runs)", help="Suffix appended to EN doc titles")
    args = ap.parse_args()

    runs_root = Path(args.runs_root).expanduser().resolve()
    out_dir = Path(args.out_dir)

    run_infos: List[RunInfo] = []
    if not runs_root.exists():
        raise SystemExit(f"runs_root not found: {runs_root}")

    for child in sorted(runs_root.iterdir()):
        ri = _parse_run_dir(child)
        if not ri:
            continue
        if _exclude_model(ri.model_id, args.exclude_model):
            continue
        if not ri.tasks:
            continue
        run_infos.append(ri)

    if not run_infos:
        raise SystemExit("No valid runs found (after filtering).")

    build_docs(runs=run_infos, out_dir=out_dir, title_suffix=args.title_suffix, runs_root=runs_root)
    print(f"Wrote docs to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

