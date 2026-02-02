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
    model_final_message: Optional[str] = None

