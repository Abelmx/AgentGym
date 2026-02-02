from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass(frozen=True)
class CommandRunResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int


@dataclass(frozen=True)
class SafetyEvent:
    kind: str  # e.g. prohibited_command, disallowed_write_path, path_escape
    detail: str


class PolicyError(RuntimeError):
    def __init__(self, message: str, *, event: SafetyEvent):
        super().__init__(message)
        self.event = event


def _normalize_allowed_cmds(cmds: List[str]) -> Set[str]:
    return {c.strip() for c in cmds if isinstance(c, str) and c.strip()}


def _normalize_path_prefixes(prefixes: List[str]) -> List[str]:
    out: List[str] = []
    for p in prefixes:
        if not isinstance(p, str):
            continue
        p = p.strip()
        if not p:
            continue
        out.append(p)
    return out


def _first_token(cmd: str) -> Optional[str]:
    try:
        parts = shlex.split(cmd, posix=True)
    except ValueError:
        return None
    if not parts:
        return None
    return parts[0]


_WORD_RE = re.compile(r"[A-Za-z0-9_./:-]+")


def _tokens_for_scan(cmd: str) -> Set[str]:
    # Used for quick black/white list checks (not a full parser).
    return {m.group(0) for m in _WORD_RE.finditer(cmd)}


class TerminalTools:
    """
    A minimal, OpenAI-tool-call-friendly terminal/files API for evaluation.

    - All filesystem ops are restricted to `repo_root` except explicit `/tmp/`.
    - Writes are restricted to configured prefixes (default: `eval_artifacts/`, `/tmp/`).
    - Command execution is gated by allow/deny lists.
    """

    def __init__(
        self,
        *,
        repo_root: Path,
        allowed_commands: List[str],
        prohibited_commands: List[str],
        write_paths_allowed: List[str],
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.allowed = _normalize_allowed_cmds(allowed_commands)
        self.prohibited = _normalize_allowed_cmds(prohibited_commands)
        self.write_prefixes = _normalize_path_prefixes(write_paths_allowed)
        self.safety_events: List[SafetyEvent] = []

    def _record_event(self, event: SafetyEvent) -> None:
        self.safety_events.append(event)

    def _resolve_repo_path(self, path: str, *, allow_tmp: bool) -> Path:
        p = Path(path)
        if p.is_absolute():
            rp = p.resolve()
        else:
            rp = (self.repo_root / p).resolve()

        if allow_tmp and str(rp).startswith("/tmp/"):
            return rp

        # Must remain inside repo_root.
        try:
            rp.relative_to(self.repo_root)
        except ValueError:
            event = SafetyEvent(kind="path_escape", detail=f"path={path} resolved={rp}")
            self._record_event(event)
            raise PolicyError("Path escapes repo_root", event=event)
        return rp

    def _is_write_allowed(self, resolved_path: Path) -> bool:
        s = str(resolved_path)
        if s.startswith("/tmp/"):
            return any(p.startswith("/tmp/") or p == "/tmp" for p in self.write_prefixes)

        rel = resolved_path.relative_to(self.repo_root).as_posix()
        for prefix in self.write_prefixes:
            if prefix.startswith("/tmp/"):
                continue
            # Treat prefixes as path prefixes (e.g. eval_artifacts/)
            if rel == prefix.rstrip("/"):
                return True
            if rel.startswith(prefix):
                return True
        return False

    def _check_command_policy(self, cmd: str) -> None:
        first = _first_token(cmd)
        if first is None:
            event = SafetyEvent(kind="command_parse_error", detail=f"cmd={cmd!r}")
            self._record_event(event)
            raise PolicyError("Failed to parse command", event=event)

        # Deny list: if any prohibited token appears, block.
        scan = _tokens_for_scan(cmd)
        for bad in self.prohibited:
            if bad in scan or bad == first:
                event = SafetyEvent(kind="prohibited_command", detail=f"cmd={cmd!r} matched={bad!r}")
                self._record_event(event)
                raise PolicyError("Prohibited command", event=event)

        # Allow list: require the first token be in allowed.
        if self.allowed and first not in self.allowed:
            event = SafetyEvent(kind="command_not_allowed", detail=f"cmd={cmd!r} first={first!r}")
            self._record_event(event)
            raise PolicyError("Command not in allow-list", event=event)

    def run_command(self, command: str, *, cwd: Optional[str] = None, timeout_seconds: Optional[int] = None) -> CommandRunResult:
        self._check_command_policy(command)

        cwd_path = self.repo_root if cwd is None else self._resolve_repo_path(cwd, allow_tmp=False)

        t0 = time.time()
        try:
            # Use bash to support common shell builtins/pipes while still applying our policy checks above.
            p = subprocess.run(
                ["bash", "-lc", command],
                cwd=str(cwd_path),
                capture_output=True,
                text=True,
                timeout=timeout_seconds or 60,
                env={**os.environ, "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"},
            )
        except subprocess.TimeoutExpired as e:
            dt = int((time.time() - t0) * 1000)
            return CommandRunResult(stdout=e.stdout or "", stderr=(e.stderr or "") + "\nTIMEOUT", exit_code=124, duration_ms=dt)

        dt = int((time.time() - t0) * 1000)
        return CommandRunResult(stdout=p.stdout, stderr=p.stderr, exit_code=p.returncode, duration_ms=dt)

    def read_file(self, path: str, *, max_bytes: int = 200_000) -> Dict[str, Any]:
        rp = self._resolve_repo_path(path, allow_tmp=False)
        if not rp.exists() or not rp.is_file():
            return {"ok": False, "error": "not_found"}
        data = rp.read_bytes()
        if len(data) > max_bytes:
            return {"ok": False, "error": "too_large", "size": len(data)}
        return {"ok": True, "content": data.decode("utf-8", errors="replace")}

    def list_dir(self, path: str) -> Dict[str, Any]:
        rp = self._resolve_repo_path(path, allow_tmp=False)
        if not rp.exists() or not rp.is_dir():
            return {"ok": False, "error": "not_found"}
        entries = sorted([p.name for p in rp.iterdir()])
        return {"ok": True, "entries": entries}

    def write_file(self, path: str, content: str, *, mode: str = "overwrite") -> Dict[str, Any]:
        rp = self._resolve_repo_path(path, allow_tmp=True)
        if not self._is_write_allowed(rp):
            event = SafetyEvent(kind="disallowed_write_path", detail=f"path={path} resolved={rp}")
            self._record_event(event)
            raise PolicyError("Write path not allowed", event=event)

        rp.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append":
            rp.write_text(rp.read_text(encoding="utf-8", errors="replace") + content, encoding="utf-8")
        else:
            rp.write_text(content, encoding="utf-8")
        return {"ok": True}

    def write_json(self, path: str, obj: Any, *, mode: str = "overwrite") -> Dict[str, Any]:
        return self.write_file(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n", mode=mode)

