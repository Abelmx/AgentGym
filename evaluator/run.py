from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from evaluator.config import ModelConfig, RunConfig, getenv_str, parse_repos_csv
from evaluator.dotenv import load_dotenv, parse_dotenv
from evaluator.git_checkout import clone_repo
from evaluator.jsonl_logger import JsonlLogger
from evaluator.logging_utils import log_event, write_json
from evaluator.paths import EvalPaths, default_runs_root
from evaluator.report import generate_run_report
from evaluator.repo_schema import load_repos_dir
from evaluator.task_schema import load_tasks_dir
from evaluator.model_runner import run_one_task
from evaluator.utils import getenv_float, getenv_int, safe_name


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="L1 terminal eval runner (MVP).")
    p.add_argument("--repos", type=str, default=None, help="Comma-separated repo ids. Example: opencompass,mmengine")
    p.add_argument("--task-set", type=str, default="l1", help="Task set name (default: l1)")
    p.add_argument("--runs-root", type=str, default=None, help="Output root directory (default: ./runs)")
    p.add_argument("--dry-run", action="store_true", help="Validate loading only; do not call model.")

    p.add_argument("--model", type=str, default=None, help="Model name (or env MODEL_NAME)")
    p.add_argument("--base-url", type=str, default=None, help="OpenAI-compatible base url (or env BASE_URL)")
    p.add_argument("--api-key", type=str, default=None, help="API key (or env OPENAI_API_KEY)")
    p.add_argument("--temperature", type=float, default=None, help="Sampling temperature (or env OPENAI_TEMPERATURE)")
    p.add_argument("--max-output-tokens", type=int, default=None, help="Max output tokens (or env OPENAI_MAX_OUTPUT_TOKENS)")
    p.add_argument(
        "--include-reasoning-content",
        action="store_true",
        help="Include `reasoning_content` in conversation history (for providers that require it).",
    )

    return p.parse_args()


def main() -> int:
    args = parse_args()

    # Load local .env if present (does not override existing environment by default)
    dotenv_path = Path.cwd() / ".env"
    dotenv_parsed = {}
    if dotenv_path.exists() and dotenv_path.is_file():
        try:
            dotenv_parsed = parse_dotenv(dotenv_path.read_text(encoding="utf-8"))
        except Exception:
            dotenv_parsed = {}
    env_before = dict(os.environ)
    load_dotenv(dotenv_path, override=False)

    env = os.environ
    repos = parse_repos_csv(args.repos) if args.repos else ["opencompass"]
    runs_root = Path(args.runs_root).resolve() if args.runs_root else default_runs_root()

    # Resolve model with explicit precedence: CLI > MODEL_NAME > OPENAI_MODEL
    model_source = "unset"
    if args.model:
        model = args.model
        model_source = "cli"
    else:
        mn = getenv_str(env, "MODEL_NAME")
        if mn:
            model = mn
            # distinguish dotenv vs pre-existing env
            model_source = "dotenv" if ("MODEL_NAME" in dotenv_parsed and env_before.get("MODEL_NAME") != mn) else "env"
        else:
            om = getenv_str(env, "OPENAI_MODEL")
            model = om
            if om:
                model_source = "dotenv" if ("OPENAI_MODEL" in dotenv_parsed and env_before.get("OPENAI_MODEL") != om) else "env"
            else:
                model_source = "unset"

    base_url = args.base_url or getenv_str(env, "BASE_URL") or getenv_str(env, "OPENAI_BASE_URL")
    api_key = args.api_key or getenv_str(env, "OPENAI_API_KEY")
    temperature = (
        args.temperature
        if args.temperature is not None
        else getenv_float(env, "OPENAI_TEMPERATURE") or getenv_float(env, "TEMPERATURE") or 0.0
    )
    max_output_tokens = (
        args.max_output_tokens
        if args.max_output_tokens is not None
        else getenv_int(env, "OPENAI_MAX_OUTPUT_TOKENS") or getenv_int(env, "MAX_OUTPUT_TOKENS") or 4096
    )

    run_cfg = RunConfig(repos=repos, task_set=args.task_set, runs_root=runs_root, dry_run=args.dry_run)
    model_cfg = ModelConfig(
        provider="openai_compatible",
        model=model or "unset",
        api_key=api_key,
        base_url=base_url,
        temperature=float(temperature),
        max_output_tokens=int(max_output_tokens),
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{safe_name(model_cfg.model)}-{ts}"
    run_dir = runs_root / run_id
    paths = EvalPaths(run_dir=run_dir)
    paths.ensure()

    # Record config
    model_cfg_sanitized = {
        "provider": model_cfg.provider,
        "model": model_cfg.model,
        "base_url": model_cfg.base_url,
        "has_api_key": bool(model_cfg.api_key),
        "temperature": model_cfg.temperature,
        "max_output_tokens": model_cfg.max_output_tokens,
        "include_reasoning_content": bool(args.include_reasoning_content),
    }
    write_json(paths.results_dir / "run_config.json", {"run": run_cfg, "model": model_cfg_sanitized})
    # Log dotenv merge summary (never log values; only key names)
    if dotenv_parsed:
        applied = []
        skipped = []
        for k in dotenv_parsed.keys():
            if env_before.get(k) is None and os.environ.get(k) == dotenv_parsed.get(k):
                applied.append(k)
            elif env_before.get(k) is not None and os.environ.get(k) == env_before.get(k):
                skipped.append(k)
        log_event("dotenv_loaded", path=str(dotenv_path), keys=list(dotenv_parsed.keys()), applied_keys=applied, skipped_keys=skipped)
    log_event("model_resolved", model=model_cfg.model, source=model_source)
    log_event("run_started", run_id=run_id, run_dir=str(run_dir), repos=run_cfg.repos, task_set=run_cfg.task_set, dry_run=run_cfg.dry_run, model=model_cfg_sanitized)

    # Load repo registry + tasks
    ws_root = Path.cwd().resolve()
    repo_specs = load_repos_dir(ws_root / "repos")
    weights_path = ws_root / "scoring" / "weights.yaml"
    system_prompt_path = ws_root / "prompts" / "l1_system_prompt_v1.txt"

    # Lazy import to avoid requests dependency for dry-run only use.
    from evaluator.openai_compatible import OpenAICompatibleClient

    client = OpenAICompatibleClient(base_url=model_cfg.base_url, api_key=model_cfg.api_key)

    if not run_cfg.dry_run and model_cfg.model == "unset":
        raise SystemExit("Missing --model (or env MODEL_NAME/OPENAI_MODEL)")

    for repo_id in run_cfg.repos:
        if repo_id not in repo_specs:
            raise SystemExit(f"Unknown repo id: {repo_id}")
        spec = repo_specs[repo_id]

        dest = paths.repos_dir / repo_id
        log_event("repo_clone_started", repo_id=repo_id, url=spec.url, ref=spec.ref, dest=str(dest))
        clone_repo(url=spec.url, ref=spec.ref, dest=dest)
        log_event("repo_clone_finished", repo_id=repo_id, dest=str(dest))
        repo_root = dest

        tasks_dir = ws_root / "tasks" / run_cfg.task_set / repo_id
        tasks = load_tasks_dir(tasks_dir)
        log_event("repo_tasks_loaded", repo_id=repo_id, tasks_count=len(tasks), tasks_dir=str(tasks_dir))

        repo_log = JsonlLogger(paths.transcripts_dir / f"{repo_id}.jsonl")
        repo_log.log(
            "repo_started",
            repo_id=repo_id,
            run_id=run_id,
            model=model_cfg_sanitized,
            tasks_count=len(tasks),
        )

        per_repo_results: list[dict] = []
        repo_started_count = 0
        repo_success_count = 0
        repo_score_sum = 0.0

        for idx, task in enumerate(tasks, start=1):
            repo_started_count += 1
            log_event("task_started", repo_id=repo_id, task_id=task.id, task_index=idx, task_total=len(tasks))
            r = run_one_task(
                client=client,
                model=model_cfg.model,
                system_prompt_path=system_prompt_path,
                task=task,
                repo_root=repo_root,
                weights_path=weights_path,
                max_output_tokens=model_cfg.max_output_tokens,
                temperature=model_cfg.temperature,
                dry_run=run_cfg.dry_run,
                repo_log=repo_log,
                include_reasoning_content=bool(args.include_reasoning_content),
            )
            out_path = paths.results_dir / repo_id / f"{task.id}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(r.result_json_path.read_text(encoding="utf-8"), encoding="utf-8")
            per_repo_results.append({"task_id": task.id, "result_json": str(out_path)})

            # Read back a few key metrics for progress reporting
            try:
                import json as _json

                _obj = _json.loads(out_path.read_text(encoding="utf-8"))
                _m = _obj.get("metrics") or {}
                _success = bool(_m.get("success", False))
                _score = float(_m.get("score_0_100", 0.0))
                _first_failure = ""
                for c in (_obj.get("output_checks") or []):
                    if not c.get("ok", False):
                        _first_failure = str(c.get("key") or "")
                        break
                if _success:
                    repo_success_count += 1
                repo_score_sum += _score
                log_event(
                    "task_finished",
                    repo_id=repo_id,
                    task_id=task.id,
                    task_index=idx,
                    task_total=len(tasks),
                    success=_success,
                    score_0_100=_score,
                    first_failure=_first_failure,
                    repo_progress={"done": idx, "total": len(tasks), "success": repo_success_count, "avg_score": (repo_score_sum / float(idx))},
                )
            except Exception:
                log_event("task_finished", repo_id=repo_id, task_id=task.id, task_index=idx, task_total=len(tasks))

            # Save artifacts for human inspection (best effort)
            task_art_dir = paths.artifacts_dir / repo_id / task.id
            task_art_dir.mkdir(parents=True, exist_ok=True)
            for fname in ["answer.json", "answer.md", "task_result.json"]:
                src = repo_root / "eval_artifacts" / fname
                if src.exists():
                    shutil.copy2(src, task_art_dir / fname)

        write_json(paths.results_dir / repo_id / "index.json", {"repo": repo_id, "tasks": per_repo_results})
        repo_log.log("repo_finished", repo_id=repo_id)
        log_event(
            "repo_finished",
            repo_id=repo_id,
            tasks_total=len(tasks),
            tasks_success=repo_success_count,
            success_rate=(repo_success_count / float(len(tasks))) if tasks else 0.0,
            avg_score=(repo_score_sum / float(len(tasks))) if tasks else 0.0,
        )

    (paths.results_dir / "REPORT.md").write_text(generate_run_report(paths.results_dir), encoding="utf-8")
    log_event("run_finished", run_id=run_id, results_dir=str(paths.results_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

