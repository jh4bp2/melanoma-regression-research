from __future__ import annotations

import argparse

from sqlalchemy import select

from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.llm.provider import create_provider
from app.models import Case
from app.services.biological_observation_pipeline import (
    BiologicalObservationPipeline,
)
from app.services.extraction_pipeline import ExtractionPipeline


PAPERS = (
    (2, "ong"),
    (1, "behnia"),
    (3, "moreira"),
    (4, "tran"),
    (5, "oswalt"),
    (6, "spring"),
    (7, "wang"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Re-run PHASE 3.3 on preserved papers")
    parser.add_argument("--paper-id", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    settings = get_settings()
    print(
        f"versions phase2={ExtractionPipeline.SCHEMA_VERSION}/"
        f"{ExtractionPipeline.RULE_VERSION} "
        f"phase3={BiologicalObservationPipeline.SCHEMA_VERSION}/"
        f"{BiologicalObservationPipeline.RULE_VERSION} "
        f"timeout={settings.llm_timeout_seconds}",
        flush=True,
    )
    provider = create_provider(settings)
    case_pipeline = ExtractionPipeline(provider)
    bio_pipeline = BiologicalObservationPipeline(provider)
    targets = PAPERS
    if args.paper_id is not None:
        targets = tuple(row for row in PAPERS if row[0] == args.paper_id)
        if not targets:
            raise SystemExit(f"Paper {args.paper_id} is not in the PHASE 3.3 set")

    with SessionLocal() as session:
        for paper_id, label in targets:
            print(f"=== PHASE 2 extract paper={paper_id} ({label}) ===", flush=True)
            case_run = case_pipeline.run(session, paper_id)
            print(
                f"paper={paper_id} case_run={case_run.id} "
                f"status={case_run.status.value} "
                f"schema={case_run.schema_version}",
                flush=True,
            )
            cases = list(
                session.scalars(
                    select(Case)
                    .where(
                        Case.paper_id == paper_id,
                        Case.extraction_run_id == case_run.id,
                    )
                    .order_by(Case.id)
                )
            )
            print(f"cases={[case.id for case in cases]}", flush=True)
            for case in cases:
                print(
                    f"=== PHASE 3.3 extract case={case.id} paper={paper_id} ===",
                    flush=True,
                )
                bio_run = bio_pipeline.run_case(
                    session, case.id, source_run_id=case_run.id
                )
                metrics = (bio_run.result_json or {}).get("metrics", {})
                print(
                    f"case={case.id} bio_run={bio_run.id} "
                    f"status={bio_run.status.value} "
                    f"observations={metrics.get('persisted_observations', 0)} "
                    f"episodes={metrics.get('regression_episodes', 0)} "
                    f"genotypes={metrics.get('genotype_records', 0)} "
                    f"irae={metrics.get('irae_records', 0)}",
                    flush=True,
                )


if __name__ == "__main__":
    main()
