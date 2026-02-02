from __future__ import annotations

import re
from typing import Optional


def safe_name(s: Optional[str]) -> str:
    """
    Make a string safe for use in file/dir names.
    """
    if not s:
        return "unknown"
    s = s.strip()
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s)
    return s or "unknown"


def getenv_float(env: dict, key: str) -> Optional[float]:
    v = env.get(key)
    if v is None:
        return None
    try:
        return float(str(v).strip())
    except Exception:
        return None


def getenv_int(env: dict, key: str) -> Optional[int]:
    v = env.get(key)
    if v is None:
        return None
    try:
        return int(str(v).strip())
    except Exception:
        return None

