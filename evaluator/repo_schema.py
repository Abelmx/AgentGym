from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RepoSpec:
    id: str
    url: str
    ref: str
    initial_working_dir: str = "."


def load_repo(path: Path) -> RepoSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid repo YAML: {path}")

    def must_str(k: str) -> str:
        v = raw.get(k)
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Repo field `{k}` must be non-empty string in {path}")
        return v

    return RepoSpec(
        id=must_str("id"),
        url=must_str("url"),
        ref=must_str("ref"),
        initial_working_dir=str(raw.get("initial_working_dir", ".") or "."),
    )


def load_repos_dir(repos_dir: Path) -> dict[str, RepoSpec]:
    repos: dict[str, RepoSpec] = {}
    for p in sorted(repos_dir.glob("*.yaml")):
        spec = load_repo(p)
        repos[spec.id] = spec
    return repos

