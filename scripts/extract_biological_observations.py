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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract directly observed biological findings"
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--paper-id", type=int)
    target.add_argument("--case-id", type=int)
    parser.add_argument(
        "--source-run-id",
        type=int,
        help="Preserved PHASE 2 Case/Timeline run; valid only with --case-id",
    )
    args = parser.parse_args()
    if args.source_run_id is not None and args.case_id is None:
        parser.error("--source-run-id requires --case-id")
    return args


def main() -> None:
    args = parse_args()
    settings = get_settings()
    provider = create_provider(settings)
    pipeline = BiologicalObservationPipeline(provider)
    init_db()

    with SessionLocal() as session:
        statement = select(Case).order_by(Case.id)
        if args.case_id is not None:
            statement = statement.where(Case.id == args.case_id)
        else:
            statement = statement.where(Case.paper_id == args.paper_id)
        cases = list(session.scalars(statement))
        if not cases:
            raise SystemExit("No matching cases found")

        failed = 0
        for case in cases:
            try:
                run = pipeline.run_case(
                    session,
                    case.id,
                    source_run_id=args.source_run_id,
                )
                metrics = (run.result_json or {}).get("metrics", {})
                print(
                    f"case={case.id} paper={case.paper_id} run={run.id} "
                    f"status={run.status.value} "
                    f"observations={metrics.get('persisted_observations', 0)}"
                )
            except Exception as exc:
                print(f"case={case.id} status=failed error={exc}")
                failed += 1
        if failed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
