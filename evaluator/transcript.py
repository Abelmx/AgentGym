from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

from evaluator.terminal_tools import SafetyEvent


ToolName = Literal["run_command", "read_file", "list_dir", "write_file"]


@dataclass(frozen=True)
class ToolCallRecord:
    tool_name: ToolName
    tool_input: Dict[str, Any]
    tool_output: Optional[Dict[str, Any]]
    ok: bool
    error: Optional[str]
    duration_ms: Optional[int] = None


@dataclass(frozen=True)
class TaskTranscript:
    task_id: str
    tool_calls: List[ToolCallRecord]
    safety_events: List[SafetyEvent]
    # OpenAI messages used to start the conversation (system + user).
    # We intentionally keep this to the initial messages only (not the full history)
    # to make it easy to review task context without bloating result JSON.
    prompt_messages: Optional[List[Dict[str, Any]]] = None
    model_final_message: Optional[str] = None

