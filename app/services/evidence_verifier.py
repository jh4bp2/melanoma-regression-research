from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from app.models import EvidenceType, QuoteVerificationStatus
from app.schemas.extraction import EvidenceReference, SourceEvidenceType
from app.services.chunking import TextChunk


INTERPRETATION_RE = re.compile(
    r"\b(may(?!\s+\d{4})|might|could|suggest(?:s|ed|ing)?|speculat\w*|"
    r"hypothesi[sz]\w*|postulat\w*|possible(?: mechanism)?|possibly|"
    r"likely|probably related|could represent|appears? to|thought to|"
    r"we believe|in keeping with|we attribute|intriguing to speculate|"
    r"seems most plausible)\b",
    re.IGNORECASE,
)
OBSERVATION_RE = re.compile(
    r"\b(patient|history|imaging|pet/?ct|computed tomography|patholog\w*|"
    r"histolog\w*|laboratory|biopsy|surgery|resection|treatment|lesion|nodule|"
    r"metastas\w*|regression|progression)\b.*\b("
    r"showed|demonstrated|was found|were found|confirmed|measured|decreased|"
    r"increased|presented|underwent|was performed|were performed|diagnosed|"
    r"identified|observed|received|administered|continued|reduced|resolved|"
    r"vanished|disappeared)\b|"
    r"\b(showed|demonstrated|confirmed|measured|decreased|increased|presented|"
    r"underwent|diagnosed|identified|observed|received|administered|reduced|"
    r"resolved|vanished|disappeared|were present|was present)\b",
    re.IGNORECASE,
)
DIRECT_FINDING_RE = re.compile(
    r"\b(?:were present|was present|showed|demonstrated|measured|"
    r"reduced in size|decreased|increased|resolved|vanished|disappeared|"
    r"infiltration|staining|wild-?type|necrosis|no viable|fibrosis)\b",
    re.IGNORECASE,
)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


_DASH_MAP = {
    "\u00ad": "",
    "‐": "-",
    "‑": "-",
    "‒": "-",
    "–": "-",
    "—": "-",
    "−": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬀ": "ff",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
}


def _map_dashes_and_ligatures(text: str) -> str:
    return text.translate(str.maketrans(_DASH_MAP))


def exact_normalize(text: str) -> str:
    """Whitespace, unicode fold, ligatures. Hyphens are kept."""
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _map_dashes_and_ligatures(normalized).casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = normalized.replace("\u00ad", "")
    normalized = re.sub(r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)", "", normalized)
    normalized = re.sub(r"(?<=\w)-[ \t]+(?=\w)", "", normalized)
    normalized = _map_dashes_and_ligatures(normalized)
    normalized = re.sub(r"(?<=\w)-(?=\w)", "", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def classify_claim(
    quote: str, declared_type: SourceEvidenceType
) -> EvidenceType:
    """Classify by sentence. Direct findings are not rejected as interpretation."""
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(quote) if part.strip()]
    if not sentences:
        sentences = [quote]
    has_clean_observation = False
    has_interpretation_only = False
    has_mixed = False
    for sentence in sentences:
        interpretation = bool(INTERPRETATION_RE.search(sentence))
        observational = _sentence_is_observation(sentence)
        if observational and not interpretation:
            has_clean_observation = True
        elif observational and interpretation:
            has_mixed = True
        elif interpretation:
            has_interpretation_only = True
    if has_clean_observation:
        return EvidenceType.OBSERVED_FACT
    if has_mixed:
        if declared_type == SourceEvidenceType.OBSERVED_FACT:
            return EvidenceType.OBSERVED_FACT
        remainder = INTERPRETATION_RE.split(quote, maxsplit=1)[0]
        if _sentence_is_observation(remainder):
            return EvidenceType.OBSERVED_FACT
        return EvidenceType.AUTHOR_INTERPRETATION
    if has_interpretation_only:
        return EvidenceType.AUTHOR_INTERPRETATION
    if OBSERVATION_RE.search(quote) or DIRECT_FINDING_RE.search(quote):
        return EvidenceType.OBSERVED_FACT
    return EvidenceType(declared_type.value)


def _sentence_is_observation(text: str) -> bool:
    remainder = INTERPRETATION_RE.split(text, maxsplit=1)[0]
    return bool(OBSERVATION_RE.search(remainder) or DIRECT_FINDING_RE.search(remainder))


@dataclass(frozen=True)
class VerifiedReference:
    verified: bool
    quote: str
    page: int | None
    section: str | None
    evidence_type: EvidenceType
    reason: str | None = None
    verification_status: QuoteVerificationStatus = QuoteVerificationStatus.UNVERIFIED
    raw_quote: str | None = None
    normalized_quote: str | None = None


class EvidenceVerifier:
    def __init__(self, pages: dict[int, str], chunks: list[TextChunk]):
        self.pages = pages
        self.chunks = chunks

    def verify(self, reference: EvidenceReference) -> VerifiedReference:
        if "..." in reference.quote or "…" in reference.quote:
            return self._unverified(
                reference, "Quote must be one contiguous span; ellipsis is not allowed"
            )
        raw_quote = reference.quote.strip()
        exact_quote = exact_normalize(raw_quote)
        normalized_quote = normalize_text(raw_quote)
        if not exact_quote and not normalized_quote:
            return self._unverified(reference, "Quote is empty after normalization")

        candidate_pages = []
        if reference.page in self.pages:
            candidate_pages.append(reference.page)
        candidate_pages.extend(page for page in self.pages if page not in candidate_pages)

        for page in candidate_pages:
            page_exact = exact_normalize(self.pages[page])
            page_normalized = normalize_text(self.pages[page])
            exact_hit = bool(exact_quote and exact_quote in page_exact)
            normalized_hit = bool(normalized_quote and normalized_quote in page_normalized)
            if exact_hit or normalized_hit:
                section = self._resolve_section(
                    page, normalized_quote or exact_quote, reference.section
                )
                evidence_type = classify_claim(
                    reference.quote, reference.evidence_type
                )
                status = (
                    QuoteVerificationStatus.VERIFIED_EXACT
                    if exact_hit
                    else QuoteVerificationStatus.VERIFIED_NORMALIZED
                )
                return VerifiedReference(
                    verified=True,
                    quote=raw_quote,
                    page=page,
                    section=section,
                    evidence_type=evidence_type,
                    verification_status=status,
                    raw_quote=raw_quote,
                    normalized_quote=normalized_quote,
                )
        return self._unverified(reference, "Quote was not found in normalized paper text")

    def _resolve_section(
        self, page: int, normalized_quote: str, claimed_section: str | None
    ) -> str | None:
        for chunk in self.chunks:
            if (
                chunk.page_start <= page <= chunk.page_end
                and normalized_quote in normalize_text(chunk.text)
            ):
                return chunk.section
        return claimed_section

    @staticmethod
    def _unverified(
        reference: EvidenceReference, reason: str
    ) -> VerifiedReference:
        evidence_type = (
            EvidenceType.AUTHOR_INTERPRETATION
            if reference.evidence_type == SourceEvidenceType.AUTHOR_INTERPRETATION
            else EvidenceType.OBSERVED_FACT
        )
        return VerifiedReference(
            verified=False,
            quote=reference.quote,
            page=reference.page,
            section=reference.section,
            evidence_type=evidence_type,
            reason=reason,
            verification_status=QuoteVerificationStatus.UNVERIFIED,
            raw_quote=reference.quote,
            normalized_quote=normalize_text(reference.quote),
        )
