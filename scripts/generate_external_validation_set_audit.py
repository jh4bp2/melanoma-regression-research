from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    BiologicalObservation,
    Case,
    Evidence,
    Event,
    ExplanatoryAlternative,
    ExtractionRun,
    FieldEvidenceLink,
    GenotypeObservation,
    Lesion,
    LesionAlias,
    LesionCollection,
    LesionCollectionMembership,
    Paper,
)


DOMAIN_ORDER = [
    ("BIOLOGICAL_STATE", "Biological States"),
    ("DISEASE_PHENOTYPE", "Disease Phenotypes"),
    ("DIAGNOSTIC_EVIDENCE", "Diagnostic Evidence"),
    ("CLINICAL_CONTEXT", "Clinical Context"),
    ("TREATMENT_RESPONSE", "Treatment Response"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate PHASE 3.2 external-validation audits"
    )
    parser.add_argument("--paper-id", type=int, required=True)
    parser.add_argument("--phase2-run-id", type=int, required=True)
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


def _format_evidence(evidence: Evidence) -> list[str]:
    return [
        f"  - Evidence {evidence.id}: page {evidence.page or 'NONE'}, "
        f"section {evidence.section or 'NONE'}, type "
        f"{evidence.evidence_type.value}",
        f'  - Quote: "{evidence.source_quote}"',
    ]


def _case_summary(case: Case) -> list[str]:
    fields = [
        ("Case ID", case.id),
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
    lines = [f"# Case Summary — Case {case.id}", ""]
    for label, value in fields:
        lines.append(f"- {label}: {value if value not in (None, '') else 'NOT STORED'}")
    lines.extend(["", "## Case Field Statuses", ""])
    for name, value in (case.field_statuses or {}).items():
        lines.append(
            f"- {name}: {value.get('status')} | raw value: "
            f"{value.get('raw_value')}"
        )
    return lines


def _timeline(session: Session, events: list[Event], phase2_run_id: int) -> list[str]:
    lines = ["", "# Timeline", ""]
    if not events:
        return lines + ["No events.", ""]
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


def _lesion_map(
    session: Session,
    observations: list[BiologicalObservation],
    phase3_run_id: int,
) -> list[str]:
    lesions = list(
        session.scalars(
            select(Lesion)
            .where(Lesion.created_from_run_id == phase3_run_id)
            .order_by(Lesion.id)
        )
    )
    aliases = list(
        session.scalars(
            select(LesionAlias).where(
                LesionAlias.lesion_id.in_([row.id for row in lesions] or [0])
            )
        )
    )
    collections = list(
        session.scalars(
            select(LesionCollection)
            .where(LesionCollection.created_from_run_id == phase3_run_id)
            .order_by(LesionCollection.id)
        )
    )
    memberships = list(
        session.scalars(
            select(LesionCollectionMembership).where(
                LesionCollectionMembership.collection_id.in_(
                    [row.id for row in collections] or [0]
                )
            )
        )
    )
    lines = ["# Lesion Map", ""]
    if not lesions and not collections:
        lines.extend(["No persisted lesion identities or collections.", ""])
    for lesion in lesions:
        lesion_aliases = [row for row in aliases if row.lesion_id == lesion.id]
        obs_rows = [row for row in observations if row.lesion_id == lesion.id]
        lines.extend(
            [
                f"## Lesion {lesion.id}: {lesion.canonical_name}",
                f"- Identity key: {lesion.identity_key}",
                f"- Type: {lesion.lesion_type or 'NONE'}",
                f"- Laterality: {lesion.laterality or 'NONE'}",
                f"- Organ / location: {lesion.organ or 'NONE'} / "
                f"{lesion.anatomical_location or 'NONE'}",
                "- Aliases: "
                + (
                    "; ".join(
                        f"{row.source_text} [{row.status.value}]"
                        for row in lesion_aliases
                    )
                    or "NONE"
                ),
            ]
        )
        for row in obs_rows:
            lines.append(
                f"- Observation {row.id}: {row.variable_name} | "
                f"{row.observation_domain} | {row.status}/{row.direction} | "
                f"{row.value or 'NONE'}"
            )
        lines.append("")
    if collections:
        lines.append("## Collections")
        lines.append("")
        for collection in collections:
            members = [
                row for row in memberships if row.collection_id == collection.id
            ]
            obs_rows = [
                row
                for row in observations
                if row.lesion_collection_id == collection.id
            ]
            lines.extend(
                [
                    f"### Collection {collection.id}: {collection.canonical_name}",
                    f"- Type: {collection.collection_type.value}",
                    "- Members: "
                    + (
                        ", ".join(str(row.lesion_id) for row in members) or "NONE"
                    ),
                ]
            )
            for row in obs_rows:
                lines.append(
                    f"- Observation {row.id}: {row.variable_name} | "
                    f"{row.observation_domain} | {row.value or 'NONE'}"
                )
            lines.append("")
    leftover = [
        row
        for row in observations
        if row.scope_type in {"LESION", "LYMPH_NODE", "COLLECTION"}
        and row.lesion_id is None
        and row.lesion_collection_id is None
        and row.lesion_identifier
    ]
    if leftover:
        lines.append("## Unbound lesion identifiers")
        lines.append("")
        for row in leftover:
            lines.append(
                f"- Observation {row.id}: {row.lesion_identifier} / "
                f"{row.scope_type} / {row.variable_name}"
            )
        lines.append("")
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
                f"- Lesion ID / collection ID: {observation.lesion_id or 'NONE'} / "
                f"{observation.lesion_collection_id or 'NONE'}",
                f"- Regression role: {observation.regression_role}",
                f"- Domain secondary: {observation.domain_secondary or 'NONE'}",
            ]
        )
        for evidence in _evidence_for_entity(
            session, phase3_run_id, "biological_observation", observation.id
        ):
            lines.extend(_format_evidence(evidence))
        lines.append("")
    return lines


def _genotype_section(
    session: Session, phase3_run_id: int
) -> list[str]:
    genotypes = list(
        session.scalars(
            select(GenotypeObservation)
            .where(GenotypeObservation.created_from_run_id == phase3_run_id)
            .order_by(GenotypeObservation.id)
        )
    )
    lines = ["# Genotype Observations", ""]
    if not genotypes:
        return lines + ["None.", ""]
    for genotype in genotypes:
        lines.extend(
            [
                f"## Genotype {genotype.id}: {genotype.gene}",
                f"- Variant: {genotype.variant or 'NONE'}",
                f"- State: {genotype.state.value}",
                f"- Linked observation: {genotype.biological_observation_id or 'NONE'}",
            ]
        )
        for evidence in _evidence_for_entity(
            session, phase3_run_id, "genotype_observation", genotype.id
        ):
            lines.extend(_format_evidence(evidence))
        lines.append("")
    return lines


def _alternatives_section(session: Session, phase3_run_id: int) -> list[str]:
    alternatives = list(
        session.scalars(
            select(ExplanatoryAlternative)
            .where(ExplanatoryAlternative.created_from_run_id == phase3_run_id)
            .order_by(ExplanatoryAlternative.id)
        )
    )
    lines = ["# Explanatory Alternatives", ""]
    if not alternatives:
        return lines + ["None.", ""]
    for alternative in alternatives:
        lines.extend(
            [
                f"## Alternative {alternative.id}",
                f"- Type: {alternative.alternative_type}",
                f"- Status: {alternative.status.value}",
                f"- Description: {alternative.description}",
            ]
        )
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
    phase2_run: ExtractionRun, phase3_runs: list[ExtractionRun]
) -> list[str]:
    lines = ["# Rejected Claims", ""]
    rows = [
        ("PHASE 2", row)
        for row in (phase2_run.result_json or {}).get("verification_failures", [])
    ]
    for phase3_run in phase3_runs:
        rows.extend(
            ("PHASE 3.2", row)
            for row in (phase3_run.result_json or {}).get(
                "verification_failures", []
            )
        )
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


def generate(paper_id: int, phase2_run_id: int, output: Path) -> None:
    with SessionLocal() as session:
        paper = session.get(Paper, paper_id)
        phase2_run = session.get(ExtractionRun, phase2_run_id)
        if paper is None or phase2_run is None:
            raise SystemExit("Paper or PHASE 2 run not found")
        if (
            phase2_run.paper_id != paper_id
            or phase2_run.run_type != "case_timeline"
        ):
            raise SystemExit("PHASE 2 run does not match paper")
        cases = list(
            session.scalars(
                select(Case)
                .where(
                    Case.paper_id == paper_id,
                    Case.extraction_run_id == phase2_run.id,
                )
                .order_by(Case.id)
            )
        )
        phase3_runs = []
        for case in cases:
            run = session.scalar(
                select(ExtractionRun)
                .where(
                    ExtractionRun.case_id == case.id,
                    ExtractionRun.run_type == "biological_observation",
                    ExtractionRun.schema_version == "phase3.2",
                    ExtractionRun.source_extraction_run_id == phase2_run.id,
                )
                .order_by(ExtractionRun.id.desc())
            )
            if run is None:
                raise SystemExit(f"No PHASE 3.2 run for case {case.id}")
            phase3_runs.append(run)

        lines = [
            "# External Validation Audit",
            "",
            f"- Paper ID: {paper.id}",
            f"- Title: {paper.title}",
            f"- DOI / PMID: {paper.doi or 'NONE'} / {paper.pmid or 'NONE'}",
            f"- PHASE 2 run: {phase2_run.id} ({phase2_run.schema_version} / "
            f"{phase2_run.rule_version})",
            "- PHASE 3 runs: "
            + ", ".join(
                f"{run.id} case {run.case_id}" for run in phase3_runs
            ),
            "- Stable versions: schema phase2.2.2 / rule phase2.2-adjudication-v4; "
            "schema phase3.2 / rule phase3.2-ontology-v1 / "
            "prompt biological_observation_extraction:v3",
            "- Validation-set rule: record mismatches without adapting ontology, "
            "schema, rule, or prompts. Selection rationale is research metadata "
            "only and was not preloaded into Case / Evidence / "
            "BiologicalObservation.",
            "- PHASE 4 / Pattern Discovery / Public Hypothesis / Evidence Graph "
            "were not started.",
            "",
        ]

        all_events: list[Event] = []
        all_observations: list[BiologicalObservation] = []
        for case, phase3_run in zip(cases, phase3_runs, strict=True):
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
            all_events.extend(events)
            all_observations.extend(observations)
            lines.extend(_case_summary(case))
            lines.extend(_timeline(session, events, phase2_run.id))
            lines.extend(_lesion_map(session, observations, phase3_run.id))
            for domain, heading in DOMAIN_ORDER:
                lines.extend(
                    _domain_section(
                        session, observations, phase3_run.id, domain, heading
                    )
                )
            lines.extend(_genotype_section(session, phase3_run.id))
            lines.extend(_alternatives_section(session, phase3_run.id))
            lines.extend(_interpretations(phase3_run))

        lines.extend(_rejected_claims(phase2_run, phase3_runs))
        lines.extend(
            [
                "# Validation Failures",
                "",
                "Filled after extraction review. Schema/rule/prompt were not changed.",
                "",
                "# New Ontology Pressure Points",
                "",
                "Filled after extraction review. No ontology patch was implemented.",
                "",
            ]
        )

        domains = Counter(row.observation_domain for row in all_observations)
        genotype_count = 0
        for phase3_run in phase3_runs:
            genotype_count += len(
                list(
                    session.scalars(
                        select(GenotypeObservation).where(
                            GenotypeObservation.created_from_run_id == phase3_run.id
                        )
                    )
                )
            )
        phase2_failures = len(
            (phase2_run.result_json or {}).get("verification_failures", [])
        )
        phase3_failures = sum(
            len((run.result_json or {}).get("verification_failures", []))
            for run in phase3_runs
        )
        verified = 0
        rejected = 0
        for run in phase3_runs:
            metrics = (run.result_json or {}).get("metrics", {})
            verified += int(metrics.get("verified_evidence", 0))
            rejected += int(metrics.get("rejected_evidence", 0))
        verified += len(
            set(
                session.scalars(
                    select(FieldEvidenceLink.evidence_id).where(
                        FieldEvidenceLink.extraction_run_id == phase2_run.id
                    )
                )
            )
        )
        lines.extend(
            [
                "# Validation Summary",
                "",
                f"- Case count: {len(cases)}",
                f"- Event count: {len(all_events)}",
                f"- Observation count: {len(all_observations)}",
                f"- Biological State: {domains['BIOLOGICAL_STATE']}",
                f"- Disease Phenotype: {domains['DISEASE_PHENOTYPE']}",
                f"- Diagnostic Evidence: {domains['DIAGNOSTIC_EVIDENCE']}",
                f"- Clinical Context: {domains['CLINICAL_CONTEXT']}",
                f"- Treatment Response: {domains['TREATMENT_RESPONSE']}",
                f"- Genotype observations: {genotype_count}",
                f"- Verified Evidence: {verified}",
                f"- Rejected Evidence: {rejected}",
                f"- Quote failures: {phase2_failures + phase3_failures}",
                "",
            ]
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    generate(args.paper_id, args.phase2_run_id, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
