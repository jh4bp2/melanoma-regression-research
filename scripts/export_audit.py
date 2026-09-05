import argparse
import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select

from app.core.config import PROJECT_ROOT
from app.db.session import SessionLocal
from app.models import (
    Case,
    Evidence,
    ExtractionRun,
    FieldEvidenceLink,
    Paper,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export one paper extraction audit")
    parser.add_argument("--paper-id", type=int, required=True)
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def _json_value(value):
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _record(record, excluded: set[str] | None = None) -> dict:
    excluded = excluded or set()
    return {
        column.name: _json_value(getattr(record, column.name))
        for column in record.__table__.columns
        if column.name not in excluded
    }


def _field_evidence(
    session, entity_type: str, entity_id: int, run_id: int
) -> list[dict]:
    rows = session.execute(
        select(FieldEvidenceLink.field_name, Evidence)
        .join(Evidence, Evidence.id == FieldEvidenceLink.evidence_id)
        .where(
            FieldEvidenceLink.entity_type == entity_type,
            FieldEvidenceLink.entity_id == entity_id,
            FieldEvidenceLink.extraction_run_id == run_id,
        )
        .order_by(FieldEvidenceLink.field_name, Evidence.id)
    )
    return [
        {"field_name": field_name, "evidence": _record(evidence)}
        for field_name, evidence in rows
    ]


def build_export(session, paper: Paper, run: ExtractionRun) -> dict:
    cases = list(
        session.scalars(
            select(Case).where(Case.paper_id == paper.id).order_by(Case.id)
        )
    )
    return {
        "export_type": "PHASE_2_RESEARCH_AUDIT",
        "warning": "Association does not imply causation.",
        "paper": _record(paper, {"raw_metadata"}),
        "extraction_run": _record(run),
        "paper_field_evidence": _field_evidence(
            session, "paper", paper.id, run.id
        ),
        "cases": [
            {
                "case": _record(case),
                "field_evidence": _field_evidence(
                    session, "case", case.id, run.id
                ),
                "timeline": [
                    {
                        "event": _record(event),
                        "field_evidence": _field_evidence(
                            session, "event", event.id, run.id
                        ),
                    }
                    for event in sorted(
                        (
                            event
                            for event in case.events
                            if event.extraction_run_id == run.id
                        ),
                        key=lambda item: (
                            item.relative_day is None,
                            item.relative_day or 0,
                            item.event_date is None,
                            item.event_date or date.max,
                            item.id,
                        ),
                    )
                ],
            }
            for case in cases
        ],
    }


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or PROJECT_ROOT / "data" / "processed" / "audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as session:
        paper = session.get(Paper, args.paper_id)
        if paper is None:
            raise SystemExit(f"Paper {args.paper_id} not found")
        run = (
            session.get(ExtractionRun, args.run_id)
            if args.run_id is not None
            else session.scalar(
                select(ExtractionRun)
                .where(ExtractionRun.paper_id == paper.id)
                .order_by(ExtractionRun.id.desc())
                .limit(1)
            )
        )
        if run is None:
            raise SystemExit(f"Paper {args.paper_id} has no extraction run")
        if run.paper_id != paper.id:
            raise SystemExit(f"Run {run.id} does not belong to paper {paper.id}")
        payload = build_export(session, paper, run)

    output_path = output_dir / f"paper_{paper.id}_run_{run.id}.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
