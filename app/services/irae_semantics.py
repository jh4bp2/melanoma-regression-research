from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import Event, EventType
from app.services.evidence_verifier import normalize_text


IRAE_PATTERNS = (
    (r"\b(?:hepatotoxicity|hepatitis|ast|alt)\b", "hepatotoxicity", "hepatic"),
    (r"\bpolymyositis\b", "polymyositis", "musculoskeletal"),
    (r"\bmyasthenia\b", "myasthenia_gravis", "neuromuscular"),
    (r"\bcolitis\b|\b(?:persistent )?(?:diarrhea|diarrhoea)\b", "colitis_or_diarrhea", "gastrointestinal"),
    (r"\bpneumonitis\b", "pneumonitis", "pulmonary"),
    (r"\bendocrinopath", "endocrinopathy", "endocrine"),
    (r"\bir(?:ae|aes)\b|immune-related adverse", "immune_related_adverse_event", "systemic"),
)

CHECKPOINT_RE = re.compile(
    r"\b(?:ipilimumab|nivolumab|pembrolizumab|anti-?pd-?1|anti-?ctla-?4|"
    r"checkpoint)\b",
    re.IGNORECASE,
)
GRADE_RE = re.compile(r"\bgrade\s*([1-5])\b", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedIrae:
    event_type: str
    organ_system: str
    grade: str | None
    onset_relation_to_treatment: str | None
    resolution_status: str | None
    description: str
    event_id: int | None


def parse_irae(text: str, event: Event | None = None) -> ParsedIrae | None:
    normalized = normalize_text(text)
    match = next(
        (
            (name, organ)
            for pattern, name, organ in IRAE_PATTERNS
            if re.search(pattern, normalized)
        ),
        None,
    )
    if match is None:
        return None
    if not (
        CHECKPOINT_RE.search(normalized)
        or (event is not None and CHECKPOINT_RE.search(event.description))
        or re.search(r"\bir(?:ae|aes)\b|checkpoint inhibitor toxicity", normalized)
    ):
        if match[0] not in {
            "hepatotoxicity",
            "polymyositis",
            "myasthenia_gravis",
            "immune_related_adverse_event",
        }:
            return None
    grade_match = GRADE_RE.search(text)
    relation = None
    if event is not None:
        relation = event.relation_to_regression
    elif re.search(r"\bafter the first\b", normalized):
        relation = "AFTER_TREATMENT"
    resolution = None
    if re.search(r"\bimprov", normalized):
        resolution = "IMPROVED"
    return ParsedIrae(
        event_type=match[0],
        organ_system=match[1],
        grade=f"grade {grade_match.group(1)}" if grade_match else None,
        onset_relation_to_treatment=relation,
        resolution_status=resolution,
        description=text.strip(),
        event_id=event.id if event is not None else None,
    )


def irae_events(events: list[Event]) -> list[tuple[Event, ParsedIrae]]:
    found: list[tuple[Event, ParsedIrae]] = []
    for event in events:
        parsed = parse_irae(event.description, event)
        if parsed is not None:
            found.append((event, parsed))
    return found


def canonical_irae_groups(
    events: list[Event],
) -> list[tuple[ParsedIrae, list[Event]]]:
    grouped: dict[str, list[tuple[Event, ParsedIrae]]] = {}
    for event, parsed in irae_events(events):
        grouped.setdefault(parsed.event_type, []).append((event, parsed))
    canonical: list[tuple[ParsedIrae, list[Event]]] = []
    for event_type, rows in grouped.items():
        first_event, first = rows[0]
        grades = [row[1].grade for row in rows if row[1].grade]
        relations = [
            row[1].onset_relation_to_treatment
            for row in rows
            if row[1].onset_relation_to_treatment
        ]
        resolutions = [
            row[1].resolution_status for row in rows if row[1].resolution_status
        ]
        merged = ParsedIrae(
            event_type=event_type,
            organ_system=first.organ_system,
            grade=grades[0] if grades else None,
            onset_relation_to_treatment=relations[0] if relations else None,
            resolution_status=resolutions[0] if resolutions else None,
            description=first.event_type.replace("_", " "),
            event_id=first_event.id,
        )
        canonical.append((merged, [row[0] for row in rows]))
    return canonical
