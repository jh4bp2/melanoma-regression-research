from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.llm.provider import create_provider
from app.models import Case, ExtractionRun
from app.services.biological_observation_pipeline import (
    BiologicalObservationPipeline,
)
from app.services.extraction_pipeline import ExtractionPipeline
from scripts.generate_biological_observation_audit import generate


PAPERS = (
    (2, "ong"),
    (1, "behnia"),
    (4, "paper4"),
    (3, "paper3"),
)
AUDIT_DIR = Path("data/processed/audit")


def _latest_case_for_paper(session, paper_id: int, run_id: int) -> Case:
    case = session.scalar(
        select(Case)
        .where(Case.paper_id == paper_id, Case.extraction_run_id == run_id)
        .order_by(Case.id.desc())
    )
    if case is None:
        raise SystemExit(f"No case created for paper {paper_id} run {run_id}")
    return case


def main() -> None:
    init_db()
    settings = get_settings()
    provider = create_provider(settings)
    case_pipeline = ExtractionPipeline(provider)
    bio_pipeline = BiologicalObservationPipeline(provider)
    created: list[tuple[int, str, int, int, int]] = []

    with SessionLocal() as session:
        for paper_id, label in PAPERS:
            print(f"=== PHASE 2 extract paper={paper_id} ({label}) ===")
            case_run = case_pipeline.run(session, paper_id)
            print(
                f"paper={paper_id} case_run={case_run.id} "
                f"status={case_run.status.value}"
            )
            case = _latest_case_for_paper(session, paper_id, case_run.id)
            print(f"=== PHASE 3.2 extract case={case.id} paper={paper_id} ===")
            bio_run = bio_pipeline.run_case(
                session, case.id, source_run_id=case_run.id
            )
            metrics = (bio_run.result_json or {}).get("metrics", {})
            print(
                f"case={case.id} bio_run={bio_run.id} "
                f"status={bio_run.status.value} "
                f"observations={metrics.get('persisted_observations', 0)}"
            )
            output = AUDIT_DIR / f"phase32_{label}_biological_observations.md"
            generate(bio_run.id, output)
            print(f"audit={output}")
            created.append((paper_id, label, case.id, case_run.id, bio_run.id))

    print("=== PHASE 3.2 RUNS ===")
    for paper_id, label, case_id, case_run_id, bio_run_id in created:
        print(
            f"paper={paper_id} label={label} case={case_id} "
            f"phase2={case_run_id} phase32={bio_run_id}"
        )


if __name__ == "__main__":
    main()
