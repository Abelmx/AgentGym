from __future__ import annotations

from typing import Any


def terminal_tools_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Run a terminal command in the repo workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to run."},
                        "cwd": {"type": "string", "description": "Working directory relative to repo root.", "nullable": True},
                        "timeout_seconds": {"type": "integer", "description": "Timeout for this command.", "nullable": True},
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a UTF-8 text file under the repo root.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}, "max_bytes": {"type": "integer", "nullable": True}},
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "List directory entries under the repo root.",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write a UTF-8 text file. Only allowed under eval_artifacts/ or /tmp/.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "mode": {"type": "string", "enum": ["overwrite", "append"], "nullable": True},
                    },
                    "required": ["path", "content"],
                },
            },
        },
    ]

