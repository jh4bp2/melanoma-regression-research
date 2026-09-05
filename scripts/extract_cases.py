import argparse

from sqlalchemy import select

from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.llm.provider import create_provider
from app.models import Paper
from app.services.extraction_pipeline import ExtractionPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract cases from ingested papers")
    parser.add_argument("--paper-id", type=int, help="Extract one paper only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    provider = create_provider(settings)
    pipeline = ExtractionPipeline(provider)
    init_db()

    with SessionLocal() as session:
        statement = select(Paper).order_by(Paper.id)
        if args.paper_id is not None:
            statement = statement.where(Paper.id == args.paper_id)
        papers = list(session.scalars(statement))
        if args.paper_id is not None and not papers:
            raise SystemExit(f"Paper {args.paper_id} not found")

        completed = 0
        failed = 0
        for paper in papers:
            try:
                run = pipeline.run(session, paper.id)
                print(f"paper={paper.id} run={run.id} status={run.status.value}")
                completed += 1
            except Exception as exc:
                print(f"paper={paper.id} status=failed error={exc}")
                failed += 1

    print(f"Extraction finished: {completed} processed, {failed} failed.")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
