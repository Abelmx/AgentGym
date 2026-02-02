from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


def _run(cmd: List[str], *, cwd: Optional[Path] = None, timeout_seconds: int = 300) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, capture_output=False, timeout=timeout_seconds)


def clone_repo(*, url: str, ref: str, dest: Path) -> None:
    """
    Clone `url` into `dest` and checkout `ref`.

    Strategy:
    - Try shallow clone with `--branch ref` first (works for branches/tags).
    - If that fails (e.g. ref is a commit sha), do a shallow clone of default branch,
      fetch the ref, then checkout.
    """
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        _run(["git", "clone", "--depth", "1", "--branch", ref, url, str(dest)], timeout_seconds=600)
        return
    except subprocess.CalledProcessError:
        # Fallback
        _run(["git", "clone", "--depth", "1", url, str(dest)], timeout_seconds=600)
        try:
            _run(["git", "fetch", "--depth", "1", "origin", ref], cwd=dest, timeout_seconds=300)
        except subprocess.CalledProcessError:
            # Best effort: still attempt checkout; git will error with context.
            pass
        _run(["git", "checkout", ref], cwd=dest, timeout_seconds=60)

