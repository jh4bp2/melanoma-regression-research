import json
from typing import Any

from app.llm.base import LLMProvider, StructuredExtractionResult
from app.llm.prompts import PromptTemplate, load_prompt
from app.schemas.extraction import BiologicalObservationExtractionResult
from app.services.chunking import TextChunk, bounded_chunk_context


class BiologicalObservationExtractor:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.prompt: PromptTemplate = load_prompt(
            "biological_observation_extraction", "v5"
        )

    def extract(
        self,
        chunks: list[TextChunk],
        case_context: dict[str, Any],
        timeline_context: list[dict[str, Any]],
    ) -> StructuredExtractionResult[BiologicalObservationExtractionResult]:
        source = bounded_chunk_context(
            chunks,
            max_chars=32000,
            case_priority=True,
        )
        extraction_text = (
            "PHASE 2 CASE CONTEXT (not source evidence):\n"
            f"{json.dumps(case_context, ensure_ascii=False, default=str)}\n\n"
            "PHASE 2 TIMELINE CONTEXT (not source evidence):\n"
            f"{json.dumps(timeline_context, ensure_ascii=False, default=str)}\n\n"
            "PAPER SOURCE TEXT:\n"
            f"{source}"
        )
        return self.provider.extract_structured(
            extraction_text,
            BiologicalObservationExtractionResult,
            self.prompt.content,
        )
