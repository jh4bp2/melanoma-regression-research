from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select

from app.corpus.pipeline import CorpusPipeline
from app.corpus.reconciliation import reconcile_paper
from app.corpus.runs import latest_reconciliation_runs, seed_cases_and_runs
from app.corpus.store import CorpusStore
from app.corpus.versions import CORPUS_INFRA_VERSION, CORPUS_RULE_VERSION, frozen_ontology
from app.core.config import PROJECT_ROOT
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models import Lesion, LesionCollection, RegressionEpisode


TARGET_PAPER_IDS = (8, 9, 10, 11, 12, 13, 14, 15, 16, 17)
AUDIT_PATH = PROJECT_ROOT / "data" / "processed" / "audit" / "phase4a2_ontology_patch.md"


def _counts(session, paper_ids: list[int], recon_only: bool = False) -> dict[str, int]:
    collections = 0
    collection_only = 0
    members = 0
    episodes = 0
    for paper_id in paper_ids:
        cases, _phase2, phase3 = seed_cases_and_runs(session, paper_id)
        if not cases:
            continue
        if recon_only:
            runs = latest_reconciliation_runs(session, paper_id)
        else:
            runs = phase3
        run_ids = [run.id for run in runs] or [-1]
        case_ids = [case.id for case in cases]
        episode_rows = list(
            session.scalars(
                select(RegressionEpisode).where(
                    RegressionEpisode.case_id.in_(case_ids),
                    RegressionEpisode.created_from_run_id.in_(run_ids),
                )
            )
        )
        collection_rows = list(
            session.scalars(
                select(LesionCollection).where(
                    LesionCollection.case_id.in_(case_ids),
                    LesionCollection.created_from_run_id.in_(run_ids),
                )
            )
        )
        episodes += len(episode_rows)
        collections += len(collection_rows)
        collection_only += sum(1 for item in collection_rows if item.collection_only)
        members += sum(len(item.memberships) for item in collection_rows)
    return {
        "collections": collections,
        "collection_only": collection_only,
        "members": members,
        "episodes": episodes,
    }


def main() -> None:
    init_db()
    store = CorpusStore()
    before: dict[str, int] = {}
    after_rows: list[dict] = []
    totals = Counter()
    with SessionLocal() as session:
        before = _counts(session, list(TARGET_PAPER_IDS), recon_only=False)
        for paper_id in TARGET_PAPER_IDS:
            print(f"=== reconcile paper {paper_id} ===", flush=True)
            result = reconcile_paper(session, paper_id)
            after_rows.append(result)
            for key in (
                "collections_created",
                "collection_only",
                "linked_members",
                "episodes_before",
                "episodes_after",
                "merged_episodes",
                "split_episodes",
                "fact_inversions",
                "rejected_claims",
                "name_improvements",
            ):
                totals[key] += result.get(key, 0)
            print(result, flush=True)
        after = _counts(session, list(TARGET_PAPER_IDS), recon_only=True)
        pipeline = CorpusPipeline(store)
        index_summary = pipeline.rebuild_indexes_and_matrix(session)
    payload = store.read_json("corpus_manifest.json", {})
    payload["frozen_ontology"] = frozen_ontology()
    payload["version"] = CORPUS_INFRA_VERSION
    store.write_json("corpus_manifest.json", payload, snapshot=True)
    store.write_json("frozen_ontology.json", frozen_ontology(), snapshot=True)
    lines = [
        "# PHASE 4A.2 corpus ontology patch",
        "",
        f"- corpus infra: {CORPUS_INFRA_VERSION}",
        f"- rule: {CORPUS_RULE_VERSION}",
        "- PHASE 2/3 schema, rule, and prompt were not redesigned.",
        "- Historical extraction runs were preserved. New reconciliation runs were added.",
        "",
        "## Before / after (Batch 1–3 extracted papers)",
        "",
        f"- LesionCollection before: {before['collections']}",
        f"- LesionCollection after: {after['collections']}",
        f"- COLLECTION_ONLY after: {after['collection_only']}",
        f"- linked members after: {after['members']}",
        f"- RegressionEpisode before: {before['episodes']}",
        f"- RegressionEpisode after (canonical): {after['episodes']}",
        "",
        "## Patch actions",
        "",
        f"- recovered collections: {totals['collections_created']}",
        f"- merged duplicate/fragmented episodes: {totals['merged_episodes']}",
        f"- split true distinct episodes: {totals['split_episodes']}",
        f"- FACT_INVERSION count: {totals['fact_inversions']}",
        f"- rejected contradiction outputs: {totals['rejected_claims']}",
        f"- canonical lesion-name improvements: {totals['name_improvements']}",
        "",
        "## Per paper",
        "",
    ]
    for row in after_rows:
        lines.append(
            f"- paper {row.get('paper_id')}: collections={row.get('collections_created')} "
            f"episodes {row.get('episodes_before')}→{row.get('episodes_after')} "
            f"merged={row.get('merged_episodes')} split={row.get('split_episodes')} "
            f"inversions={row.get('fact_inversions')} names={row.get('name_improvements')}"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Abstracts were not used as Evidence.",
            "- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.",
            "- PHASE 4B and Batch 4 were not started.",
            f"- index rebuild: {index_summary}",
            "",
        ]
    )
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"before": before, "after": after, "totals": dict(totals)}, indent=2))
    print(f"wrote {AUDIT_PATH}")


if __name__ == "__main__":
    main()
