from __future__ import annotations

from copy import deepcopy

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.llm.base import LLMProvider


class LLMConfigurationError(ValueError):
    pass


def _strict_json_schema(schema: dict) -> dict:
    result = deepcopy(schema)

    def visit(node):
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties", {})
                node["additionalProperties"] = False
                node["required"] = list(properties)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(result)
    return result


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        max_retries: int = 2,
        timeout: float = 120.0,
    ):
        if not api_key:
            raise LLMConfigurationError("LLM_API_KEY is required")
        if not model:
            raise LLMConfigurationError("LLM_MODEL is required")
        super().__init__(model=model, max_retries=max_retries)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "strict": True,
                    "schema": _strict_json_schema(schema.model_json_schema()),
                },
            },
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = response.text[:2000]
            raise RuntimeError(
                f"LLM API rejected the request ({response.status_code}): {detail}"
            ) from exc
        data = response.json()
        return data["choices"][0]["message"]["content"]


def create_provider(settings: Settings) -> LLMProvider:
    provider_name = settings.llm_provider.strip().lower()
    if provider_name in {"openai", "openai_compatible"}:
        return OpenAICompatibleProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            max_retries=settings.llm_max_retries,
            timeout=settings.llm_timeout_seconds,
        )
    raise LLMConfigurationError(
        "LLM_PROVIDER must be 'openai' or 'openai_compatible' for PHASE 2"
    )
