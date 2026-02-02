from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def _strip_quotes(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        return v[1:-1]
    return v


def parse_dotenv(text: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if not k:
            continue
        env[k] = _strip_quotes(v)
    return env


def load_dotenv(path: Path, *, override: bool = False) -> Dict[str, str]:
    """
    Load `.env`-style variables from `path` into process environment.

    - By default does NOT override existing env vars.
    - Returns the parsed key-values.
    """
    if not path.exists() or not path.is_file():
        return {}
    parsed = parse_dotenv(path.read_text(encoding="utf-8"))
    for k, v in parsed.items():
        if not override and k in os.environ:
            continue
        os.environ[k] = v
    return parsed

