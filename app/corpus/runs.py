from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.corpus.versions import (
    CORPUS_INFRA_VERSION,
    FROZEN_PHASE2_SCHEMA,
    FROZEN_PHASE3_SCHEMA,
    RECONCILIATION_RUN_TYPE,
)
from app.models import Case, ExtractionRun, ExtractionStatus


def latest_phase2_run(session: Session, paper_id: int) -> ExtractionRun | None:
    return session.scalar(
        select(ExtractionRun)
        .where(
            ExtractionRun.paper_id == paper_id,
            ExtractionRun.run_type == "case_timeline",
            ExtractionRun.schema_version == FROZEN_PHASE2_SCHEMA,
            ExtractionRun.status.in_(
                (ExtractionStatus.COMPLETED, ExtractionStatus.PARTIAL)
            ),
        )
        .order_by(ExtractionRun.id.desc())
    )


def latest_phase3_runs(session: Session, paper_id: int) -> list[ExtractionRun]:
    runs = list(
        session.scalars(
            select(ExtractionRun)
            .where(
                ExtractionRun.paper_id == paper_id,
                ExtractionRun.run_type == "biological_observation",
                ExtractionRun.schema_version == FROZEN_PHASE3_SCHEMA,
                ExtractionRun.status.in_(
                    (ExtractionStatus.COMPLETED, ExtractionStatus.PARTIAL)
                ),
            )
            .order_by(ExtractionRun.id.desc())
        )
    )
    if not runs:
        return []
    latest_source = runs[0].source_extraction_run_id
    by_case: dict[int | None, ExtractionRun] = {}
    for run in reversed(runs):
        if run.source_extraction_run_id != latest_source:
            continue
        if run.case_id not in by_case:
            by_case[run.case_id] = run
    return list(by_case.values())


def latest_reconciliation_runs(session: Session, paper_id: int) -> list[ExtractionRun]:
    runs = list(
        session.scalars(
            select(ExtractionRun)
            .where(
                ExtractionRun.paper_id == paper_id,
                ExtractionRun.run_type == RECONCILIATION_RUN_TYPE,
                ExtractionRun.schema_version == CORPUS_INFRA_VERSION,
                ExtractionRun.status.in_(
                    (ExtractionStatus.COMPLETED, ExtractionStatus.PARTIAL)
                ),
            )
            .order_by(ExtractionRun.id.desc())
        )
    )
    by_case: dict[int | None, ExtractionRun] = {}
    for run in runs:
        if run.case_id not in by_case:
            by_case[run.case_id] = run
    return list(by_case.values())


def seed_cases_and_runs(
    session: Session, paper_id: int
) -> tuple[list[Case], ExtractionRun | None, list[ExtractionRun]]:
    phase2 = latest_phase2_run(session, paper_id)
    phase3 = latest_phase3_runs(session, paper_id)
    if phase2 is None:
        return [], None, []
    cases = list(
        session.scalars(
            select(Case)
            .where(
                Case.paper_id == paper_id,
                Case.extraction_run_id == phase2.id,
            )
            .order_by(Case.id)
        )
    )
    return cases, phase2, phase3
