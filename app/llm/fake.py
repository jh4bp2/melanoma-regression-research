from __future__ import annotations

import json
from collections import deque

from pydantic import BaseModel

from app.llm.base import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Deterministic queued responses for tests; never calls an external API."""

    def __init__(self, responses: list[str | dict], max_retries: int = 2):
        super().__init__(model="fake-llm", max_retries=max_retries)
        self.responses = deque(
            response if isinstance(response, str) else json.dumps(response)
            for response in responses
        )
        self.calls: list[dict[str, str]] = []

    def _complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "schema": schema.__name__,
            }
        )
        if not self.responses:
            raise RuntimeError("FakeLLMProvider has no queued response")
        return self.responses.popleft()
