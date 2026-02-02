from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalPaths:
    """
    Centralized filesystem layout for one evaluation run.

    Everything written by the evaluator should live under `run_dir`.
    """

    run_dir: Path

    @property
    def artifacts_dir(self) -> Path:
        return self.run_dir / "artifacts"

    @property
    def transcripts_dir(self) -> Path:
        return self.run_dir / "transcripts"

    @property
    def results_dir(self) -> Path:
        return self.run_dir / "results"

    @property
    def work_dir(self) -> Path:
        return self.run_dir / "work"

    @property
    def repos_dir(self) -> Path:
        return self.work_dir / "repos"

    def ensure(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)


def workspace_root() -> Path:
    # In CI and locally, we treat the current repo root as workspace root.
    # `python -m evaluator.run` is expected to run from repo root.
    return Path.cwd().resolve()


def default_runs_root() -> Path:
    return workspace_root() / "runs"

