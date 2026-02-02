from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional


ModelProvider = Literal["openai_compatible"]


@dataclass(frozen=True)
class ModelConfig:
    provider: ModelProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # e.g. https://api.openai.com or custom gateway
    temperature: float = 0.0
    max_output_tokens: int = 1024


@dataclass(frozen=True)
class RunConfig:
    repos: list[str]
    task_set: str = "l1"
    runs_root: Optional[Path] = None
    dry_run: bool = False
    max_total_seconds: int = 60 * 30  # per repo run guardrail


def getenv_str(d: dict[str, str], key: str) -> Optional[str]:
    v = d.get(key)
    if v is None:
        return None
    v = v.strip()
    return v or None


def parse_repos_csv(s: str) -> list[str]:
    parts = [p.strip() for p in s.split(",")]
    return [p for p in parts if p]


def merge_run_overrides(base: RunConfig, overrides: dict[str, Any]) -> RunConfig:
    data = {
        "repos": base.repos,
        "task_set": base.task_set,
        "runs_root": base.runs_root,
        "dry_run": base.dry_run,
        "max_total_seconds": base.max_total_seconds,
    }
    data.update(overrides)
    return RunConfig(**data)

