from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.models import RegressionEpisode, RegressionExtent
from app.services.evidence_verifier import normalize_text


CONFIRMATION_RE = re.compile(
    r"\b(?:did not reveal|did not detect|confirming|confirmation|"
    r"follow-up|still absent|no longer|first explicitly timed observation|"
    r"ct scans?|ultrasound|absent at)\b",
    re.I,
)
RECURRENCE_RE = re.compile(
    r"\b(?:recurrence|regrew|re-?growth|again after|second regression|"
    r"new nodule|new metastases)\b",
    re.I,
)
MILESTONE_LABELS = (
    (r"\b(?:decreased|reduced|smaller|partial)\b", "first_observed_reduction"),
    (r"\b(?:disappeared|vanished|complete regression|resolved)\b", "complete_disappearance"),
    (r"\b(?:confirm|did not (?:reveal|detect)|follow-up)\b", "confirmation"),
    (r"\b(?:still absent|no evidence of recurrence)\b", "follow_up"),
)


@dataclass
class CanonicalEpisode:
    case_id: int
    episode_type: str
    extent: str
    anatomic_scope: str
    description: str
    associated_lesion_ids: list[int] = field(default_factory=list)
    associated_collection_ids: list[int] = field(default_factory=list)
    associated_event_ids: list[int] = field(default_factory=list)
    source_episode_ids: list[int] = field(default_factory=list)
    milestones: list[dict[str, str]] = field(default_factory=list)
    extent_transition: str | None = None
    spontaneous_status: str | None = None
    confidence: float = 0.85
    action: str = "KEPT"


def canonicalize_episodes(
    episodes: list[RegressionEpisode],
    *,
    lesion_organs: dict[int, str] | None = None,
) -> list[CanonicalEpisode]:
    if not episodes:
        return []
    groups: list[list[RegressionEpisode]] = []
    for episode in sorted(episodes, key=lambda item: item.episode_index):
        placed = False
        for group in groups:
            if _same_continuous_course(group[0], episode, lesion_organs or {}):
                group.append(episode)
                placed = True
                break
        if not placed:
            groups.append([episode])
    canonical: list[CanonicalEpisode] = []
    for group in groups:
        canonical.append(_collapse_group(group))
    return canonical


def _same_continuous_course(
    left: RegressionEpisode,
    right: RegressionEpisode,
    lesion_organs: dict[int, str],
) -> bool:
    if left.case_id != right.case_id:
        return False
    left_text = normalize_text(left.description or "")
    right_text = normalize_text(right.description or "")
    if RECURRENCE_RE.search(left_text) or RECURRENCE_RE.search(right_text):
        if _organ_scope(left, lesion_organs) != _organ_scope(right, lesion_organs):
            return False
        return False
    left_scope = _organ_scope(left, lesion_organs)
    right_scope = _organ_scope(right, lesion_organs)
    left_lesions = set(left.associated_lesion_ids or [])
    right_lesions = set(right.associated_lesion_ids or [])
    shared_lesion = bool(left_lesions and right_lesions and left_lesions & right_lesions)
    confirmation = bool(CONFIRMATION_RE.search(left_text) or CONFIRMATION_RE.search(right_text))
    partial_to_complete = {left.extent.value, right.extent.value} == {
        RegressionExtent.PARTIAL.value,
        RegressionExtent.COMPLETE.value,
    }
    same_or_unspecified = (
        left_scope == right_scope
        or "UNSPECIFIED" in left_scope
        or "UNSPECIFIED" in right_scope
    )
    if shared_lesion and (confirmation or partial_to_complete):
        return True
    if same_or_unspecified and (confirmation or partial_to_complete):
        return True
    if left_scope == right_scope and left_scope != "UNSPECIFIED":
        return True
    return False


def _organ_scope(episode: RegressionEpisode, lesion_organs: dict[int, str]) -> str:
    if episode.anatomic_scope:
        return episode.anatomic_scope
    for lesion_id in episode.associated_lesion_ids or []:
        if lesion_id in lesion_organs:
            return lesion_organs[lesion_id]
    text = normalize_text(episode.description or "")
    for token, organ in (
        ("sole", "SKIN_PRIMARY"),
        ("primary", "SKIN_PRIMARY"),
        ("ankle", "SKIN_PRIMARY"),
        ("thigh", "SKIN"),
        ("inguinal", "LYMPH_NODE"),
        ("lung", "LUNG"),
        ("pulmon", "LUNG"),
        ("brain", "BRAIN"),
        ("nevi", "NEVI"),
        ("neck", "LYMPH_NODE"),
    ):
        if token in text:
            return organ
    return "UNSPECIFIED"


def _collapse_group(group: list[RegressionEpisode]) -> CanonicalEpisode:
    first = group[0]
    extents = [item.extent.value if hasattr(item.extent, "value") else item.extent for item in group]
    extent = _final_extent(extents)
    transition = None
    if RegressionExtent.PARTIAL.value in extents and RegressionExtent.COMPLETE.value in extents:
        transition = "PARTIAL_TO_COMPLETE"
        extent = RegressionExtent.COMPLETE.value
    lesion_ids: list[int] = []
    event_ids: list[int] = []
    for item in group:
        for lesion_id in item.associated_lesion_ids or []:
            if lesion_id not in lesion_ids:
                lesion_ids.append(lesion_id)
        for event_id in item.associated_event_ids or []:
            if event_id not in event_ids:
                event_ids.append(event_id)
    action = "MERGED" if len(group) > 1 else "KEPT"
    return CanonicalEpisode(
        case_id=first.case_id,
        episode_type=(
            first.episode_type.value
            if hasattr(first.episode_type, "value")
            else first.episode_type
        ),
        extent=extent,
        anatomic_scope=_organ_scope(first, {}),
        description=first.description or "",
        associated_lesion_ids=lesion_ids,
        associated_event_ids=event_ids,
        source_episode_ids=[item.id for item in group],
        milestones=_milestones(group),
        extent_transition=transition,
        spontaneous_status=first.spontaneous_status,
        action=action,
    )


def _final_extent(extents: list[str]) -> str:
    if RegressionExtent.COMPLETE.value in extents:
        return RegressionExtent.COMPLETE.value
    if RegressionExtent.PARTIAL.value in extents:
        return RegressionExtent.PARTIAL.value
    return extents[0] if extents else RegressionExtent.UNCERTAIN.value


def _milestones(group: list[RegressionEpisode]) -> list[dict[str, str]]:
    rows = []
    seen: set[str] = set()
    for item in group:
        text = item.description or ""
        label = "confirmation"
        for pattern, name in MILESTONE_LABELS:
            if re.search(pattern, text, re.I):
                label = name
                break
        if label in seen and label == "confirmation":
            label = "follow_up"
        seen.add(label)
        rows.append({"label": label, "text": text, "source_episode_id": str(item.id)})
    return rows


def should_split_collapsed_case(
    episodes: list[RegressionEpisode],
    organ_mentions: list[str],
) -> list[str]:
    """If one case-level episode covers distinct organ courses, return those organs."""
    if len(episodes) != 1:
        return []
    distinct = []
    for organ in ("LUNG", "LYMPH_NODE", "SKIN_PRIMARY", "NEVI", "BRAIN"):
        if organ in organ_mentions:
            distinct.append(organ)
    if len(distinct) >= 2:
        return distinct
    return []
