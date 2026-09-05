import argparse
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import (
    BiologicalObservation,
    Evidence,
    ExplanatoryAlternative,
    ExtractionRun,
    FieldEvidenceLink,
    GenotypeObservation,
    Lesion,
    LesionAlias,
    LesionCollection,
    TemporalRecord,
)
from app.services.biological_observation_pipeline import (
    BiologicalObservationPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a PHASE 3 biological observation audit"
    )
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _evidence_for_observation(
    session, run_id: int, observation_id: int
) -> list[Evidence]:
    rows = session.scalars(
        select(Evidence)
        .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
        .where(
            FieldEvidenceLink.extraction_run_id == run_id,
            FieldEvidenceLink.entity_type == "biological_observation",
            FieldEvidenceLink.entity_id == observation_id,
            FieldEvidenceLink.field_name == "value",
        )
        .order_by(Evidence.page, Evidence.id)
    )
    unique: list[Evidence] = []
    seen: set[int] = set()
    for evidence in rows:
        if evidence.id not in seen:
            seen.add(evidence.id)
            unique.append(evidence)
    if unique:
        return unique
    return list(
        session.scalars(
            select(Evidence)
            .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
            .where(
                FieldEvidenceLink.extraction_run_id == run_id,
                FieldEvidenceLink.entity_type == "biological_observation",
                FieldEvidenceLink.entity_id == observation_id,
                FieldEvidenceLink.field_name == "status",
            )
            .order_by(Evidence.page, Evidence.id)
        ).unique()
    )


def generate(run_id: int, output: Path) -> None:
    with SessionLocal() as session:
        run = session.get(ExtractionRun, run_id)
        if run is None or run.run_type != BiologicalObservationPipeline.RUN_TYPE:
            raise SystemExit(f"Biological observation run {run_id} not found")
        observations = list(
            session.scalars(
                select(BiologicalObservation)
                .where(BiologicalObservation.created_from_run_id == run.id)
                .order_by(
                    BiologicalObservation.category,
                    BiologicalObservation.normalized_variable,
                    BiologicalObservation.id,
                )
            )
        )
        result = run.result_json or {}
        lines = [
            "# PHASE 3 Biological Observation Audit",
            "",
            f"- RUN ID: {run.id}",
            f"- CASE ID: {run.case_id}",
            f"- SOURCE PHASE 2 RUN: {run.source_extraction_run_id}",
            f"- STATUS: {run.status.value}",
            f"- SCHEMA: {run.schema_version}",
            f"- RULE: {run.rule_version}",
            f"- PROMPT: {run.prompt_version}",
            "",
            "## Biological Observations",
            "",
        ]
        if not observations:
            lines.extend(["No verified biological observations.", ""])
        for index, observation in enumerate(observations, start=1):
            lines.extend(
                [
                    f"### Observation {index}",
                    "",
                    f"CATEGORY: {observation.category.value}",
                    f"OBSERVATION DOMAIN: {observation.observation_domain}",
                    f"DOMAIN SECONDARY: {observation.domain_secondary or 'NONE'}",
                    f"MEASUREMENT SEMANTICS: {observation.measurement_semantics}",
                    f"VARIABLE: {observation.variable_name}",
                    f"NORMALIZED VARIABLE: {observation.normalized_variable or 'NONE'}",
                    f"VALUE: {observation.value or 'NONE'}",
                    "NORMALIZED VALUE: "
                    f"{observation.normalized_value if observation.normalized_value is not None else 'NONE'}",
                    f"UNIT: {observation.unit or 'NONE'}",
                    f"DIRECTION: {observation.direction}",
                    f"STATUS: {observation.status}",
                    f"TIME RELATION: {observation.time_relation}",
                    f"TEMPORAL PRECISION: {observation.temporal_precision}",
                    f"SCOPE TYPE: {observation.scope_type}",
                    f"LESION IDENTIFIER: {observation.lesion_identifier or 'NONE'}",
                    f"LESION ID: {observation.lesion_id or 'NONE'}",
                    f"LESION COLLECTION ID: {observation.lesion_collection_id or 'NONE'}",
                    f"TEMPORAL TEXT: {observation.temporal_text or 'NONE'}",
                    f"REGRESSION ROLE: {observation.regression_role}",
                    f"QUALITATIVE LEVEL: {observation.qualitative_level}",
                    f"CONTEXT: {observation.observation_context or 'NONE'}",
                    f"LINKED EVENT ID: {observation.linked_event_id or 'NONE'}",
                    f"CONFIDENCE: {observation.confidence:.2f}",
                    "",
                ]
            )
            evidence_rows = _evidence_for_observation(
                session, run.id, observation.id
            )
            for evidence_index, evidence in enumerate(evidence_rows, start=1):
                lines.extend(
                    [
                        f"EVIDENCE {evidence_index} TYPE: {evidence.evidence_type.value}",
                        f"PAGE: {evidence.page or 'NONE'}",
                        f"SECTION: {evidence.section or 'NONE'}",
                        f'QUOTE: "{evidence.source_quote}"',
                        "",
                    ]
                )

        lines.extend(["## Rejected As Interpretation", ""])
        rejected = result.get("rejected_as_interpretation", [])
        if not rejected:
            lines.extend(["None.", ""])
        for index, item in enumerate(rejected, start=1):
            lines.extend(
                [
                    f"### Rejected Interpretation {index}",
                    "",
                    f"STATEMENT: {item['statement']}",
                    f"REASON: {item['reason']}",
                    f"PAGE: {item.get('page') or 'NONE'}",
                    f"SECTION: {item.get('section') or 'NONE'}",
                    f'QUOTE: "{item["quote"]}"',
                    "",
                ]
            )

        lesions = list(
            session.scalars(
                select(Lesion).where(Lesion.created_from_run_id == run.id)
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
                select(LesionCollection).where(
                    LesionCollection.created_from_run_id == run.id
                )
            )
        )
        genotypes = list(
            session.scalars(
                select(GenotypeObservation).where(
                    GenotypeObservation.created_from_run_id == run.id
                )
            )
        )
        alternatives = list(
            session.scalars(
                select(ExplanatoryAlternative).where(
                    ExplanatoryAlternative.created_from_run_id == run.id
                )
            )
        )
        temporals = list(
            session.scalars(
                select(TemporalRecord).where(
                    TemporalRecord.created_from_run_id == run.id
                )
            )
        )
        lines.extend(["## Lesions", ""])
        if not lesions:
            lines.extend(["None.", ""])
        for lesion in lesions:
            lesion_aliases = [
                row for row in aliases if row.lesion_id == lesion.id
            ]
            lines.extend(
                [
                    f"- {lesion.canonical_name} ({lesion.identity_key})",
                    *[
                        f"  alias: {row.source_text} [{row.status.value}]"
                        for row in lesion_aliases
                    ],
                ]
            )
        lines.extend(["", "## Lesion Collections", ""])
        if not collections:
            lines.extend(["None.", ""])
        for collection in collections:
            lines.append(
                f"- {collection.canonical_name} [{collection.collection_type.value}]"
            )
        lines.extend(["", "## Genotype Observations", ""])
        if not genotypes:
            lines.extend(["None.", ""])
        for genotype in genotypes:
            lines.append(
                f"- {genotype.gene} {genotype.variant or ''} "
                f"{genotype.state.value}".replace("  ", " ")
            )
        lines.extend(["", "## Explanatory Alternatives", ""])
        if not alternatives:
            lines.extend(["None.", ""])
        for alternative in alternatives:
            lines.append(
                f"- {alternative.alternative_type} [{alternative.status.value}]: "
                f"{alternative.description}"
            )
        lines.extend(["", "## Temporal Records", ""])
        if not temporals:
            lines.extend(["None.", ""])
        for record in temporals:
            lines.append(
                f"- {record.entity_type}.{record.field_name}: "
                f"{record.temporal_text} [{record.temporal_precision.value}]"
            )

        metrics = result.get("metrics", {})
        lines.extend(
            [
                "",
                "## Summary",
                "",
                f"- OBSERVATIONS: {metrics.get('persisted_observations', 0)}",
                f"- VERIFIED EVIDENCE: {metrics.get('verified_evidence', 0)}",
                f"- REJECTED EVIDENCE: {metrics.get('rejected_evidence', 0)}",
                f"- DUPLICATE MERGES: {metrics.get('duplicate_merges', 0)}",
                f"- LESION ALIAS MERGES: {metrics.get('lesion_alias_merges', 0)}",
                f"- UNRESOLVED LESION IDENTITIES: "
                f"{metrics.get('unresolved_lesion_identities', 0)}",
                f"- DUAL-DOMAIN IMMUNE: {metrics.get('dual_domain_immune', 0)}",
                f"- GENOTYPE RECORDS: {metrics.get('genotype_records', 0)}",
                f"- UNCERTAIN: {metrics.get('uncertain_observations', 0)}",
                f"- NOT REPORTED TARGETS: {metrics.get('not_reported_variables', 0)}",
                "",
            ]
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    generate(args.run_id, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
