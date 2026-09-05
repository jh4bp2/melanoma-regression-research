from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import Case, CaseScopeStatus
from app.services.chunking import TextChunk
from app.services.evidence_verifier import normalize_text


OTHER_PATIENT_RE = re.compile(
    r"\b(?:patient|case)\s+([a-d]|[1-4])\b(?!\s+report)",
    re.IGNORECASE,
)
SHARED_RE = re.compile(
    r"\b(?:both patients|neither patient|in both cases|"
    r"collectively these findings|the two patients|"
    r"these cases highlight)\b",
    re.IGNORECASE,
)
DISCUSSION_RE = re.compile(
    r"\b(?:may|might|could|suggest|hypothes|we believe|potentially)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ScopedSentence:
    text: str
    status: CaseScopeStatus
    marker: str | None


def case_markers(case: Case) -> set[str]:
    identifier = re.sub(
        r"\s*\[run \d+\]\s*$", "", case.patient_identifier or "", flags=re.I
    )
    if re.match(r"paper-\d+-case-\d+$", identifier, re.I):
        return set()
    match = re.search(
        r"\b(?:patient|case)\s+([a-d]|[1-4])\b(?!\s+report)",
        identifier,
        re.IGNORECASE,
    )
    if match:
        return {match.group(1).casefold()}
    return set()


def classify_sentence(sentence: str, active: set[str]) -> CaseScopeStatus:
    if SHARED_RE.search(sentence):
        if DISCUSSION_RE.search(sentence):
            return CaseScopeStatus.CASE_SCOPE_UNCERTAIN
        return CaseScopeStatus.SHARED_BOTH
    markers = {match.group(1).casefold() for match in OTHER_PATIENT_RE.finditer(sentence)}
    letter_markers = {token for token in markers if token.isalpha() or token.isdigit()}
    if not letter_markers:
        return CaseScopeStatus.CASE_SCOPE_UNCERTAIN if not active else CaseScopeStatus.ASSIGNED
    if letter_markers & active:
        if letter_markers - active:
            return CaseScopeStatus.CASE_SCOPE_UNCERTAIN
        return CaseScopeStatus.ASSIGNED
    return CaseScopeStatus.CASE_SCOPE_UNCERTAIN


def scope_chunks_for_identifier(
    chunks: list[TextChunk], identifier: str | None
) -> list[TextChunk]:
    if not identifier:
        return chunks

    class _Marker:
        patient_identifier = identifier
        age = None
        sex = None

    return scope_chunks(chunks, _Marker())


def scope_chunks(chunks: list[TextChunk], case: Case) -> list[TextChunk]:
    active = case_markers(case)
    if not active:
        return chunks
    scoped: list[TextChunk] = []
    for chunk in chunks:
        kept: list[str] = []
        for sentence in _sentences(chunk.text):
            status = classify_sentence(sentence, active)
            if status == CaseScopeStatus.ASSIGNED:
                kept.append(sentence)
            elif status == CaseScopeStatus.SHARED_BOTH:
                kept.append(f"[SHARED_BOTH] {sentence}")
            elif OTHER_PATIENT_RE.search(sentence):
                continue
            elif chunk.section in {"References"}:
                continue
            else:
                kept.append(sentence)
        if kept:
            scoped.append(
                TextChunk(
                    paper_id=chunk.paper_id,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    section=chunk.section,
                    chunk_index=chunk.chunk_index,
                    text=" ".join(kept),
                )
            )
    return scoped or chunks


def quote_scope_status(quote: str, case: Case) -> CaseScopeStatus:
    active = case_markers(case)
    if not active:
        return CaseScopeStatus.ASSIGNED
    return classify_sentence(quote, active)


def other_patient_quote(quote: str, case: Case) -> bool:
    active = case_markers(case)
    if not active:
        return False
    markers = {match.group(1).casefold() for match in OTHER_PATIENT_RE.finditer(quote)}
    if not markers:
        return False
    if SHARED_RE.search(quote):
        return False
    return bool(markers - active) and not bool(markers & active)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def normalize_marker_text(text: str) -> str:
    return normalize_text(text)
