from app.llm.base import LLMProvider, StructuredExtractionResult
from app.llm.prompts import PromptTemplate, load_prompt
from app.schemas.extraction import CaseCandidate, TimelineExtractionResult
from app.services.chunking import TextChunk, bounded_chunk_context


class TimelineExtractor:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.prompt: PromptTemplate = load_prompt("timeline_extraction", "v3")

    def extract(
        self,
        chunks: list[TextChunk],
        case_candidate: CaseCandidate,
    ) -> StructuredExtractionResult[TimelineExtractionResult]:
        case_context = case_candidate.model_dump_json(exclude={"confidence"})
        source_context = bounded_chunk_context(
            chunks, max_chars=24000, case_priority=True
        )
        text = f"TARGET CASE:\n{case_context}\n\nPAPER EXCERPTS:\n{source_context}"
        return self.provider.extract_structured(
            text, TimelineExtractionResult, self.prompt.content
        )
