from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError


SchemaT = TypeVar("SchemaT", bound=BaseModel)
JSON_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


@dataclass(frozen=True)
class StructuredExtractionResult(Generic[SchemaT]):
    value: SchemaT
    retry_count: int
    raw_response: str


class StructuredExtractionError(RuntimeError):
    def __init__(self, message: str, retry_count: int, raw_response: str = ""):
        super().__init__(message)
        self.retry_count = retry_count
        self.raw_response = raw_response


class LLMProvider(ABC):
    def __init__(self, model: str, max_retries: int = 2):
        self.model = model
        self.max_retries = max_retries

    @abstractmethod
    def _complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> str:
        """Return one raw model response without parsing or persistence."""

    def extract_structured(
        self,
        text: str,
        schema: type[SchemaT],
        system_prompt: str,
    ) -> StructuredExtractionResult[SchemaT]:
        user_prompt = (
            "Return only JSON that conforms to this schema:\n"
            f"{json.dumps(schema.model_json_schema(), ensure_ascii=False)}\n\n"
            "SOURCE TEXT:\n"
            f"{text}"
        )
        last_raw = ""
        last_error = ""

        for attempt in range(self.max_retries + 1):
            if attempt:
                user_prompt = (
                    "Repair the previous response. Return only schema-valid JSON. "
                    "Do not add facts, quotes, or locators absent from SOURCE TEXT.\n"
                    f"VALIDATION ERROR:\n{last_error}\n"
                    f"PREVIOUS RESPONSE:\n{last_raw}\n\n"
                    "SOURCE TEXT:\n"
                    f"{text}"
                )
            last_raw = self._complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
            )
            candidate = last_raw.strip()
            fenced = JSON_FENCE_RE.match(candidate)
            if fenced:
                candidate = fenced.group(1)
            try:
                return StructuredExtractionResult(
                    value=schema.model_validate_json(candidate),
                    retry_count=attempt,
                    raw_response=last_raw,
                )
            except (ValidationError, ValueError) as exc:
                last_error = str(exc)

        raise StructuredExtractionError(
            f"Structured extraction failed after {self.max_retries + 1} attempts: "
            f"{last_error}",
            retry_count=self.max_retries,
            raw_response=last_raw,
        )
