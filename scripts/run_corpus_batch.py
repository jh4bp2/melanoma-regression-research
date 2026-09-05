from __future__ import annotations

import argparse

from app.corpus.audit import write_batch_audit
from app.corpus.pipeline import CorpusPipeline
from app.corpus.store import CorpusStore
from app.corpus.versions import BATCH_SIZE
from app.db.init_db import init_db
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one corpus batch of up to 5 papers")
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--resume", action="store_true", default=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    store = CorpusStore()
    pipeline = CorpusPipeline(store)
    plan = pipeline.resume_batch(args.batch) if args.resume else pipeline.plan_batch(args.batch)
    print(
        f"corpus batch={args.batch} size={BATCH_SIZE} pending={plan.candidate_ids}",
        flush=True,
    )
    if not plan.candidate_ids:
        print("nothing to extract; rebuild indexes from current seed", flush=True)
    with SessionLocal() as session:
        summary = pipeline.rebuild_indexes_and_matrix(session)
    write_batch_audit(
        store,
        batch_number=args.batch,
        attempted=plan.candidate_ids,
        summary=summary,
        extra_notes=[
            "PHASE 4A does not search new papers. Provide a candidate list first.",
            "Frozen PHASE 2.3 / 3.4 ontology was not modified.",
        ],
    )
    print(summary, flush=True)


if __name__ == "__main__":
    main()
