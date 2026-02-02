from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class OpenAIHTTPError(RuntimeError):
    def __init__(self, message: str, *, status_code: Optional[int] = None, response_text: Optional[str] = None, url: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
        self.url = url


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class OpenAICompatibleClient:
    def __init__(self, *, base_url: Optional[str], api_key: Optional[str]) -> None:
        self.base_url = (base_url or "https://api.openai.com").rstrip("/")
        self.api_key = api_key

    def _url(self, path: str) -> str:
        # Accept base urls like https://x/v1 or https://x
        if self.base_url.endswith("/v1"):
            return f"{self.base_url}{path}"
        return f"{self.base_url}/v1{path}"

    def chat_completions(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        url = self._url("/chat/completions")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            resp = getattr(e, "response", None)
            raise OpenAIHTTPError(
                f"OpenAI-compatible HTTP error: {e}",
                status_code=getattr(resp, "status_code", None),
                response_text=getattr(resp, "text", None),
                url=url,
            ) from e

