from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from app.models import Event, EvidenceType
from app.schemas.extraction import EvidenceReference, SourceEvidenceType
from app.services.chunking import TextChunk
from app.services.evidence_verifier import (
    EvidenceVerifier,
    SENTENCE_SPLIT_RE,
    normalize_text,
)
from app.services.genotype_semantics import (
    genotype_state_is_clear,
    is_genotype_claim,
    parse_genotype,
)


METADATA_SECTIONS = {"Title", "Abstract"}
SKIP_SECTIONS = {"References"}
PRIORITY_IMMUNE_SECTIONS = {
    "Case Report",
    "Case Presentation",
    "Clinical Course",
    "Results",
    "Methods",
    "Unknown",
}
HEDGE_RE = re.compile(
    r"\b(?:may|might|could|suggest(?:s|ed|ing)?|postulat\w*|"
    r"possible delayed|cannot exclude|hypothesi[sz]\w*|"
    r"intriguing to speculate|we hypothesize|remains speculative)\b",
    re.IGNORECASE,
)
PATIENT_ANCHOR_RE = re.compile(
    r"\b(?:our patient|this patient|his exposure|her exposure|"
    r"we hypothesize|intriguing to speculate|cannot exclude|"
    r"for this patient|for our patient)\b",
    re.IGNORECASE,
)
LITERATURE_RE = re.compile(
    r"\b(?:have been reported|has been reported|previous(?:ly)? (?:reported|study)|"
    r"other authors|in melanoma patients)\b",
    re.IGNORECASE,
)
IMMUNE_MARKER_RE = re.compile(
    r"\b(?:cd3|cd8|cd4|nk cells?|tils?|macrophages?|"
    r"t-?cell infiltration|lymphocyt\w* infiltration|"
    r"immune infiltration)\b",
    re.IGNORECASE,
)
IMMUNE_FINDING_RE = re.compile(
    r"\b(?:infiltrat\w*|brisk|were present|was present|demonstrated)\b",
    re.IGNORECASE,
)
FIGURE_RE = re.compile(r"\b(?:fig(?:ure)?\.?\s*\d+)\b", re.IGNORECASE)
PATIENT_GENOTYPE_RE = re.compile(
    r"\b(?:this patient|our patient|the patient|was found to be|"
    r"mutation analysis|molecular testing|harbor(?:s|ed)?|"
    r"sequencing data revealed|yielded wild|detected a|"
    r"status was)\b",
    re.IGNORECASE,
)
TABLE_NOISE_RE = re.compile(
    r"\b(?:provean|sift|polyphen|annovar|allele frequenc|table \d+)\b",
    re.IGNORECASE,
)
HYPHEN_JOIN_RE = re.compile(r"(?<=\w)-\s*\n\s*(?=\w)")


@dataclass(frozen=True)
class RecallHit:
    kind: str
    status: str
    quote: str
    page: int
    section: str | None
    source: str
    reason: str
    variable_name: str | None = None
    value: str | None = None
    alternative_type: str | None = None
    gene: str | None = None
    state: str | None = None
    evidence_type: SourceEvidenceType = SourceEvidenceType.OBSERVED_FACT
    extra: dict = field(default_factory=dict)

    def as_reference(self) -> EvidenceReference:
        return EvidenceReference(
            page=max(self.page, 1),
            quote=self.quote,
            section=self.section,
            evidence_type=self.evidence_type,
        )


def iter_body_sentences(
    pages: dict[int, str],
    chunks: list[TextChunk],
) -> Iterable[tuple[int, str | None, str]]:
    for page, text in sorted(pages.items()):
        joined = HYPHEN_JOIN_RE.sub("", text)
        joined = re.sub(r"\s+", " ", joined)
        for raw in SENTENCE_SPLIT_RE.split(joined):
            sentence = raw.strip()
            if len(sentence) < 20:
                continue
            section = _section_for_sentence(chunks, page, sentence)
            if section in SKIP_SECTIONS:
                continue
            yield page, section, sentence


def _section_for_sentence(
    chunks: list[TextChunk], page: int, sentence: str
) -> str | None:
    needle = normalize_text(sentence[:80])
    for chunk in chunks:
        if chunk.page_start <= page <= chunk.page_end:
            if needle and needle in normalize_text(chunk.text):
                return chunk.section
    for chunk in chunks:
        if chunk.page_start <= page <= chunk.page_end:
            return chunk.section
    return None


def classify_explanatory_alternative(statement: str, quote: str = "") -> str | None:
    text = normalize_text(f"{statement} {quote}")
    if not HEDGE_RE.search(text) and not re.search(
        r"\b(?:delay|years? (?:prior|earlier)|contribut|cannot exclude)\b",
        text,
    ):
        return None
    if LITERATURE_RE.search(text) and not PATIENT_ANCHOR_RE.search(text):
        return None
    if re.search(r"\b(?:ipilimumab|nivolumab|pembrolizumab|anti-ctla-4|checkpoint)\b", text) and re.search(
        r"\b(?:delay|years? (?:prior|earlier|after)|contribut|unusual)\b",
        text,
    ):
        return "delayed_immunotherapy_effect"
    if re.search(r"\b(?:dtap|adacel|vaccin)\b", text):
        return "vaccination_associated_regression"
    if re.search(r"\b(?:infection|operative trauma|surgery|postoperative)\b", text) and re.search(
        r"\b(?:immune|innate|hypothes|augment)\b",
        text,
    ):
        return "infection_or_surgery_immune_trigger"
    if re.search(r"\b(?:pyrin|mefv|inflammasome)\b", text):
        return "pyrin_related_predisposition"
    if re.search(r"\bbiopsy\b", text) and re.search(
        r"\b(?:inflam|immune|contribut)\b", text
    ):
        return "biopsy_induced_inflammation"
    if PATIENT_ANCHOR_RE.search(text) and re.search(
        r"\b(?:regression|response|cause)\b", text
    ):
        return "author_suggested_regression_mechanism"
    return None


def scan_genotype_text(
    pages: dict[int, str],
    chunks: list[TextChunk],
) -> list[RecallHit]:
    hits: list[RecallHit] = []
    best: dict[str, RecallHit] = {}
    for page, section, sentence in iter_body_sentences(pages, chunks):
        if section in METADATA_SECTIONS:
            continue
        if not is_genotype_claim(sentence):
            continue
        if TABLE_NOISE_RE.search(sentence) and not PATIENT_GENOTYPE_RE.search(sentence):
            continue
        if len(sentence) > 400 and not PATIENT_GENOTYPE_RE.search(sentence):
            continue
        parsed = parse_genotype(sentence)
        key = parsed.gene if parsed else normalize_text(sentence)[:40]
        quote = _factual_genotype_quote(sentence)
        parsed = parse_genotype(quote) or parsed
        if genotype_state_is_clear(parsed):
            candidate = RecallHit(
                kind="genotype",
                status="READY",
                quote=quote,
                page=page,
                section=section,
                source="text_scan",
                reason="Verified-body genotype sentence with a clear parser state",
                variable_name=f"{parsed.gene} genotype",
                value=parsed.state,
                gene=parsed.gene,
                state=parsed.state,
                extra={"protein_change": parsed.protein_change, "origin": parsed.origin},
            )
        else:
            candidate = RecallHit(
                kind="genotype",
                status="RECONCILIATION_REQUIRED",
                quote=sentence,
                page=page,
                section=section,
                source="text_scan",
                reason="Genotype language is present but the parser state is not clear",
                gene=parsed.gene if parsed else None,
                state=parsed.state if parsed else None,
            )
        previous = best.get(key)
        if previous is None or _genotype_priority(candidate) > _genotype_priority(previous):
            best[key] = candidate
    hits.extend(best.values())
    return hits


def _genotype_priority(hit: RecallHit) -> int:
    rank = {
        "WILD_TYPE": 6,
        "VARIANT_PRESENT": 5,
        "NOT_DETECTED": 4,
        "MUTATED": 3,
        "DELETED": 2,
        "AMPLIFIED": 2,
        "UNKNOWN": 0,
    }
    score = rank.get(hit.state or "", 0)
    if hit.status == "READY":
        score += 10
    if hit.extra.get("origin") == "GERMLINE":
        score += 1
    return score


def scan_immune_pathology(
    pages: dict[int, str],
    chunks: list[TextChunk],
) -> list[RecallHit]:
    hits: list[RecallHit] = []
    seen: set[str] = set()
    prioritized: list[tuple[int, int, str | None, str]] = []
    for page, section, sentence in iter_body_sentences(pages, chunks):
        if not IMMUNE_MARKER_RE.search(sentence):
            continue
        if not IMMUNE_FINDING_RE.search(sentence):
            continue
        if section == "Methods" and not re.search(
            r"\b(?:demonstrated|brisk|infiltration with)\b", sentence, re.I
        ):
            continue
        if section == "Discussion" and not FIGURE_RE.search(sentence):
            if not re.search(r"\b(?:demonstrated|brisk infiltration)\b", sentence, re.I):
                continue
        priority = 0
        if section in PRIORITY_IMMUNE_SECTIONS or FIGURE_RE.search(sentence):
            priority = 1
        if re.search(r"\b(?:immunohistochem|patholog|figure caption)\b", sentence, re.I):
            priority = 2
        prioritized.append((priority, page, section, sentence))
    for _priority, page, section, sentence in sorted(prioritized, reverse=True):
        key = normalize_text(sentence)
        if key in seen:
            continue
        seen.add(key)
        hits.append(
            RecallHit(
                kind="immune",
                status="READY",
                quote=sentence,
                page=page,
                section=section,
                source="immune_pathology_pass",
                reason="Direct immune-infiltration sentence in pathology/IHC/figure text",
                variable_name=_immune_variable_name(sentence),
                value=sentence,
            )
        )
    return hits


def _immune_variable_name(sentence: str) -> str:
    markers = []
    for marker in ("CD3", "CD8", "CD4", "NK", "TIL", "macrophage"):
        if re.search(rf"\b{marker}s?\b", sentence, re.IGNORECASE):
            markers.append(marker)
    if markers:
        return f"{'/'.join(markers)} infiltration"
    return "immune-cell infiltration"


def scan_explanatory_alternatives(
    pages: dict[int, str],
    chunks: list[TextChunk],
) -> list[RecallHit]:
    hits: list[RecallHit] = []
    seen: set[str] = set()
    for page, section, sentence in iter_body_sentences(pages, chunks):
        if section in METADATA_SECTIONS:
            continue
        alternative_type = classify_explanatory_alternative(sentence, sentence)
        if alternative_type is None:
            continue
        if alternative_type in seen:
            continue
        seen.add(alternative_type)
        hits.append(
            RecallHit(
                kind="alternative",
                status="READY",
                quote=sentence,
                page=page,
                section=section,
                source="alternative_pass",
                reason="Author-hedged alternative explanation; not an observation",
                alternative_type=alternative_type,
                value=sentence,
                evidence_type=SourceEvidenceType.AUTHOR_INTERPRETATION,
            )
        )
    return hits


def reconcile_phase2_genotypes(
    events: list[Event],
    existing_keys: set[tuple[str, str]],
    pages: dict[int, str],
    chunks: list[TextChunk],
    event_quotes: dict[int, tuple[int | None, str | None, str]],
) -> list[RecallHit]:
    hits: list[RecallHit] = []
    for event in events:
        if not is_genotype_claim(event.description):
            continue
        parsed = parse_genotype(event.description)
        key = (
            parsed.gene if parsed else "UNKNOWN",
            parsed.state if parsed else "UNKNOWN",
        )
        if parsed and (parsed.gene, parsed.state) in existing_keys:
            continue
        page, section, quote = _event_quote(event, event_quotes, pages, chunks)
        if quote and genotype_state_is_clear(parsed):
            hits.append(
                RecallHit(
                    kind="genotype",
                    status="READY",
                    quote=quote,
                    page=page or 1,
                    section=section,
                    source="phase2_event",
                    reason="PHASE 2 Event reconciled to a verified genotype quote",
                    variable_name=f"{parsed.gene} genotype",
                    value=parsed.state,
                    gene=parsed.gene,
                    state=parsed.state,
                    extra={"event_id": event.id},
                )
            )
        else:
            hits.append(
                RecallHit(
                    kind="genotype",
                    status="RECONCILIATION_REQUIRED",
                    quote=quote or event.description,
                    page=page or 1,
                    section=section,
                    source="phase2_event",
                    reason=(
                        "PHASE 2 has a gene finding but the quote is unverified "
                        "or the parser state is unclear; no fact was created"
                    ),
                    gene=parsed.gene if parsed else None,
                    state=parsed.state if parsed else None,
                    extra={"event_id": event.id},
                )
            )
    return hits


def _event_quote(
    event: Event,
    event_quotes: dict[int, tuple[int | None, str | None, str]],
    pages: dict[int, str],
    chunks: list[TextChunk],
) -> tuple[int | None, str | None, str | None]:
    stored = event_quotes.get(event.id)
    if stored and stored[2]:
        return stored
    parsed = parse_genotype(event.description)
    needle = normalize_text(event.description[:80])
    for page, section, sentence in iter_body_sentences(pages, chunks):
        if section in METADATA_SECTIONS:
            continue
        if needle and needle in normalize_text(sentence):
            return page, section, sentence
        if parsed and parsed.gene:
            if parsed.gene.casefold() in sentence.casefold() and is_genotype_claim(sentence):
                return page, section, sentence
    return None, None, None


def verify_hit(verifier: EvidenceVerifier, hit: RecallHit) -> RecallHit:
    verified = verifier.verify(hit.as_reference())
    if not verified.verified:
        return RecallHit(
            kind=hit.kind,
            status="RECONCILIATION_REQUIRED",
            quote=hit.quote,
            page=hit.page,
            section=hit.section,
            source=hit.source,
            reason=verified.reason or "Quote was not verified in the PDF body",
            variable_name=hit.variable_name,
            value=hit.value,
            alternative_type=hit.alternative_type,
            gene=hit.gene,
            state=hit.state,
            evidence_type=hit.evidence_type,
            extra=hit.extra,
        )
    if hit.kind == "genotype" and hit.status == "READY":
        return hit
    if hit.kind == "alternative":
        if verified.evidence_type != EvidenceType.AUTHOR_INTERPRETATION:
            return RecallHit(
                kind=hit.kind,
                status="RECONCILIATION_REQUIRED",
                quote=hit.quote,
                page=hit.page,
                section=hit.section,
                source=hit.source,
                reason="Hedged alternative did not classify as AUTHOR_INTERPRETATION",
                alternative_type=hit.alternative_type,
                evidence_type=hit.evidence_type,
                extra=hit.extra,
            )
    elif verified.evidence_type != EvidenceType.OBSERVED_FACT:
        return RecallHit(
            kind=hit.kind,
            status="RECONCILIATION_REQUIRED",
            quote=hit.quote,
            page=hit.page,
            section=hit.section,
            source=hit.source,
            reason="Candidate did not verify as OBSERVED_FACT",
            variable_name=hit.variable_name,
            value=hit.value,
            gene=hit.gene,
            state=hit.state,
            extra=hit.extra,
        )
    return hit


def _factual_genotype_quote(sentence: str) -> str:
    cut = re.split(
        r"\b(?:consistent with|suggest(?:s|ing)? that|other authors|"
        r"altogether|while case reports|these results suggest)\b",
        sentence,
        maxsplit=1,
        flags=re.I,
    )[0].strip(" ;,")
    if 24 <= len(cut) <= 320:
        return cut
    return sentence[:320]


def core_entity_signature(kind: str, *parts: str | None) -> tuple[str, ...]:
    cleaned = [kind]
    for part in parts:
        cleaned.append(normalize_text(part or "") or "_")
    return tuple(cleaned)
