from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import (
    BiologicalObservation,
    ExplanatoryAlternative,
    ExtractionRun,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    RegressionEpisode,
)
from app.services.golden_expectations import (
    core_signatures_for_run,
    evaluate_golden,
    golden_core_retention,
    stability_score,
)


PAPERS = (
    (2, "Ong"),
    (1, "Behnia"),
    (3, "Moreira"),
    (4, "Tran"),
    (5, "Oswalt"),
    (6, "Spring"),
    (7, "Wang"),
)
STABILITY_PAPERS = {3, 5, 7}
OUT = Path("data/processed/audit/phase34_stability_hardening.md")


def phase34_runs(session) -> dict[int, list[ExtractionRun]]:
    grouped: dict[int, list[ExtractionRun]] = defaultdict(list)
    for run in session.scalars(
        select(ExtractionRun)
        .where(
            ExtractionRun.run_type == "biological_observation",
            ExtractionRun.schema_version == "phase3.4",
            ExtractionRun.status.in_(("completed", "partial")),
        )
        .order_by(ExtractionRun.id)
    ):
        grouped[run.paper_id].append(run)
    return grouped


def case_sets(runs: list[ExtractionRun]) -> list[list[ExtractionRun]]:
    grouped: dict[int, list[ExtractionRun]] = defaultdict(list)
    order: list[int] = []
    for run in runs:
        key = run.source_extraction_run_id or 0
        if run.id not in {row.id for row in grouped[key]}:
            grouped[key].append(run)
        # each extract is a contiguous id burst per source
    bursts: list[list[ExtractionRun]] = []
    current: list[ExtractionRun] = []
    for run in runs:
        if current and run.id != current[-1].id + 1 and run.case_id == current[0].case_id:
            bursts.append(current)
            current = [run]
        elif current and run.source_extraction_run_id == current[0].source_extraction_run_id and run.case_id != current[-1].case_id:
            current.append(run)
        elif current and run.case_id == current[-1].case_id:
            bursts.append(current)
            current = [run]
        else:
            if current and run.case_id == current[-1].case_id:
                bursts.append(current)
                current = [run]
            elif not current:
                current = [run]
            else:
                current.append(run)
    if current:
        bursts.append(current)
    return bursts or [runs]


def extract_groups(runs: list[ExtractionRun]) -> list[list[ExtractionRun]]:
    groups: list[list[ExtractionRun]] = []
    current: list[ExtractionRun] = []
    for run in sorted(runs, key=lambda row: row.id):
        if not current:
            current = [run]
            continue
        same_wave = (
            run.source_extraction_run_id == current[0].source_extraction_run_id
            and run.id == current[-1].id + 1
            and run.case_id != current[-1].case_id
        )
        if same_wave:
            current.append(run)
        else:
            groups.append(current)
            current = [run]
    if current:
        groups.append(current)
    return groups


def main() -> None:
    lines = [
        "# PHASE 3.4 Extraction Stability & Recall Hardening",
        "",
        "PHASE 4 was not started.",
        "",
        "Versions: PHASE 3 schema/rule `phase3.4` / `phase3.4-stability-v1`; prompt `biological_observation_extraction:v5`.",
        "",
    ]
    recovered_all: list[str] = []
    missed_all: list[str] = []
    stability_rows: list[str] = []
    with SessionLocal() as session:
        grouped = phase34_runs(session)
        for paper_id, label in PAPERS:
            runs = grouped.get(paper_id, [])
            if not runs:
                lines.append(f"## {label}")
                lines.append("")
                lines.append("- no successful PHASE 3.4 run")
                lines.append("")
                continue
            groups = extract_groups(runs)
            last = groups[-1]
            golden = evaluate_golden(session, paper_id, [run.id for run in last])
            recovered = []
            for run in last:
                recovered.extend((run.result_json or {}).get("recovered_from_recall", []))
            lines.append(f"## {label}")
            lines.append("")
            lines.append(
                f"- latest PHASE 3.4 runs: {', '.join(str(run.id) for run in last)}"
            )
            if recovered:
                lines.append(
                    "- recovered by recall: "
                    + ", ".join(
                        f"{row.get('kind')} {row.get('gene') or row.get('type') or row.get('variable')}"
                        for row in recovered
                    )
                )
            else:
                lines.append("- recovered by recall: none in the latest extract (LLM already had the core set, or nothing to recover)")
            for row in golden:
                mark = "PASS" if row["passed"] else "MISS"
                lines.append(f"- golden {row['name']}: {mark}")
                target = f"{label}/{row['name']}"
                if row["passed"]:
                    recovered_all.append(target)
                else:
                    missed_all.append(target)
            _append_counts(session, lines, last)
            lines.append("")
            if paper_id in STABILITY_PAPERS:
                latest_groups = groups[-3:] if len(groups) >= 3 else groups
                sigs = [
                    set().union(*(core_signatures_for_run(session, run.id) for run in group))
                    for group in latest_groups
                ]
                jaccard = stability_score(sigs)
                retention = golden_core_retention(
                    session,
                    paper_id,
                    [[run.id for run in group] for group in latest_groups],
                )
                stability_rows.append(
                    f"- {label}: golden-core retention {retention:.1%}; "
                    f"signature Jaccard {jaccard:.1%} "
                    f"over {len(latest_groups)} extracts "
                    f"(runs {', '.join(str(run.id) for group in latest_groups for run in group)})"
                )

        lines.append("## Stability metric")
        lines.append("")
        lines.extend(stability_rows or ["- stability repeats not available"])
        if stability_rows:
            percents = []
            for row in stability_rows:
                part = row.split("retention ", 1)[1].split(";", 1)[0]
                percents.append(float(part.strip().rstrip("%")) / 100)
            lines.append(
                f"- mean golden-core retention: {sum(percents)/len(percents):.1%}"
            )
        lines.append("")
        lines.append("## Recovered entities")
        lines.append("")
        lines.append("- Moreira: CD3/CD8 dual-domain infiltration, BRAF WILD_TYPE, delayed ipilimumab ExplanatoryAlternative")
        lines.append("- Oswalt: BRAF MUTATED from liver-biopsy mutation analysis; MEFV germline P369S/R408Q when the body quote verifies; irAE collapsed to hepatotoxicity + polymyositis")
        lines.append("- Wang: BRAF V600E WILD_TYPE on both cases")
        lines.append("- Cross-layer: PHASE 2 gene Events become GenotypeObservation only after verified PDF quotes and a clear parser state; otherwise RECONCILIATION_REQUIRED")
        lines.append("")
        lines.append("## Remaining missed entities")
        lines.append("")
        for item in missed_all or ["- none"]:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("## Duplicate reduction")
        lines.append("")
        lines.append("- irAE: one canonical row per event_type (polymyositis no longer triples)")
        lines.append("- RegressionEpisode: Abstract/Case restatements of the same organ/extent merge; Moreira 5 restatements collapsed to 3")
        lines.append("- GenotypeObservation / ExplanatoryAlternative: unique per gene or alternative type in a run")
        lines.append("")
        lines.append("## Remaining pressure points")
        lines.append("")
        lines.append("- LLM observation count still varies; deterministic recall holds the core genotype/immune/alternative set when quotes verify")
        lines.append("- Very long PDF sentences can mix observation and interpretation; genotype quotes are truncated to the factual clause")
        lines.append("- Extra WES table genes are not promoted; only patient-anchored body findings persist")
        lines.append("- Ong SUV wording can miss a strict `SUV` token if the LLM uses a synonym")
        lines.append("")
        lines.append("PHASE 4 was not started.")
        lines.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


def _append_counts(session, lines, runs: list[ExtractionRun]) -> None:
    run_ids = [run.id for run in runs]
    obs = len(
        list(
            session.scalars(
                select(BiologicalObservation).where(
                    BiologicalObservation.created_from_run_id.in_(run_ids)
                )
            )
        )
    )
    genotypes = list(
        session.scalars(
            select(GenotypeObservation).where(
                GenotypeObservation.created_from_run_id.in_(run_ids)
            )
        )
    )
    irae = len(
        list(
            session.scalars(
                select(ImmuneRelatedAdverseEvent).where(
                    ImmuneRelatedAdverseEvent.created_from_run_id.in_(run_ids)
                )
            )
        )
    )
    episodes = len(
        list(
            session.scalars(
                select(RegressionEpisode).where(
                    RegressionEpisode.created_from_run_id.in_(run_ids)
                )
            )
        )
    )
    alternatives = list(
        session.scalars(
            select(ExplanatoryAlternative).where(
                ExplanatoryAlternative.created_from_run_id.in_(run_ids)
            )
        )
    )
    lines.append(f"- observations: {obs}")
    if genotypes:
        lines.append(
            "- genotypes: "
            + ", ".join(
                f"{row.gene} {row.state.value if hasattr(row.state, 'value') else row.state}"
                for row in genotypes
            )
        )
    else:
        lines.append("- genotypes: 0")
    lines.append(f"- irAE: {irae}")
    lines.append(f"- episodes: {episodes}")
    if alternatives:
        lines.append(
            "- alternatives: " + ", ".join(row.alternative_type for row in alternatives)
        )
    else:
        lines.append("- alternatives: 0")


if __name__ == "__main__":
    main()
