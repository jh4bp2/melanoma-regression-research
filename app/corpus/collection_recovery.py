from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.corpus.polarity import is_literature_statement
from app.models import CollectionCountSemantics, CollectionMembershipStatus, LesionScopeKind
from app.services.evidence_verifier import normalize_text
from app.services.lesion_identity import parse_lesion_text


COLLECTION_TRIGGER = re.compile(
    r"\b(?:multiple|numerous|several|bilateral|multifocal|"
    r"multiple nodules|multiple metastases|multiple lymph nodes|"
    r"multiple nevi|all (?:her |his |the )?nevi|numerous lesions|"
    r"all nevi|melanocytic nevi|remaining nevi|other nevi)\b",
    re.I,
)

ORGAN_MAP = (
    (r"\b(?:pulmonary|pulmonar\w*|lung|chest-?film|chest film)\b", "LUNG", "pulmonary metastases"),
    (r"\b(?:brain|cerebral|intracranial)\b", "BRAIN", "brain metastases"),
    (r"\b(?:hepatic|liver)\b", "LIVER", "hepatic metastases"),
    (r"\b(?:bone|osseous|skeletal)\b", "BONE", "bone metastases"),
    (r"\b(?:in-?transit)\b", "SKIN", "in-transit metastases"),
    (r"\b(?:nevi|nevus|naev)\b", "SKIN", "melanocytic nevi"),
    (r"\b(?:lymph[- ]?node|inguinal nodes|iliac nodes|cervical lymphaden)\b", "LYMPH_NODE", "lymph-node metastases"),
    (r"\b(?:cutaneous|skin lesions|subcutaneous)\b", "SKIN", "cutaneous lesions"),
)

EXACT_COUNT_RE = re.compile(
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    re.I,
)
APPROX_COUNT_RE = re.compile(r"\b(?:approximately|about|~)\s*\d+", re.I)


@dataclass
class CollectionCandidate:
    collection_type: LesionScopeKind
    organ: str
    region: str | None
    laterality: str | None
    source_label: str
    normalized_label: str
    reported_count: int | None
    count_semantics: CollectionCountSemantics
    membership_status: CollectionMembershipStatus
    member_lesion_ids: list[int] = field(default_factory=list)
    confidence: float = 0.8
    source_observation_ids: list[int] = field(default_factory=list)
    reason: str = ""


def recover_collections(
    texts: list[tuple[str, str | None, int | None]],
    lesions: list[object],
) -> list[CollectionCandidate]:
    """texts: (patient_fact_text, quote, observation_id)."""
    buckets: dict[str, CollectionCandidate] = {}
    for text, quote, observation_id in texts:
        for candidate in _candidates_from_text(text, quote, observation_id):
            key = f"{candidate.organ}|{candidate.normalized_label}"
            existing = buckets.get(key)
            if existing is None:
                buckets[key] = candidate
                continue
            if observation_id is not None:
                existing.source_observation_ids.append(observation_id)
            if candidate.reported_count and not existing.reported_count:
                existing.reported_count = candidate.reported_count
                existing.count_semantics = candidate.count_semantics
    recovered = []
    for candidate in buckets.values():
        _assign_members(candidate, lesions)
        if _already_fully_individualized(candidate, lesions):
            continue
        recovered.append(candidate)
    return recovered


def _candidates_from_text(
    text: str,
    quote: str | None,
    observation_id: int | None,
) -> list[CollectionCandidate]:
    blob = " ".join(part for part in (text, quote) if part)
    normalized = normalize_text(blob)
    if not COLLECTION_TRIGGER.search(normalized):
        return []
    if is_literature_statement(blob):
        return []
    parsed = parse_lesion_text(text)
    count, semantics = _count_semantics(normalized)
    found = []
    for organ, label, collection_type in _organs_and_types(normalized):
        found.append(
            CollectionCandidate(
                collection_type=collection_type,
                organ=organ,
                region=parsed.anatomical_location if parsed else None,
                laterality=parsed.laterality if parsed else None,
                source_label=text.strip()[:240],
                normalized_label=label,
                reported_count=count,
                count_semantics=semantics,
                membership_status=CollectionMembershipStatus.COLLECTION_ONLY,
                source_observation_ids=[observation_id] if observation_id else [],
                reason="Verified multifocal wording without inventing unnamed members.",
            )
        )
    return found


NEGATED_ORGAN = {
    "BONE": re.compile(r"\bno bones? metastases\b"),
    "LUNG": re.compile(r"\bno (?:lung|pulmonary) metastases\b"),
    "BRAIN": re.compile(r"\bno (?:brain|cerebral) metastases\b"),
    "LIVER": re.compile(
        r"\bno (?:liver|hepatic) metastases\b|"
        r"\bno evidence of (?:metastatic melanoma )?in the liver\b|"
        r"\bliver scan (?:were|was) normal\b|"
        r"\bnormal\b.{0,40}\bliver scan\b|"
        r"\bliver scan\b.{0,40}\bnormal\b"
    ),
    "LYMPH_NODE": re.compile(r"\bno (?:lymph[- ]?node) metastases\b"),
}


def _organs_and_types(normalized: str) -> list[tuple[str, str, LesionScopeKind]]:
    found: list[tuple[str, str, LesionScopeKind]] = []
    seen: set[str] = set()
    for pattern, organ, label in ORGAN_MAP:
        if not re.search(pattern, normalized):
            continue
        if organ in seen:
            continue
        if organ in NEGATED_ORGAN and NEGATED_ORGAN[organ].search(normalized):
            continue
        if organ == "SKIN" and re.search(r"\b(?:nevi|nevus|naev)\b", normalized):
            found.append(
                (organ, "multiple melanocytic nevi", LesionScopeKind.MELANOCYTIC_NEVI_GROUP)
            )
        elif re.search(r"\b(?:in-?transit|multifocal cutaneous)\b", normalized):
            found.append((organ, label, LesionScopeKind.MULTIFOCAL_DISEASE))
        else:
            found.append(
                (organ, f"multiple {label}", LesionScopeKind.METASTATIC_LESION_GROUP)
            )
        seen.add(organ)
    if not found and re.search(r"\b(?:nevi|nevus|naev)\b", normalized):
        found.append(
            ("SKIN", "multiple melanocytic nevi", LesionScopeKind.MELANOCYTIC_NEVI_GROUP)
        )
    return found


def _count_semantics(normalized: str) -> tuple[int | None, CollectionCountSemantics]:
    if APPROX_COUNT_RE.search(normalized):
        number = re.search(r"\d+", normalized)
        return (int(number.group()) if number else None, CollectionCountSemantics.APPROXIMATE)
    if re.search(r"\b(?:multiple|numerous|several|all)\b", normalized):
        return None, CollectionCountSemantics.MULTIPLE_UNSPECIFIED
    exact = EXACT_COUNT_RE.search(normalized)
    if exact and re.search(r"\b(?:two|three|four|\d+)\s+(?:brain|measured)\b", normalized):
        words = {"two": 2, "three": 3, "four": 4}
        raw = exact.group().lower()
        return words.get(raw, int(raw) if raw.isdigit() else None), CollectionCountSemantics.EXACT
    return None, CollectionCountSemantics.UNKNOWN


def _assign_members(candidate: CollectionCandidate, lesions: list[object]) -> None:
    members = []
    for lesion in lesions:
        organ = getattr(lesion, "organ", None)
        name = normalize_text(
            " ".join(
                [
                    getattr(lesion, "canonical_name", "") or "",
                    getattr(lesion, "anatomical_location", "") or "",
                    organ or "",
                ]
            )
        )
        if organ == candidate.organ or candidate.organ.lower() in name:
            if candidate.collection_type == LesionScopeKind.MELANOCYTIC_NEVI_GROUP:
                if not re.search(r"\b(?:nev|naev)\b", name):
                    continue
            if _is_named_individual(lesion) or organ == candidate.organ:
                if not re.search(r"\b(?:multiple|numerous|several|all nevi)\b", name):
                    members.append(getattr(lesion, "id"))
    candidate.member_lesion_ids = members
    if not members:
        candidate.membership_status = CollectionMembershipStatus.COLLECTION_ONLY
        return
    if candidate.reported_count and len(members) >= candidate.reported_count:
        candidate.membership_status = CollectionMembershipStatus.INDIVIDUAL_MEMBERS_KNOWN
    else:
        candidate.membership_status = CollectionMembershipStatus.PARTIAL_MEMBERS_KNOWN


def _is_named_individual(lesion: object) -> bool:
    name = normalize_text(getattr(lesion, "canonical_name", "") or "")
    location = getattr(lesion, "anatomical_location", None)
    if re.search(r"\b(?:multiple|numerous|several|all nevi)\b", name):
        return False
    return bool(location or re.search(r"\b(?:right|left|lower|upper|lobe|flank)\b", name))


def _already_fully_individualized(
    candidate: CollectionCandidate, lesions: list[object]
) -> bool:
    """Do not also create a collection when the only instances are named individuals."""
    if candidate.organ in {"BRAIN"} and candidate.member_lesion_ids:
        named = [
            lesion
            for lesion in lesions
            if getattr(lesion, "organ", None) == "BRAIN"
            and _is_named_individual(lesion)
        ]
        source = normalize_text(candidate.source_label)
        if len(named) >= 2:
            if re.search(r"\b\d+\s*/\s*\d+\s*mm\b", source) or "measuring" in source:
                return True
            if not re.search(r"\bmultiple (?:brain|cerebral) metastases\b", source):
                return True
    return False
