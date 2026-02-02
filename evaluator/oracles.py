from __future__ import annotations

import fnmatch
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


def _is_hidden(name: str) -> bool:
    return name.startswith(".")


def _expand_brace_glob(pattern: str) -> list[str]:
    # Minimal support for patterns like **/*.{yml,yaml}
    if "{" not in pattern or "}" not in pattern:
        return [pattern]
    pre, rest = pattern.split("{", 1)
    inside, post = rest.split("}", 1)
    opts = [o.strip() for o in inside.split(",") if o.strip()]
    return [f"{pre}{opt}{post}" for opt in opts] or [pattern]


def top_level_entry_count(*, repo_root: Path, exclude: Optional[List[str]] = None, exclude_hidden: bool = True) -> int:
    exclude = exclude or []
    names = []
    for p in repo_root.iterdir():
        if p.name in exclude:
            continue
        if exclude_hidden and _is_hidden(p.name):
            continue
        names.append(p.name)
    return len(names)


def readme_first_nonempty_line(*, repo_root: Path, path: str = "README.md") -> str:
    p = (repo_root / path).resolve()
    text = p.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.strip():
            return line.rstrip("\n")
    return ""


def glob_count(*, repo_root: Path, glob: str, exclude_dirs: Optional[List[str]] = None) -> int:
    exclude_dirs = exclude_dirs or []
    patterns = _expand_brace_glob(glob)
    matched: set[Path] = set()

    for pat in patterns:
        for p in repo_root.glob(pat):
            if not p.is_file():
                continue
            # Exclude by directory component match.
            parts = set(p.relative_to(repo_root).parts)
            if any(d in parts for d in exclude_dirs):
                continue
            matched.add(p)
    return len(matched)


def _iter_text_files(repo_root: Path, *, exclude_dirs: list[str], max_bytes: int = 1_000_000) -> list[Path]:
    out: list[Path] = []
    for root, dirs, files in os.walk(repo_root):
        root_p = Path(root)
        rel_parts = set(root_p.relative_to(repo_root).parts) if root_p != repo_root else set()
        if any(d in rel_parts for d in exclude_dirs):
            dirs[:] = []
            continue

        # prune excluded dirs early
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            p = root_p / f
            try:
                st = p.stat()
            except OSError:
                continue
            if max_bytes is not None and st.st_size > max_bytes:
                continue
            out.append(p)
    return out


def repo_token_count(
    *,
    repo_root: Path,
    token: str,
    case_insensitive: bool = False,
    exclude_dirs: Optional[List[str]] = None,
    max_bytes: Optional[int] = 1_000_000,
) -> int:
    exclude_dirs = exclude_dirs or []
    total = 0
    needle = token.lower() if case_insensitive else token

    for p in _iter_text_files(repo_root, exclude_dirs=exclude_dirs, max_bytes=max_bytes or 0):
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if b"\x00" in data:
            continue
        text = data.decode("utf-8", errors="ignore")
        hay = text.lower() if case_insensitive else text
        total += hay.count(needle)
    return total


def largest_file(*, repo_root: Path, exclude_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
    exclude_dirs = exclude_dirs or []
    best_path: Optional[Path] = None
    best_size: int = -1

    for root, dirs, files in os.walk(repo_root):
        root_p = Path(root)
        rel_parts = set(root_p.relative_to(repo_root).parts) if root_p != repo_root else set()
        if any(d in rel_parts for d in exclude_dirs):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            p = root_p / f
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_size > best_size:
                best_size = int(st.st_size)
                best_path = p

    if best_path is None:
        return {"path": "", "size": 0}
    rel = best_path.relative_to(repo_root).as_posix()
    return {"path": rel, "size": best_size}


def has_license_file(*, repo_root: Path, paths: List[str]) -> bool:
    for p in paths:
        if (repo_root / p).is_file():
            return True
    return False


def dir_top_entry_count(*, repo_root: Path, path: str, exclude_hidden: bool = True) -> int:
    p = repo_root / path
    if not p.exists() or not p.is_dir():
        return 0
    entries = []
    for c in p.iterdir():
        if exclude_hidden and _is_hidden(c.name):
            continue
        entries.append(c.name)
    return len(entries)


def answer_md_contains(*, repo_root: Path, path: str, must_contain: List[str]) -> bool:
    p = repo_root / path
    if not p.exists() or not p.is_file():
        return False
    text = p.read_text(encoding="utf-8", errors="replace")
    return all(s in text for s in must_contain)


_KV_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_\-]+)\s*:\s*(.*?)\s*$")


def _parse_simple_kv(text: str) -> Dict[str, str]:
    """
    Parse a simple `key: value` file (ignores empty lines and markdown headings).
    Keys are lowercased.
    """
    out: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        m = _KV_LINE_RE.match(raw)
        if not m:
            continue
        k = m.group(1).strip().lower()
        v = m.group(2).strip()
        out[k] = v
    return out


def answer_md_kv_matches(
    *,
    repo_root: Path,
    path: str,
    repo_id: str,
    exclude_top_level: List[str],
    exclude_hidden: bool = True,
) -> bool:
    """
    Validate `eval_artifacts/answer.md` contains exact keys:
      repo_id: <repo_id>
      top_level_entries: <int>   (non-hidden entries at repo root excluding exclude_top_level)
      has_license: <true|false>  (LICENSE or LICENSE.md exists)
    """
    p = repo_root / path
    if not p.exists() or not p.is_file():
        return False
    kv = _parse_simple_kv(p.read_text(encoding="utf-8", errors="replace"))

    expected_top = top_level_entry_count(repo_root=repo_root, exclude=exclude_top_level, exclude_hidden=exclude_hidden)
    expected_license = has_license_file(repo_root=repo_root, paths=["LICENSE", "LICENSE.md"])

    if kv.get("repo_id") != repo_id:
        return False

    try:
        top_val = int(kv.get("top_level_entries", "").strip())
    except Exception:
        return False
    if top_val != expected_top:
        return False

    hv = kv.get("has_license", "").strip().lower()
    if hv in ("true", "yes", "y", "1"):
        has_val = True
    elif hv in ("false", "no", "n", "0"):
        has_val = False
    else:
        return False
    return has_val == expected_license

FN_REGISTRY = {
    "top_level_entry_count": top_level_entry_count,
    "readme_first_nonempty_line": readme_first_nonempty_line,
    "glob_count": glob_count,
    "largest_file": largest_file,
    "repo_token_count": repo_token_count,
    "has_license_file": has_license_file,
    "dir_top_entry_count": dir_top_entry_count,
    "answer_md_contains": answer_md_contains,
    "answer_md_kv_matches": answer_md_kv_matches,
}


def compute_oracle(repo_root: Path, fn: str, args: Dict[str, Any]) -> Any:
    if fn not in FN_REGISTRY:
        raise ValueError(f"Unknown oracle fn: {fn}")
    f = FN_REGISTRY[fn]
    return f(repo_root=repo_root, **args)


def read_answer_json(repo_root: Path, path: str = "eval_artifacts/answer.json") -> Optional[Dict[str, Any]]:
    p = repo_root / path
    if not p.exists() or not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

