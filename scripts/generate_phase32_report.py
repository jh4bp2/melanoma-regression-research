from __future__ import annotations

from collections import Counter
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import (
    BiologicalObservation,
    Event,
    EventType,
    ExplanatoryAlternative,
    ExtractionRun,
    GenotypeObservation,
    Lesion,
    LesionAlias,
    LesionAliasStatus,
    ObservationCategory,
    ObservationDomain,
    TemporalRecord,
    TemporalSemanticPrecision,
)
from app.services.evidence_verifier import normalize_text

AUDIT_DIR = Path("data/processed/audit")
LABELS = {1: "Behnia", 2: "Ong", 3: "Paper 3", 4: "Paper 4"}


def _latest_phase32_runs(session) -> list[ExtractionRun]:
    runs = []
    for paper_id in (2, 1, 4, 3):
        run = session.scalar(
            select(ExtractionRun)
            .where(
                ExtractionRun.paper_id == paper_id,
                ExtractionRun.run_type == "biological_observation",
                ExtractionRun.schema_version == "phase3.2",
            )
            .order_by(ExtractionRun.id.desc())
        )
        if run is None:
            raise SystemExit(f"No PHASE 3.2 run for paper {paper_id}")
        runs.append(run)
    return runs


def main() -> None:
    with SessionLocal() as session:
        runs = _latest_phase32_runs(session)
        lines = [
            "# PHASE 3.2 Ontology Hardening Report",
            "",
            "PHASE 4 was not started. No new papers were added.",
            "",
            "## Versions",
            "",
            "- schema_version: phase3.2",
            "- rule_version: phase3.2-ontology-v1",
            "- biological observation prompt: biological_observation_extraction:v3",
            "- PHASE 2 schema/rule unchanged: phase2.2.2 / phase2.2-adjudication-v4",
            "",
            "## Runs",
            "",
        ]
        totals = Counter()
        paper_notes: list[str] = []
        for run in runs:
            observations = list(
                session.scalars(
                    select(BiologicalObservation).where(
                        BiologicalObservation.created_from_run_id == run.id
                    )
                )
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
                        TemporalRecord.created_from_run_id.in_(
                            [run.id, run.source_extraction_run_id or 0]
                        )
                    )
                )
            )
            phase2_temporals = [
                row
                for row in temporals
                if row.created_from_run_id == run.source_extraction_run_id
            ]
            bio_temporals = [
                row for row in temporals if row.created_from_run_id == run.id
            ]
            approx_relative = [
                row
                for row in temporals
                if row.temporal_precision
                in {
                    TemporalSemanticPrecision.APPROXIMATE_DATE,
                    TemporalSemanticPrecision.RELATIVE_TIME,
                    TemporalSemanticPrecision.INTERVAL,
                }
            ]
            confirmed_aliases = [
                row
                for row in aliases
                if row.status == LesionAliasStatus.CONFIRMED_ALIAS
                and normalize_text(row.source_text)
                != normalize_text(
                    next(
                        (
                            lesion.canonical_name
                            for lesion in lesions
                            if lesion.id == row.lesion_id
                        ),
                        "",
                    )
                )
            ]
            possible_aliases = [
                row
                for row in aliases
                if row.status == LesionAliasStatus.POSSIBLE_SAME_LESION
            ]
            dual_immune = [
                row
                for row in observations
                if row.observation_domain
                == ObservationDomain.BIOLOGICAL_STATE.value
                and row.domain_secondary
                == ObservationDomain.DIAGNOSTIC_EVIDENCE.value
                and row.category == ObservationCategory.IMMUNE
            ]
            spontaneous_as_treatment = [
                row
                for row in observations
                if row.observation_domain
                == ObservationDomain.TREATMENT_RESPONSE.value
                and (
                    "spontaneous" in normalize_text(row.variable_name)
                    or "resolved both clinically"
                    in normalize_text(row.value or "")
                    or "all in transit"
                    in normalize_text(f"{row.variable_name} {row.value or ''}")
                )
            ]
            infection_events = list(
                session.scalars(
                    select(Event).where(
                        Event.case_id == run.case_id,
                        Event.extraction_run_id == run.source_extraction_run_id,
                    )
                )
            )
            infection_event_present = any(
                event.event_type == EventType.INFECTION
                or "infection" in normalize_text(event.description)
                for event in infection_events
            )
            infection_context = [
                row
                for row in observations
                if row.observation_domain
                == ObservationDomain.CLINICAL_CONTEXT.value
                and "infection"
                in normalize_text(f"{row.variable_name} {row.value or ''}")
            ]
            static_decreased = [
                row
                for row in observations
                if row.direction == "DECREASED"
                and (
                    "ranged" in normalize_text(row.value or "")
                    or "measur" in normalize_text(row.value or "")
                )
            ]
            metrics = (run.result_json or {}).get("metrics", {})
            label = LABELS.get(run.paper_id, f"Paper {run.paper_id}")
            totals["alias_merges"] += metrics.get(
                "lesion_alias_merges", len(confirmed_aliases)
            )
            totals["unresolved"] += metrics.get(
                "unresolved_lesion_identities", len(possible_aliases)
            )
            totals["approx_relative"] += len(approx_relative)
            totals["dual_immune"] += len(dual_immune)
            totals["genotypes"] += len(genotypes)
            totals["observations"] += len(observations)
            lines.extend(
                [
                    f"### {label} (paper {run.paper_id})",
                    "",
                    f"- PHASE 2 run: {run.source_extraction_run_id}",
                    f"- PHASE 3.2 run: {run.id}",
                    f"- case_id: {run.case_id}",
                    f"- status: {run.status.value}",
                    f"- observations: {len(observations)}",
                    f"- lesions: {len(lesions)}",
                    f"- lesion aliases: {len(aliases)} "
                    f"(confirmed extra-name {len(confirmed_aliases)}, "
                    f"possible {len(possible_aliases)})",
                    f"- alias merges (run metric): "
                    f"{metrics.get('lesion_alias_merges', 0)}",
                    f"- unresolved lesion identities: "
                    f"{metrics.get('unresolved_lesion_identities', 0)}",
                    f"- temporal records: {len(temporals)} "
                    f"(case/event {len(phase2_temporals)}, "
                    f"observation {len(bio_temporals)}; "
                    f"approximate/relative/interval {len(approx_relative)})",
                    f"- dual-domain immune pathology: {len(dual_immune)}",
                    f"- genotype records: {len(genotypes)}",
                    f"- explanatory alternatives: {len(alternatives)}",
                    f"- static range marked DECREASED: {len(static_decreased)}",
                    f"- spontaneous regression as TREATMENT_RESPONSE: "
                    f"{len(spontaneous_as_treatment)}",
                    f"- infection Event present: {infection_event_present}",
                    f"- infection Clinical Context: {len(infection_context)}",
                    "",
                ]
            )
            if genotypes:
                lines.append("Genotypes:")
                for genotype in genotypes:
                    lines.append(
                        f"- {genotype.gene} {genotype.variant or ''} "
                        f"{genotype.state.value}".replace("  ", " ")
                    )
                lines.append("")
            if alternatives:
                lines.append("Explanatory alternatives:")
                for alternative in alternatives:
                    lines.append(
                        f"- {alternative.alternative_type} "
                        f"[{alternative.status.value}]"
                    )
                lines.append("")
            paper_notes.append(
                f"{label}: infection_context_recovered="
                f"{bool(infection_context) if infection_event_present else 'n/a'}; "
                f"spontaneous_misclass_remaining={len(spontaneous_as_treatment)}"
            )

        lines.extend(
            [
                "## Requested totals",
                "",
                f"- lesion alias merge count: {totals['alias_merges']}",
                f"- unresolved lesion identity count: {totals['unresolved']}",
                f"- approximate/relative/interval temporal records: "
                f"{totals['approx_relative']}",
                f"- dual-domain immune pathology count: {totals['dual_immune']}",
                f"- genotype records: {totals['genotypes']}",
                "",
                "## Checklist",
                "",
                * [f"- {note}" for note in paper_notes],
                "",
            ]
        )
        output = AUDIT_DIR / "phase32_ontology_hardening.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines), encoding="utf-8")
        print(output)
        print("\n".join(lines))


if __name__ == "__main__":
    main()
