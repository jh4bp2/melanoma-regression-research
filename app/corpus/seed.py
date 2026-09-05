from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.corpus.manifest import add_or_update_paper, empty_manifest, save_manifest
from app.corpus.pipeline import CorpusPipeline
from app.corpus.runs import seed_cases_and_runs
from app.corpus.states import PaperIntakeState, QualityStatus
from app.corpus.store import CorpusStore
from app.corpus.tracks import HYPOTHESIS_TRACKS, TRACK_POLICY
from app.corpus.versions import SEED_PAPERS
from app.core.config import PROJECT_ROOT
from app.models import Paper


PAPERS_MANIFEST = PROJECT_ROOT / "data" / "papers" / "manifest.json"


SEED_SELECTION = {
    1: "Development seed: Behnia metastatic melanoma mixed-response imaging case",
    2: "Development seed: Ong solitary pulmonary metastasis with necrosis",
    3: "External-validation seed: Moreira in-transit regression after infection/surgery",
    4: "External-validation seed: Tran vaccination-associated cutaneous regression",
    5: "External-validation seed: Oswalt multiple regression episodes and irAE/genotype",
    6: "External-validation seed: Spring acral melanoma with leukoderma",
    7: "External-validation seed: Wang two-case completely regressed primaries",
}


def seed_corpus(session: Session, store: CorpusStore | None = None) -> dict[str, Any]:
    store = store or CorpusStore()
    store.ensure()
    payload = empty_manifest()
    papers_manifest = _load_papers_manifest()
    by_sha = {
        row.get("local_sha256"): row
        for row in papers_manifest.get("papers", [])
        if row.get("local_sha256")
    }
    by_doi = {
        (row.get("candidate_identifiers") or {}).get("doi"): row
        for row in papers_manifest.get("papers", [])
        if (row.get("candidate_identifiers") or {}).get("doi")
    }

    for seed in SEED_PAPERS:
        paper = session.get(Paper, seed["paper_id"])
        if paper is None:
            continue
        cases, _phase2, phase3 = seed_cases_and_runs(session, paper.id)
        source = by_sha.get(paper.content_sha256) or by_doi.get(paper.doi) or {}
        ids = source.get("candidate_identifiers") or {}
        row = {
            "candidate_id": seed["candidate_id"],
            "title": paper.title,
            "doi": paper.doi or ids.get("doi"),
            "pmid": paper.pmid or ids.get("pmid"),
            "pmcid": ids.get("pmcid"),
            "year": paper.year,
            "journal": paper.journal,
            "selection_reason": SEED_SELECTION[paper.id],
            "source_url": source.get("source_url") or paper.source_url,
            "access_source": source.get("access_source") or source.get("source_dataset"),
            "fulltext_status": PaperIntakeState.FULLTEXT_FOUND.value,
            "ingestion_status": PaperIntakeState.INGESTED.value,
            "extraction_status": (
                PaperIntakeState.AUDITED.value
                if phase3
                else PaperIntakeState.INGESTED.value
            ),
            "paper_id": paper.id,
            "sha256": paper.content_sha256,
            "page_count": paper.page_count,
            "case_count": len(cases),
            "lesion_count": 0,
            "episode_count": 0,
            "quality_status": QualityStatus.SEED.value,
            "notes": (
                f"Seed {seed['role']} paper. Existing extraction runs were not rewritten."
            ),
            "role": seed["role"],
            "label": seed["label"],
        }
        add_or_update_paper(payload, row)

    for source in papers_manifest.get("papers", []):
        if source.get("status") != "FULLTEXT_UNAVAILABLE":
            continue
        ids = source.get("candidate_identifiers") or {}
        candidate_id = f"unavailable-{(ids.get('pmid') or ids.get('doi') or 'unknown')}"
        row = {
            "candidate_id": candidate_id,
            "title": source.get("title"),
            "doi": ids.get("doi"),
            "pmid": ids.get("pmid"),
            "pmcid": ids.get("pmcid"),
            "year": None,
            "journal": None,
            "selection_reason": "Previously considered; legal full text was not available",
            "source_url": source.get("source_url"),
            "access_source": source.get("access_source"),
            "fulltext_status": PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            "ingestion_status": PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            "extraction_status": PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            "paper_id": None,
            "sha256": None,
            "page_count": None,
            "case_count": 0,
            "lesion_count": 0,
            "episode_count": 0,
            "quality_status": QualityStatus.PENDING.value,
            "notes": "Abstract/closed-access only. Not used as Evidence.",
            "exclusion_reason": None,
        }
        add_or_update_paper(payload, row)

    save_manifest(store, payload)
    store.write_json(
        "hypothesis_tracks.json",
        {"tracks": HYPOTHESIS_TRACKS, "policy": TRACK_POLICY, "assigned_cases": []},
        snapshot=True,
    )
    pipeline = CorpusPipeline(store)
    summary = pipeline.rebuild_indexes_and_matrix(session)
    return {"seed_papers": len(SEED_PAPERS), **summary}


def _load_papers_manifest() -> dict[str, Any]:
    if not PAPERS_MANIFEST.is_file():
        return {"papers": []}
    return json.loads(PAPERS_MANIFEST.read_text(encoding="utf-8"))
