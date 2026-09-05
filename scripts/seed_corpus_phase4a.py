from __future__ import annotations

from app.corpus.audit import write_batch_audit
from app.corpus.pipeline import CorpusPipeline
from app.corpus.seed import seed_corpus
from app.corpus.store import CorpusStore
from app.db.init_db import init_db
from app.db.session import SessionLocal


def main() -> None:
    init_db()
    store = CorpusStore()
    with SessionLocal() as session:
        summary = seed_corpus(session, store)
        payload = store.read_json("corpus_manifest.json", {"papers": []})
        attempted = [
            row["candidate_id"]
            for row in payload["papers"]
            if row.get("role") in {"development", "external_validation"}
        ]
        write_batch_audit(
            store,
            batch_number=0,
            attempted=attempted,
            summary=summary,
            extra_notes=[
                "Seed registration only. Existing PHASE 2.3 / 3.4 runs were not rewritten.",
                "No new papers were searched or added.",
            ],
        )
        print(summary, flush=True)
        print("batch runner idle; waiting for candidate list", flush=True)


if __name__ == "__main__":
    main()
