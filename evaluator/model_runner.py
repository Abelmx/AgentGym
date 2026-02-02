from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from evaluator.jsonl_logger import JsonlLogger
from evaluator.openai_compatible import OpenAICompatibleClient, OpenAIHTTPError
from evaluator.scoring import score_task, write_task_result_json
from evaluator.task_schema import TaskSpec
from evaluator.terminal_tools import PolicyError, TerminalTools
from evaluator.tool_schema import terminal_tools_schema
from evaluator.transcript import TaskTranscript, ToolCallRecord


@dataclass(frozen=True)
class RunOneTaskResult:
    transcript: TaskTranscript
    result_json_path: Path


def _safe_json_loads(s: str) -> Dict[str, Any]:
    try:
        v = json.loads(s)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def _tool_result_message(tool_call_id: str, result_obj: Dict[str, Any]) -> Dict[str, Any]:
    return {"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps(result_obj, ensure_ascii=False)}


def _load_system_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _task_user_message(task: TaskSpec) -> str:
    keys = ", ".join([o.key for o in task.outputs])
    allowed = ", ".join(task.command_policy.allowed)
    prohibited = ", ".join(task.command_policy.prohibited)
    write_allowed = ", ".join(task.command_policy.write_paths_allowed)
    return (
        f"Repo: {task.repo}\n"
        f"Task: {task.id}\n\n"
        f"Instruction:\n{task.instruction}\n\n"
        f"Expected output keys in eval_artifacts/answer.json: {keys}\n\n"
        f"Command policy:\n"
        f"- allowed: {allowed}\n"
        f"- prohibited: {prohibited}\n"
        f"- write_paths_allowed: {write_allowed}\n"
    )


def run_one_task(
    *,
    client: OpenAICompatibleClient,
    model: str,
    system_prompt_path: Path,
    task: TaskSpec,
    repo_root: Path,
    weights_path: Path,
    max_output_tokens: int = 1024,
    temperature: float = 0.0,
    dry_run: bool = False,
    repo_log: Optional[JsonlLogger] = None,
    include_reasoning_content: bool = False,
) -> RunOneTaskResult:
    # Reset per-task artifacts
    artifacts = repo_root / "eval_artifacts"
    if artifacts.exists():
        shutil.rmtree(artifacts)
    artifacts.mkdir(parents=True, exist_ok=True)

    term = TerminalTools(
        repo_root=repo_root,
        allowed_commands=task.command_policy.allowed,
        prohibited_commands=task.command_policy.prohibited,
        write_paths_allowed=task.command_policy.write_paths_allowed,
    )

    tool_calls: List[ToolCallRecord] = []
    model_final: Optional[str] = None

    if dry_run:
        transcript = TaskTranscript(task_id=task.id, tool_calls=tool_calls, safety_events=term.safety_events, model_final_message=None)
        # Scoring in dry-run is still possible if user pre-populated answer.json.
        score = score_task(task, repo_root=repo_root, transcript=transcript, weights_path=weights_path)
        result_path = repo_root / "eval_artifacts" / "task_result.json"
        write_task_result_json(result_path, task=task, score=score, transcript=transcript)
        return RunOneTaskResult(transcript=transcript, result_json_path=result_path)

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": _load_system_prompt(system_prompt_path)},
        {"role": "user", "content": _task_user_message(task)},
    ]
    tools = terminal_tools_schema()

    t0 = time.time()
    command_steps = 0

    while True:
        if command_steps >= task.max_commands:
            break
        if (time.time() - t0) > task.timeout_seconds:
            break

        if repo_log:
            repo_log.log(
                "llm_request",
                task_id=task.id,
                model=model,
                temperature=temperature,
                max_tokens=max_output_tokens,
                messages=messages,
                tools=tools,
            )
        try:
            resp = client.chat_completions(
                model=model,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
        except OpenAIHTTPError as e:
            if repo_log:
                repo_log.log(
                    "llm_error",
                    task_id=task.id,
                    error_type="OpenAIHTTPError",
                    status_code=e.status_code,
                    url=e.url,
                    response_text=e.response_text,
                    message=str(e),
                )
            raise
        except Exception as e:  # noqa: BLE001
            if repo_log:
                repo_log.log("llm_error", task_id=task.id, error_type=type(e).__name__, message=str(e))
            raise

        if repo_log:
            repo_log.log("llm_response", task_id=task.id, response=resp)
        msg = (resp.get("choices") or [{}])[0].get("message") or {}
        reasoning_content = msg.get("reasoning_content")

        # Tool calls?
        tcalls = msg.get("tool_calls") or []
        if tcalls:
            # Add assistant message that requested tool calls (for OpenAI trace compatibility)
            assistant_msg: Dict[str, Any] = {"role": "assistant", "content": msg.get("content"), "tool_calls": tcalls}
            if include_reasoning_content and reasoning_content is not None:
                # Some providers require `reasoning_content` to be sent back in the next request.
                assistant_msg["reasoning_content"] = reasoning_content
            messages.append(assistant_msg)

            for tc in tcalls:
                tool_call_id = tc.get("id") or ""
                fn = (tc.get("function") or {}).get("name") or ""
                args_s = (tc.get("function") or {}).get("arguments") or "{}"
                args = _safe_json_loads(args_s)

                start = time.time()
                out_obj: Optional[Dict[str, Any]] = None
                ok = True
                err: Optional[str] = None
                try:
                    if fn == "run_command":
                        command_steps += 1
                        r = term.run_command(
                            args.get("command", ""),
                            cwd=args.get("cwd"),
                            timeout_seconds=args.get("timeout_seconds"),
                        )
                        out_obj = {"stdout": r.stdout, "stderr": r.stderr, "exit_code": r.exit_code, "duration_ms": r.duration_ms}
                    elif fn == "read_file":
                        out_obj = term.read_file(args.get("path", ""), max_bytes=int(args.get("max_bytes") or 200_000))
                    elif fn == "list_dir":
                        out_obj = term.list_dir(args.get("path", ""))
                    elif fn == "write_file":
                        out_obj = term.write_file(args.get("path", ""), args.get("content", ""), mode=args.get("mode") or "overwrite")
                    else:
                        ok = False
                        err = f"unknown_tool:{fn}"
                        out_obj = {"ok": False, "error": err}
                except PolicyError as e:
                    ok = False
                    err = str(e)
                    out_obj = {"ok": False, "error": err, "safety_event": {"kind": e.event.kind, "detail": e.event.detail}}
                except Exception as e:  # noqa: BLE001
                    ok = False
                    err = f"tool_error:{type(e).__name__}:{e}"
                    out_obj = {"ok": False, "error": err}

                dt = int((time.time() - start) * 1000)
                tool_calls.append(
                    ToolCallRecord(
                        tool_name=fn,  # type: ignore[arg-type]
                        tool_input=args,
                        tool_output=out_obj,
                        ok=ok,
                        error=err,
                        duration_ms=dt,
                    )
                )
                messages.append(_tool_result_message(tool_call_id, out_obj or {"ok": False, "error": "no_output"}))
                if repo_log:
                    repo_log.log(
                        "tool_result",
                        task_id=task.id,
                        tool_name=fn,
                        tool_input=args,
                        tool_output=out_obj,
                        ok=ok,
                        error=err,
                        duration_ms=dt,
                    )

            # Early-stop heuristic: if answer.json already satisfies oracle, stop.
            transcript = TaskTranscript(task_id=task.id, tool_calls=tool_calls, safety_events=term.safety_events, model_final_message=None)
            try:
                s = score_task(task, repo_root=repo_root, transcript=transcript, weights_path=weights_path)
                if s.success:
                    break
            except Exception:
                pass

            continue

        # No tool calls => final assistant message
        model_final = msg.get("content")
        assistant_msg2: Dict[str, Any] = {"role": "assistant", "content": model_final}
        if include_reasoning_content and reasoning_content is not None:
            assistant_msg2["reasoning_content"] = reasoning_content
        messages.append(assistant_msg2)
        break

    transcript = TaskTranscript(task_id=task.id, tool_calls=tool_calls, safety_events=term.safety_events, model_final_message=model_final)
    score = score_task(task, repo_root=repo_root, transcript=transcript, weights_path=weights_path)
    result_path = repo_root / "eval_artifacts" / "task_result.json"
    write_task_result_json(result_path, task=task, score=score, transcript=transcript)

    return RunOneTaskResult(transcript=transcript, result_json_path=result_path)

