from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    BiologicalObservation,
    Case,
    Evidence,
    Event,
    ExtractionRun,
    FieldEvidenceLink,
    Paper,
)


DOMAIN_ORDER = [
    ("BIOLOGICAL_STATE", "Biological States"),
    ("DISEASE_PHENOTYPE", "Disease Phenotypes"),
    ("DIAGNOSTIC_EVIDENCE", "Diagnostic Evidence"),
    ("CLINICAL_CONTEXT", "Clinical Context"),
    ("TREATMENT_RESPONSE", "Treatment Response"),
]

PAPER_TITLES = {
    4: (
        "Spontaneous regression of metastatic melanoma after inoculation with "
        "tetanus-diphtheria-pertussis vaccine"
    ),
    3: (
        "Regression of multifocal in transit melanoma metastases after palliative "
        "resection of dominant masses and 2 years after treatment with ipilimumab"
    ),
}

VALIDATION_FAILURES = {
    4: [
        "Four source quotes were rejected (three in PHASE 2 and one in PHASE 3.1), "
        "including a line-wrap/typography-sensitive primary-pathology sentence.",
        "A static 1-10 mm lesion-size range was assigned direction DECREASED even "
        "though it does not describe longitudinal change (observation 245).",
        "The reported relative regression-confirmation expression remained in "
        "field_statuses but could not be persisted in the date column.",
        "Patient-scoped phrases such as 'all aforementioned nodules' and 'all "
        "nodules had vanished' could not be mapped back to every lesion while new "
        "or persistent lesions coexisted.",
        "Equivalent entities were split across aliases (for example left axillary "
        "nodule versus left axillary lymph node, and chest-nodule variants), so the "
        "exact lesion-identifier count overstates distinct lesions.",
        "Biopsy findings 'fibrosis' and 'no disease' were represented with "
        "MORPHOLOGIC_FINDING semantics rather than PATHOLOGIC_FINDING.",
    ],
    3: [
        "The first PHASE 2 attempt (run 38) was blocked by a legacy SQLite temporal "
        "CHECK constraint. A compatibility-only persistence fix was required; "
        "schema, rule, and prompts were unchanged.",
        "Reported approximate diagnosis and regression-confirmation dates remained "
        "in field_statuses but could not be persisted in the exact date columns.",
        "Chronic lesion infection and postoperative recurring infections were "
        "captured as Events but no CLINICAL_CONTEXT observation was produced.",
        "Measured brisk CD3+/CD8+ T-cell infiltration was classified as "
        "DIAGNOSTIC_EVIDENCE rather than BIOLOGICAL_STATE (observation 289).",
        "BRAF V600 wild-type was represented as REPORTED_ABSENT/ABSENT instead of "
        "a reported genetic state (observation 278).",
        "Complete spontaneous resolution of in-transit metastases was classified "
        "as TREATMENT_RESPONSE despite the delayed, causally unresolved setting "
        "(observation 288).",
        "One direct radiographic reduction statement was rejected as an author "
        "interpretation ('most lesions reduced in size').",
        "Grouped and overlapping right-leg lesion identifiers prevent a reliable "
        "count of anatomically distinct lesions; exact identifiers are not stable "
        "lesion identities.",
    ],
}

PRESSURE_POINTS = {
    4: [
        "Approximate or relative case dates need representation outside exact date "
        "columns without losing the reported value.",
        "Cross-sentence references such as 'aforementioned nodules' need explicit "
        "lesion-set identity and membership.",
        "A stable lesion identity is needed across nodule, lymph-node, biopsy, and "
        "resection wording variants.",
        "A static numeric range must be distinguishable from a temporal direction.",
        "Pathology provenance and pathology measurement semantics can diverge for "
        "generic terms such as fibrosis and no disease.",
        "A combined local-and-systemic reaction does not fit one unambiguous scope.",
    ],
    3: [
        "Approximate month/year and 'by month/year' dates are preserved only in "
        "raw field status, not typed date columns.",
        "Observed infection functions as both a timed event and local/systemic "
        "clinical context, but the current observation layer omitted the latter.",
        "Immune-cell infiltration used diagnostically is simultaneously a measured "
        "biological state; one domain cannot express both roles.",
        "Wild-type genotype is a positive state, not reported absence.",
        "Delayed post-treatment regression cannot be labeled treatment response "
        "without encoding causal uncertainty.",
        "Multifocal in-transit disease requires lesion collections plus individual "
        "members, not free-text identifiers alone.",
        "Resected and non-resected lesion sets need persistent identities across "
        "pathology, surgery, imaging, and regression observations.",
        "Evidence-type fallback can preserve an incorrect LLM-declared "
        "AUTHOR_INTERPRETATION when direct-observation wording is not recognized.",
    ],
}


@dataclass(frozen=True)
class ValidationTarget:
    paper_id: int
    case_id: int
    phase2_run_id: int
    phase3_run_id: int


TARGETS = {
    4: ValidationTarget(4, 4, 36, 37),
    3: ValidationTarget(3, 5, 39, 40),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate immutable external-validation audit reports"
    )
    parser.add_argument("--paper-id", type=int, choices=sorted(TARGETS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _evidence_for_entity(
    session: Session,
    run_id: int,
    entity_type: str,
    entity_id: int,
) -> list[Evidence]:
    rows = session.scalars(
        select(Evidence)
        .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
        .where(
            FieldEvidenceLink.extraction_run_id == run_id,
            FieldEvidenceLink.entity_type == entity_type,
            FieldEvidenceLink.entity_id == entity_id,
        )
        .order_by(Evidence.page, Evidence.id)
    )
    unique: list[Evidence] = []
    seen: set[int] = set()
    for evidence in rows:
        if evidence.id not in seen:
            seen.add(evidence.id)
            unique.append(evidence)
    return unique


def _run_evidence_count(session: Session, run_id: int) -> int:
    return len(
        set(
            session.scalars(
                select(FieldEvidenceLink.evidence_id).where(
                    FieldEvidenceLink.extraction_run_id == run_id
                )
            )
        )
    )


def _format_evidence(evidence: Evidence) -> list[str]:
    return [
        f"  - Evidence {evidence.id}: page {evidence.page or 'NONE'}, "
        f"section {evidence.section or 'NONE'}, type "
        f"{evidence.evidence_type.value}",
        f'  - Quote: "{evidence.source_quote}"',
    ]


def _case_summary(case: Case) -> list[str]:
    fields = [
        ("Patient identifier", case.patient_identifier),
        ("Age / sex", f"{case.age or 'UNKNOWN'} / {case.sex or 'UNKNOWN'}"),
        ("Melanoma subtype", case.melanoma_subtype),
        ("Primary site", case.primary_site),
        ("Stage", case.stage),
        ("Metastatic sites", "; ".join(case.metastatic_sites or [])),
        ("First observed reduction", case.first_observed_reduction),
        ("Regression confirmation", case.regression_confirmed_date),
        ("Regression extent", case.regression_extent_clinical),
        ("Treatment before regression", case.treatment_before_regression),
        ("Preceding events", case.preceding_event),
        ("Outcome", case.outcome),
    ]
    lines = ["# Case Summary", ""]
    for label, value in fields:
        lines.append(f"- {label}: {value if value not in (None, '') else 'NOT STORED'}")
    lines.extend(["", "## Case Field Statuses", ""])
    for name, value in (case.field_statuses or {}).items():
        lines.append(
            f"- {name}: {value.get('status')} | raw value: "
            f"{value.get('raw_value')}"
        )
    return lines


def _timeline(
    session: Session, events: list[Event], phase2_run_id: int
) -> list[str]:
    lines = ["", "# Timeline", ""]
    for event in events:
        lines.extend(
            [
                f"## Event {event.id}: {event.event_type.value}",
                f"- Description: {event.description}",
                f"- Event date: {event.event_date or 'NONE'}",
                f"- Relative time: {event.relative_time or 'NONE'}",
                f"- Stored/source precision: {event.date_precision.value} / "
                f"{event.source_date_precision or 'NONE'}",
                f"- Relation to regression: {event.relation_to_regression or 'UNKNOWN'}",
            ]
        )
        for evidence in _evidence_for_entity(
            session, phase2_run_id, "event", event.id
        ):
            lines.extend(_format_evidence(evidence))
        lines.append("")
    return lines


def _lesion_map(observations: list[BiologicalObservation]) -> list[str]:
    lesions: dict[str, list[BiologicalObservation]] = {}
    for observation in observations:
        if observation.scope_type not in {"LESION", "LYMPH_NODE"}:
            continue
        if observation.lesion_identifier:
            lesions.setdefault(observation.lesion_identifier, []).append(observation)
    lines = ["# Lesion Map", ""]
    for identifier, rows in sorted(lesions.items()):
        lines.append(f"## {identifier}")
        lines.append(f"- Scope: {rows[0].scope_type}")
        lines.append(
            "- Roles: "
            + ", ".join(sorted({row.regression_role or "UNKNOWN" for row in rows}))
        )
        for row in rows:
            lines.append(
                f"- Observation {row.id}: {row.variable_name} | "
                f"{row.status}/{row.direction} | {row.value or 'NONE'}"
            )
        lines.append("")
    if not lesions:
        lines.extend(["No lesion-scoped observations.", ""])
    return lines


def _domain_section(
    session: Session,
    observations: list[BiologicalObservation],
    phase3_run_id: int,
    domain: str,
    heading: str,
) -> list[str]:
    lines = [f"# {heading}", ""]
    rows = [row for row in observations if row.observation_domain == domain]
    if not rows:
        return lines + ["None.", ""]
    for observation in rows:
        lines.extend(
            [
                f"## Observation {observation.id}: {observation.variable_name}",
                f"- Category: {observation.category.value}",
                f"- Value: {observation.value or 'NONE'}",
                f"- Status / direction: {observation.status} / "
                f"{observation.direction}",
                f"- Semantics: {observation.measurement_semantics}",
                f"- Time relation: {observation.time_relation}",
                f"- Scope / lesion: {observation.scope_type} / "
                f"{observation.lesion_identifier or 'NONE'}",
                f"- Regression role: {observation.regression_role}",
            ]
        )
        for evidence in _evidence_for_entity(
            session, phase3_run_id, "biological_observation", observation.id
        ):
            lines.extend(_format_evidence(evidence))
        lines.append("")
    return lines


def _matching_events(
    events: list[Event], *, event_types: set[str] | None = None, terms: tuple[str, ...] = ()
) -> list[Event]:
    matches = []
    for event in events:
        text = event.description.casefold()
        if event_types and event.event_type.value in event_types:
            matches.append(event)
        elif terms and any(term.casefold() in text for term in terms):
            matches.append(event)
    return list(dict.fromkeys(matches))


def _confounder_matches(paper_id: int, events: list[Event]) -> dict[str, list[Event]]:
    if paper_id == 4:
        return {
            "prior immunotherapy": _matching_events(events, terms=("interferon",)),
            "recent surgery": _matching_events(events, event_types={"surgery"}),
            "biopsy": _matching_events(events, event_types={"biopsy"}),
            "infection": [],
            "vaccination": _matching_events(events, event_types={"vaccination"}),
            "radiotherapy": _matching_events(events, terms=("radiotherapy",)),
            "systemic therapy": _matching_events(events, terms=("interferon",)),
            "alternative treatment": [],
            "other major clinical intervention": [],
        }
    return {
        "prior immunotherapy": _matching_events(events, terms=("ipilimumab",)),
        "recent surgery": _matching_events(events, event_types={"surgery"}),
        "biopsy": _matching_events(events, event_types={"biopsy"}),
        "infection": _matching_events(events, event_types={"infection"}),
        "vaccination": [],
        "radiotherapy": [],
        "systemic therapy": _matching_events(
            events,
            terms=("ipilimumab", "dexamethasone", "immunoglobulin", "lenalidomide"),
        ),
        "alternative treatment": [],
        "other major clinical intervention": _matching_events(
            events, terms=("transfusion",)
        ),
    }


def _confounder_register(
    session: Session,
    paper_id: int,
    events: list[Event],
    phase2_run_id: int,
) -> list[str]:
    lines = [
        "# Confounder Register",
        "",
        "Presence records temporal co-occurrence only and is not a causal assignment.",
        "",
    ]
    for name, matches in _confounder_matches(paper_id, events).items():
        status = "PRESENT" if matches else "NOT_REPORTED"
        lines.extend([f"## {name}", f"- Status: {status}"])
        if not matches:
            lines.extend(["- Temporal relation: UNKNOWN", "- Evidence: NONE", ""])
            continue
        for event in matches:
            lines.append(
                f"- Temporal relation: {event.relation_to_regression or 'UNKNOWN'}; "
                f"{event.relative_time or event.event_date or 'time not stored'}"
            )
            evidence_rows = _evidence_for_entity(
                session, phase2_run_id, "event", event.id
            )
            for evidence in evidence_rows:
                lines.extend(_format_evidence(evidence))
        lines.append("")
    return lines


def _interpretations(phase3_run: ExtractionRun) -> list[str]:
    lines = ["# Author Interpretations", ""]
    rows = (phase3_run.result_json or {}).get("rejected_as_interpretation", [])
    if not rows:
        return lines + ["None.", ""]
    for index, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## Interpretation {index}",
                f"- Statement: {row.get('statement')}",
                f"- Rejection reason: {row.get('reason')}",
                f"- Page / section: {row.get('page') or 'NONE'} / "
                f"{row.get('section') or 'NONE'}",
                f'- Quote: "{row.get("quote")}"',
                "",
            ]
        )
    return lines


def _rejected_claims(
    phase2_run: ExtractionRun, phase3_run: ExtractionRun
) -> list[str]:
    lines = ["# Rejected Claims", ""]
    rows = [
        ("PHASE 2", row)
        for row in (phase2_run.result_json or {}).get("verification_failures", [])
    ] + [
        ("PHASE 3.1", row)
        for row in (phase3_run.result_json or {}).get("verification_failures", [])
    ]
    if not rows:
        return lines + ["No quote-verification failures.", ""]
    for index, (phase, row) in enumerate(rows, start=1):
        lines.extend(
            [
                f"## Rejected claim {index}",
                f"- Phase: {phase}",
                f"- Field: {row.get('field')}",
                f"- Reason: {row.get('reason')}",
                f"- Page: {row.get('page') or 'NONE'}",
                f'- Quote: "{row.get("quote")}"',
                "",
            ]
        )
    return lines


def _validation_sections(paper_id: int) -> list[str]:
    lines = ["# Validation Failures", ""]
    for failure in VALIDATION_FAILURES[paper_id]:
        lines.append(f"- {failure}")
    lines.extend(["", "# New Ontology Pressure Points", ""])
    for point in PRESSURE_POINTS[paper_id]:
        lines.append(f"- {point}")
    lines.append("")
    return lines


def _summary(
    session: Session,
    target: ValidationTarget,
    case: Case,
    events: list[Event],
    observations: list[BiologicalObservation],
    phase2_run: ExtractionRun,
    phase3_run: ExtractionRun,
) -> list[str]:
    lesions = {
        row.lesion_identifier
        for row in observations
        if row.scope_type in {"LESION", "LYMPH_NODE"} and row.lesion_identifier
    }
    domains = Counter(row.observation_domain for row in observations)
    field_states = Counter(
        value.get("status") for value in (case.field_statuses or {}).values()
    )
    observation_states = Counter(row.status for row in observations)
    phase2_failures = len(
        (phase2_run.result_json or {}).get("verification_failures", [])
    )
    phase3_failures = len(
        (phase3_run.result_json or {}).get("verification_failures", [])
    )
    phase3_metrics = (phase3_run.result_json or {}).get("metrics", {})
    lines = [
        "# Validation Summary",
        "",
        f"- PHASE 2 status/run: {phase2_run.status.value} / {phase2_run.id}",
        f"- PHASE 3.1 status/run: {phase3_run.status.value} / {phase3_run.id}",
        "- Stable versions: phase2.2.2 / phase2.2-adjudication-v4 / case v5 / "
        "timeline v3; phase3.1 / phase3.1-ontology-v4 / biological v2",
        "- Case count: 1",
        f"- Event count: {len(events)}",
        f"- Exact lesion identifier count: {len(lesions)}",
        f"- Biological State count: {domains['BIOLOGICAL_STATE']}",
        f"- Disease Phenotype count: {domains['DISEASE_PHENOTYPE']}",
        f"- Clinical Context count: {domains['CLINICAL_CONTEXT']}",
        f"- Diagnostic Evidence count: {domains['DIAGNOSTIC_EVIDENCE']}",
        f"- Treatment Response count: {domains['TREATMENT_RESPONSE']}",
        f"- Verified Evidence count: "
        f"{_run_evidence_count(session, target.phase2_run_id) + int(phase3_metrics.get('verified_evidence', 0))}",
        f"- Rejected Evidence count: {phase3_metrics.get('rejected_evidence', 0)}",
        f"- Quote failure count: {phase2_failures + phase3_failures}",
        f"- Case UNCERTAIN/CONFLICTING count: "
        f"{field_states['UNCERTAIN'] + field_states['CONFLICTING']}",
        f"- Observation UNCERTAIN/CONFLICTING count: "
        f"{observation_states['UNCERTAIN'] + observation_states['CONFLICTING']}",
        f"- UNKNOWN direction count: "
        f"{sum(row.direction == 'UNKNOWN' for row in observations)}",
        f"- UNKNOWN regression-role count: "
        f"{sum(row.regression_role == 'UNKNOWN' for row in observations)}",
        f"- Ontology pressure point count: {len(PRESSURE_POINTS[target.paper_id])}",
        "",
    ]
    return lines


def generate(paper_id: int, output: Path) -> None:
    target = TARGETS[paper_id]
    with SessionLocal() as session:
        paper = session.get(Paper, target.paper_id)
        case = session.get(Case, target.case_id)
        phase2_run = session.get(ExtractionRun, target.phase2_run_id)
        phase3_run = session.get(ExtractionRun, target.phase3_run_id)
        if not all((paper, case, phase2_run, phase3_run)):
            raise SystemExit("External-validation extraction records are incomplete")
        events = list(
            session.scalars(
                select(Event)
                .where(
                    Event.case_id == case.id,
                    Event.extraction_run_id == phase2_run.id,
                )
                .order_by(Event.id)
            )
        )
        observations = list(
            session.scalars(
                select(BiologicalObservation)
                .where(BiologicalObservation.created_from_run_id == phase3_run.id)
                .order_by(BiologicalObservation.id)
            )
        )

        lines = [
            "# External Validation Audit",
            "",
            f"- Paper ID: {paper_id}",
            f"- Title: {PAPER_TITLES[paper_id]}",
            "- Validation-set rule: record mismatches without adapting ontology, "
            "schema, rule, or prompts.",
            "",
        ]
        lines.extend(_case_summary(case))
        lines.extend(_timeline(session, events, phase2_run.id))
        lines.extend(_lesion_map(observations))
        for domain, heading in DOMAIN_ORDER:
            lines.extend(
                _domain_section(
                    session, observations, phase3_run.id, domain, heading
                )
            )
        lines.extend(
            _confounder_register(session, paper_id, events, phase2_run.id)
        )
        lines.extend(_interpretations(phase3_run))
        lines.extend(_rejected_claims(phase2_run, phase3_run))
        lines.extend(_validation_sections(paper_id))
        lines.extend(
            _summary(
                session,
                target,
                case,
                events,
                observations,
                phase2_run,
                phase3_run,
            )
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    generate(args.paper_id, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
