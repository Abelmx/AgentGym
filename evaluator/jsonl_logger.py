from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from evaluator.logging_utils import to_jsonable, utc_now_iso


class JsonlLogger:
    """
    Append-only JSONL logger (one JSON object per line).
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, **fields: Any) -> None:
        payload: Dict[str, Any] = {"ts": utc_now_iso(), "event": event, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(to_jsonable(payload), ensure_ascii=False) + "\n")

