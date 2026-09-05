from app.llm.base import LLMProvider, StructuredExtractionResult
from app.llm.prompts import PromptTemplate, load_prompt
from app.schemas.extraction import (
    CaseDetectionResult,
    CaseExtractionResult,
    PaperMetadataCandidate,
)
from app.services.chunking import TextChunk, bounded_chunk_context


class PaperMetadataExtractor:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.prompt: PromptTemplate = load_prompt("paper_metadata", "v2")

    def extract(
        self, chunks: list[TextChunk]
    ) -> StructuredExtractionResult[PaperMetadataCandidate]:
        context = bounded_chunk_context(chunks, max_chars=12000, case_priority=False)
        return self.provider.extract_structured(
            context, PaperMetadataCandidate, self.prompt.content
        )


class CaseExistenceClassifier:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.prompt: PromptTemplate = load_prompt("case_detection", "v2")

    def classify(
        self, chunks: list[TextChunk]
    ) -> StructuredExtractionResult[CaseDetectionResult]:
        context = bounded_chunk_context(chunks, max_chars=24000, case_priority=True)
        return self.provider.extract_structured(
            context, CaseDetectionResult, self.prompt.content
        )


class CaseExtractor:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.prompt: PromptTemplate = load_prompt("case_extraction", "v5")

    def extract(
        self, chunks: list[TextChunk]
    ) -> StructuredExtractionResult[CaseExtractionResult]:
        context = bounded_chunk_context(chunks, max_chars=24000, case_priority=True)
        return self.provider.extract_structured(
            context, CaseExtractionResult, self.prompt.content
        )
