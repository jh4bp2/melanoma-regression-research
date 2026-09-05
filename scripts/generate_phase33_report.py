from __future__ import annotations

from collections import Counter
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import (
    BiologicalObservation,
    Case,
    Event,
    Evidence,
    ExplanatoryAlternative,
    ExtractionRun,
    FieldEvidenceLink,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    Lesion,
    LesionCollection,
    ObservationCategory,
    ObservationDomain,
    QuoteVerificationStatus,
    RegressionEpisode,
)


AUDIT_DIR = Path("data/processed/audit")
LABELS = {
    2: "Ong",
    1: "Behnia",
    3: "Moreira",
    4: "Tran",
    5: "Oswalt",
    6: "Spring",
    7: "Wang",
}


def _latest_phase2(session, paper_id: int) -> ExtractionRun:
    run = session.scalar(
        select(ExtractionRun)
        .where(
            ExtractionRun.paper_id == paper_id,
            ExtractionRun.run_type == "case_timeline",
            ExtractionRun.schema_version == "phase2.3",
        )
        .order_by(ExtractionRun.id.desc())
    )
    if run is None:
        raise SystemExit(f"No PHASE 2.3 run for paper {paper_id}")
    return run


def main() -> None:
    totals = Counter()
    lines = [
        "# PHASE 3.3 External Validation–Driven Ontology Revision",
        "",
        "PHASE 4 was not started. Pattern Discovery, Hypothesis Generator, "
        "and Evidence Graph were not started.",
        "",
        "## Versions",
        "",
        "- PHASE 2 schema/rule: phase2.3 / phase2.3-case-scope-v1",
        "- PHASE 3 schema/rule: phase3.3 / phase3.3-ontology-v1",
        "- biological observation prompt: biological_observation_extraction:v4",
        "",
    ]
    with SessionLocal() as session:
        for paper_id in (2, 1, 3, 4, 5, 6, 7):
            phase2 = _latest_phase2(session, paper_id)
            cases = list(
                session.scalars(
                    select(Case).where(
                        Case.paper_id == paper_id,
                        Case.extraction_run_id == phase2.id,
                    )
                )
            )
            phase3_runs = []
            for case in cases:
                run = session.scalar(
                    select(ExtractionRun)
                    .where(
                        ExtractionRun.case_id == case.id,
                        ExtractionRun.run_type == "biological_observation",
                        ExtractionRun.schema_version == "phase3.3",
                        ExtractionRun.source_extraction_run_id == phase2.id,
                    )
                    .order_by(ExtractionRun.id.desc())
                )
                if run is None:
                    raise SystemExit(f"No PHASE 3.3 run for case {case.id}")
                phase3_runs.append(run)
            events = list(
                session.scalars(select(Event).where(Event.extraction_run_id == phase2.id))
            )
            observations = []
            lesions = []
            collections = []
            genotypes = []
            episodes = []
            iraes = []
            alternatives = []
            for run in phase3_runs:
                observations.extend(
                    session.scalars(
                        select(BiologicalObservation).where(
                            BiologicalObservation.created_from_run_id == run.id
                        )
                    )
                )
                lesions.extend(
                    session.scalars(select(Lesion).where(Lesion.created_from_run_id == run.id))
                )
                collections.extend(
                    session.scalars(
                        select(LesionCollection).where(
                            LesionCollection.created_from_run_id == run.id
                        )
                    )
                )
                genotypes.extend(
                    session.scalars(
                        select(GenotypeObservation).where(
                            GenotypeObservation.created_from_run_id == run.id
                        )
                    )
                )
                episodes.extend(
                    session.scalars(
                        select(RegressionEpisode).where(
                            RegressionEpisode.created_from_run_id == run.id
                        )
                    )
                )
                iraes.extend(
                    session.scalars(
                        select(ImmuneRelatedAdverseEvent).where(
                            ImmuneRelatedAdverseEvent.created_from_run_id == run.id
                        )
                    )
                )
                alternatives.extend(
                    session.scalars(
                        select(ExplanatoryAlternative).where(
                            ExplanatoryAlternative.created_from_run_id == run.id
                        )
                    )
                )
            evidence_ids = set(
                session.scalars(
                    select(FieldEvidenceLink.evidence_id).where(
                        FieldEvidenceLink.extraction_run_id == phase2.id
                    )
                )
            )
            for run in phase3_runs:
                evidence_ids.update(
                    session.scalars(
                        select(FieldEvidenceLink.evidence_id).where(
                            FieldEvidenceLink.extraction_run_id == run.id
                        )
                    )
                )
            evidence_rows = [
                session.get(Evidence, evidence_id) for evidence_id in evidence_ids
            ]
            quote_counts = Counter(
                (row.verification_status or QuoteVerificationStatus.UNVERIFIED.value)
                for row in evidence_rows
                if row is not None
            )
            unresolved = sum(
                len((run.result_json or {}).get("unresolved_lesion_identities", []))
                for run in phase3_runs
            )
            case_scope_uncertain = sum(
                len((run.result_json or {}).get("case_scope_uncertain", []))
                for run in phase3_runs
            )
            leukoderma = [
                row
                for row in observations
                if row.category == ObservationCategory.DERMATOLOGIC_PHENOTYPE
                or "leukoderma"
                in f"{row.variable_name} {row.value or ''}".casefold()
            ]
            germline = [row for row in genotypes if row.origin == "GERMLINE"]
            somatic = [row for row in genotypes if row.origin == "SOMATIC"]
            domains = Counter(row.observation_domain for row in observations)
            lines.extend(
                [
                    f"### {LABELS[paper_id]} (paper {paper_id})",
                    "",
                    f"- PHASE 2 run: {phase2.id} / {phase2.status.value}",
                    f"- PHASE 3.3 runs: "
                    + ", ".join(f"{run.id} case {run.case_id}" for run in phase3_runs),
                    f"- cases: {len(cases)}",
                    f"- events: {len(events)}",
                    f"- observations: {len(observations)} {dict(domains)}",
                    f"- lesions: {len(lesions)}",
                    f"- collections: {len(collections)}",
                    f"- unresolved lesion identities: {unresolved}",
                    f"- regression episodes: {len(episodes)}",
                    f"- genotypes: {len(genotypes)} "
                    f"(germline {len(germline)}, somatic {len(somatic)})",
                    f"- irAE records: {len(iraes)}",
                    f"- leukoderma/immune phenotype: {len(leukoderma)}",
                    f"- case-scope uncertain: {case_scope_uncertain}",
                    f"- quotes exact/normalized/unverified: "
                    f"{quote_counts.get('VERIFIED_EXACT', 0)}/"
                    f"{quote_counts.get('VERIFIED_NORMALIZED', 0)}/"
                    f"{quote_counts.get('UNVERIFIED', 0)}",
                    f"- explanatory alternatives: {len(alternatives)}",
                    "",
                ]
            )
            if genotypes:
                for genotype in genotypes:
                    lines.append(
                        f"- genotype {genotype.gene} {genotype.variant or ''} "
                        f"{genotype.state.value} origin={genotype.origin} "
                        f"protein={genotype.protein_change or 'NONE'}"
                    )
                lines.append("")
            if episodes:
                for episode in episodes:
                    lines.append(
                        f"- episode {episode.episode_index} {episode.episode_type.value} "
                        f"{episode.extent.value}: {episode.description[:160]}"
                    )
                lines.append("")
            totals["cases"] += len(cases)
            totals["events"] += len(events)
            totals["observations"] += len(observations)
            totals["lesions"] += len(lesions)
            totals["collections"] += len(collections)
            totals["unresolved"] += unresolved
            totals["episodes"] += len(episodes)
            totals["genotypes"] += len(genotypes)
            totals["germline"] += len(germline)
            totals["somatic"] += len(somatic)
            totals["irae"] += len(iraes)
            totals["leukoderma"] += len(leukoderma)
            totals["case_scope_uncertain"] += case_scope_uncertain
            totals["exact"] += quote_counts.get("VERIFIED_EXACT", 0)
            totals["normalized"] += quote_counts.get("VERIFIED_NORMALIZED", 0)
            totals["unverified"] += quote_counts.get("UNVERIFIED", 0)
            totals["alternatives"] += len(alternatives)
        lines.extend(
            [
                "## Totals",
                "",
                f"- cases: {totals['cases']}",
                f"- events: {totals['events']}",
                f"- observations: {totals['observations']}",
                f"- lesions: {totals['lesions']}",
                f"- collections: {totals['collections']}",
                f"- unresolved lesion identities: {totals['unresolved']}",
                f"- regression episodes: {totals['episodes']}",
                f"- genotype observations: {totals['genotypes']}",
                f"- germline/somatic: {totals['germline']}/{totals['somatic']}",
                f"- irAE records: {totals['irae']}",
                f"- leukoderma/immune phenotype: {totals['leukoderma']}",
                f"- case-scope uncertain: {totals['case_scope_uncertain']}",
                f"- quotes exact/normalized/unverified: "
                f"{totals['exact']}/{totals['normalized']}/{totals['unverified']}",
                f"- explanatory alternatives: {totals['alternatives']}",
                "",
            ]
        )
    output = AUDIT_DIR / "phase33_ontology_revision.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
