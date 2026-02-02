from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

import yaml


Difficulty = Literal["easy", "medium", "hard"]


@dataclass(frozen=True)
class CommandPolicy:
    allowed: list[str]
    prohibited: list[str]
    write_paths_allowed: list[str]


@dataclass(frozen=True)
class OracleSpec:
    fn: str
    args: dict[str, Any]


@dataclass(frozen=True)
class ExpectedOutput:
    key: str
    type: Literal["int", "str", "float", "json", "oracle_bool"]
    oracle: OracleSpec
    comparator: Literal["equals"] = "equals"
    weight: float = 1.0


@dataclass(frozen=True)
class TaskSpec:
    id: str
    repo: str
    difficulty: Difficulty
    initial_working_dir: str
    instruction: str
    command_policy: CommandPolicy
    outputs: list[ExpectedOutput]
    max_commands: int = 10
    timeout_seconds: int = 120


def _must_str(d: dict[str, Any], k: str) -> str:
    v = d.get(k)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"Task field `{k}` must be non-empty string")
    return v


def _must_int(d: dict[str, Any], k: str, default: Optional[int] = None) -> int:
    if k not in d:
        if default is None:
            raise ValueError(f"Task field `{k}` must be int")
        return default
    v = d[k]
    if not isinstance(v, int):
        raise ValueError(f"Task field `{k}` must be int")
    return v


def load_task(path: Path) -> TaskSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid YAML task: {path}")

    cp_raw = raw.get("command_policy") or {}
    if not isinstance(cp_raw, dict):
        raise ValueError(f"`command_policy` must be object in {path}")

    outputs_raw = raw.get("outputs")
    if not isinstance(outputs_raw, list) or not outputs_raw:
        raise ValueError(f"`outputs` must be non-empty list in {path}")

    outputs: list[ExpectedOutput] = []
    for o in outputs_raw:
        if not isinstance(o, dict):
            raise ValueError(f"Each output must be object in {path}")
        oracle_raw = o.get("oracle")
        if not isinstance(oracle_raw, dict):
            raise ValueError(f"Output.oracle must be object in {path}")
        args = oracle_raw.get("args") or {}
        if not isinstance(args, dict):
            raise ValueError(f"Oracle.args must be object in {path}")

        outputs.append(
            ExpectedOutput(
                key=_must_str(o, "key"),
                type=o.get("type", "str"),
                oracle=OracleSpec(fn=_must_str(oracle_raw, "fn"), args=args),
                comparator=o.get("comparator", "equals"),
                weight=float(o.get("weight", 1.0)),
            )
        )

    return TaskSpec(
        id=_must_str(raw, "id"),
        repo=_must_str(raw, "repo"),
        difficulty=raw.get("difficulty", "easy"),
        initial_working_dir=_must_str(raw, "initial_working_dir"),
        instruction=_must_str(raw, "instruction"),
        command_policy=CommandPolicy(
            allowed=list(cp_raw.get("allowed", [])),
            prohibited=list(cp_raw.get("prohibited", [])),
            write_paths_allowed=list(cp_raw.get("write_paths_allowed", ["eval_artifacts/", "/tmp/"])),
        ),
        outputs=outputs,
        max_commands=_must_int(raw, "max_commands", default=10),
        timeout_seconds=_must_int(raw, "timeout_seconds", default=120),
    )


def load_tasks_dir(tasks_dir: Path) -> list[TaskSpec]:
    paths = sorted([p for p in tasks_dir.glob("task_*.yaml") if p.is_file()])
    return [load_task(p) for p in paths]

