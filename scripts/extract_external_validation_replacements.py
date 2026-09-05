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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract replacement external-validation papers on frozen 3.2"
    )
    parser.add_argument("--paper-id", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
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
    init_db()

    with SessionLocal() as session:
        print(f"=== PHASE 2 extract paper={args.paper_id} ===", flush=True)
        case_run = case_pipeline.run(session, args.paper_id)
        print(
            f"paper={args.paper_id} case_run={case_run.id} "
            f"status={case_run.status.value} "
            f"schema={case_run.schema_version} rule={case_run.rule_version}",
            flush=True,
        )
        cases = list(
            session.scalars(
                select(Case)
                .where(
                    Case.paper_id == args.paper_id,
                    Case.extraction_run_id == case_run.id,
                )
                .order_by(Case.id)
            )
        )
        if not cases:
            raise SystemExit(f"No cases created for paper {args.paper_id} run {case_run.id}")
        print(f"cases={[case.id for case in cases]}", flush=True)
        for case in cases:
            print(
                f"=== PHASE 3.2 extract case={case.id} paper={args.paper_id} ===",
                flush=True,
            )
            bio_run = bio_pipeline.run_case(
                session, case.id, source_run_id=case_run.id
            )
            metrics = (bio_run.result_json or {}).get("metrics", {})
            print(
                f"case={case.id} bio_run={bio_run.id} "
                f"status={bio_run.status.value} "
                f"schema={bio_run.schema_version} rule={bio_run.rule_version} "
                f"prompt={bio_run.prompt_version} "
                f"observations={metrics.get('persisted_observations', 0)}",
                flush=True,
            )


if __name__ == "__main__":
    main()
