from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import Event, EventType
from app.services.evidence_verifier import normalize_text
from app.services.lesion_identity import parse_lesion_text


@dataclass(frozen=True)
class EpisodeDraft:
    episode_index: int
    episode_type: str
    extent: str
    spontaneous_status: str
    description: str
    associated_event_ids: list[int]
    organ_key: str
    confidence: float


SITE_KEYS = (
    ("axilla", "AXILLA"),
    ("axillary", "AXILLA"),
    ("hepatic", "LIVER"),
    ("liver", "LIVER"),
    ("heel", "HEEL"),
    ("thigh", "THIGH"),
    ("fingertip", "FINGERTIP"),
    ("toe", "TOE"),
    ("lung", "LUNG"),
    ("intransit", "IN_TRANSIT"),
    ("in-transit", "IN_TRANSIT"),
    ("in transit", "IN_TRANSIT"),
    ("skin nodule", "SKIN"),
    ("cutaneous", "SKIN"),
    ("popliteal", "SKIN"),
    ("mixed response", "IMAGING_MIXED"),
)
RESTATEMENT_STOP = {
    "patient",
    "showed",
    "noted",
    "after",
    "before",
    "during",
    "with",
    "that",
    "this",
    "from",
    "were",
    "been",
    "into",
    "over",
    "also",
    "had",
    "the",
    "and",
    "all",
}


def build_regression_episodes(events: list[Event]) -> list[EpisodeDraft]:
    treatment_ids = {
        event.id
        for event in events
        if event.event_type in {EventType.TREATMENT, EventType.DRUG_EXPOSURE}
        or re.search(
            r"\b(?:pembrolizumab|ipilimumab|nivolumab|dabrafenib|trametinib|"
            r"radiotherap|interferon)\b",
            normalize_text(event.description),
        )
    }
    drafts: dict[str, EpisodeDraft] = {}
    index = 1
    for event in events:
        if event.event_type != EventType.TUMOR_REGRESSION and not re.search(
            r"\b(?:spontaneous regression|complete regression|"
            r"resolved|vanished|disappeared|diminution)\b",
            normalize_text(event.description),
        ):
            continue
        organ = _organ_key(event.description)
        named_treatment = bool(
            re.search(
                r"\b(?:pembrolizumab|ipilimumab|nivolumab|dabrafenib|"
                r"trametinib|response to)\b",
                normalize_text(event.description),
            )
        )
        after_treatment = event.relation_to_regression == "AFTER" and bool(treatment_ids)
        if named_treatment or (
            after_treatment
            and not re.search(r"\bspontaneous\b", normalize_text(event.description))
        ):
            episode_type = "TREATMENT_ASSOCIATED"
            spontaneous = "NO"
        elif re.search(r"\bspontaneous\b", normalize_text(event.description)):
            episode_type = "SPONTANEOUS"
            spontaneous = "YES"
        elif event.relation_to_regression in {"BEFORE", "DURING"}:
            episode_type = "SPONTANEOUS"
            spontaneous = "YES"
        else:
            episode_type = "UNCERTAIN"
            spontaneous = "UNCERTAIN"
        restatement = _restatement_match(drafts, organ, event.description, extent=_extent(event.description, "UNCERTAIN"))
        if restatement is not None:
            existing = drafts[restatement]
            drafts[restatement] = EpisodeDraft(
                episode_index=existing.episode_index,
                episode_type=existing.episode_type
                if existing.episode_type == episode_type
                else "UNCERTAIN",
                extent=_extent(event.description, existing.extent),
                spontaneous_status=existing.spontaneous_status,
                description=existing.description,
                associated_event_ids=[*existing.associated_event_ids, event.id],
                organ_key=existing.organ_key,
                confidence=min(existing.confidence, 0.8),
            )
            continue
        drafts[organ] = EpisodeDraft(
            episode_index=index,
            episode_type=episode_type,
            extent=_extent(event.description, "UNCERTAIN"),
            spontaneous_status=spontaneous,
            description=event.description,
            associated_event_ids=[event.id],
            organ_key=organ,
            confidence=0.8,
        )
        index += 1
    return sorted(drafts.values(), key=lambda row: row.episode_index)


def _organ_key(text: str) -> str:
    normalized = normalize_text(text)
    for token, key in SITE_KEYS:
        if token in normalized:
            return key
    parsed = parse_lesion_text(text)
    if parsed and parsed.organ:
        return parsed.organ
    return f"UNSPECIFIED:{_restatement_key(normalized)}"


def _restatement_key(text: str) -> str:
    tokens = [
        token
        for token in re.findall(r"[a-z]{4,}", normalize_text(text))
        if token not in RESTATEMENT_STOP
    ]
    return " ".join(sorted(set(tokens))[:8]) or normalize_text(text)[:40]


def _restatement_match(
    drafts: dict[str, EpisodeDraft],
    organ: str,
    description: str,
    extent: str,
) -> str | None:
    if organ in drafts:
        return organ
    incoming = set(_restatement_key(description).split())
    for key, existing in drafts.items():
        if existing.organ_key != organ and not (
            existing.organ_key.startswith("UNSPECIFIED:")
            and organ.startswith("UNSPECIFIED:")
        ):
            continue
        current = set(_restatement_key(existing.description).split())
        overlap = len(incoming & current) / max(len(incoming | current), 1)
        same_extent = existing.extent == extent or extent == "UNCERTAIN"
        if overlap >= 0.45 and same_extent:
            return key
    return None


def _extent(text: str, fallback: str) -> str:
    normalized = normalize_text(text)
    if re.search(r"\bcomplete\b|\bno malignancy\b|\bvanished\b|\bdisappeared\b", normalized):
        return "COMPLETE"
    if re.search(r"\bpartial\b|\bsmaller\b|\bdecreased\b|\bdiminution\b", normalized):
        return "PARTIAL"
    return fallback
