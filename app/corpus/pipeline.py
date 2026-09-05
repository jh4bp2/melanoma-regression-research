from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.corpus.indexes import index_payload, load_seed_entities
from app.corpus.manifest import (
    CorpusManifestError,
    add_or_update_paper,
    find_duplicate,
    load_manifest,
    save_manifest,
    transition_paper,
)
from app.corpus.matrix import MATRIX_COLUMNS, build_case_row, empty_cell, skeleton
from app.corpus.quality import score_case
from app.corpus.runs import (
    latest_phase2_run,
    latest_phase3_runs,
    latest_reconciliation_runs,
    seed_cases_and_runs,
)
from app.corpus.states import PaperIntakeState, QualityStatus
from app.corpus.store import CorpusStore
from app.corpus.versions import BATCH_SIZE, CORPUS_INFRA_VERSION, frozen_ontology
from app.models import Paper
from app.services.paper_ingestion import ingest_pdf
from app.services.paper_parser import parse_pdf


LEGAL_SOURCE_HINTS = (
    "pmc-oa-opendata.s3.amazonaws.com",
    "ncbi.nlm.nih.gov/pmc",
    "europepmc.org",
    "unpaywall",
    "nihms",
)


@dataclass(frozen=True)
class BatchPlan:
    batch_number: int
    candidate_ids: list[str]


class CorpusPipeline:
    def __init__(self, store: CorpusStore):
        self.store = store

    def plan_batch(self, batch_number: int) -> BatchPlan:
        payload = load_manifest(self.store)
        pending = [
            row["candidate_id"]
            for row in payload["papers"]
            if row["extraction_status"]
            not in {
                PaperIntakeState.EXTRACTED.value,
                PaperIntakeState.AUDITED.value,
                PaperIntakeState.EXCLUDED.value,
                PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            }
        ]
        start = (batch_number - 1) * BATCH_SIZE
        return BatchPlan(
            batch_number=batch_number,
            candidate_ids=pending[start : start + BATCH_SIZE],
        )

    def resume_batch(self, batch_number: int) -> BatchPlan:
        planned = self.plan_batch(batch_number)
        payload = load_manifest(self.store)
        remaining = []
        for candidate_id in planned.candidate_ids:
            row = find_duplicate(payload, candidate_id=candidate_id)
            if row and row["extraction_status"] in {
                PaperIntakeState.EXTRACTED.value,
                PaperIntakeState.AUDITED.value,
            }:
                continue
            remaining.append(candidate_id)
        return BatchPlan(batch_number=batch_number, candidate_ids=remaining)

    def register_existing_paper(
        self,
        session: Session,
        row: dict[str, Any],
        *,
        paper: Paper | None = None,
    ) -> dict[str, Any]:
        payload = load_manifest(self.store)
        if paper is not None:
            duplicate = session.scalar(
                select(Paper).where(
                    or_(
                        Paper.id == paper.id,
                        Paper.content_sha256 == paper.content_sha256,
                        Paper.doi == paper.doi if paper.doi else False,
                        Paper.pmid == paper.pmid if paper.pmid else False,
                    )
                )
            )
            if duplicate is not None and duplicate.id != paper.id:
                raise CorpusManifestError(
                    f"Existing paper duplicate detected: {duplicate.id}"
                )
        add_or_update_paper(payload, row, allow_duplicate_update=True)
        save_manifest(self.store, payload)
        return row

    def ingest_manual_pdf(
        self,
        session: Session,
        candidate_id: str,
        pdf_path: Path,
        processed_dir: Path,
    ) -> Paper:
        payload = load_manifest(self.store)
        row = find_duplicate(payload, candidate_id=candidate_id)
        if row is None:
            raise CorpusManifestError(f"Unknown candidate {candidate_id}")
        parsed = parse_pdf(pdf_path)
        collision = find_duplicate(
            payload, doi=parsed.doi, pmid=parsed.pmid, sha256=parsed.content_sha256
        )
        if collision and collision["candidate_id"] != candidate_id:
            raise CorpusManifestError(
                f"PDF identifiers collide with {collision['candidate_id']}"
            )
        existing_db = session.scalar(
            select(Paper).where(
                or_(
                    Paper.content_sha256 == parsed.content_sha256,
                    Paper.doi == parsed.doi if parsed.doi else False,
                    Paper.pmid == parsed.pmid if parsed.pmid else False,
                )
            )
        )
        result = ingest_pdf(session, pdf_path, processed_dir)
        if existing_db is not None and result.created:
            raise CorpusManifestError("Ingestion created a duplicate paper")
        row["sha256"] = parsed.content_sha256
        row["page_count"] = parsed.page_count
        row["paper_id"] = result.paper.id
        row["fulltext_status"] = PaperIntakeState.FULLTEXT_FOUND.value
        transition_paper(row, "ingestion_status", PaperIntakeState.INGESTED)
        save_manifest(self.store, payload)
        return result.paper

    def mark_fulltext_unavailable(self, candidate_id: str, note: str = "") -> None:
        payload = load_manifest(self.store)
        row = find_duplicate(payload, candidate_id=candidate_id)
        if row is None:
            raise CorpusManifestError(f"Unknown candidate {candidate_id}")
        row["fulltext_status"] = PaperIntakeState.FULLTEXT_UNAVAILABLE.value
        row["ingestion_status"] = PaperIntakeState.FULLTEXT_UNAVAILABLE.value
        row["extraction_status"] = PaperIntakeState.FULLTEXT_UNAVAILABLE.value
        row["paper_id"] = None
        if note:
            row["notes"] = note
        save_manifest(self.store, payload)

    def rebuild_indexes_and_matrix(self, session: Session) -> dict[str, Any]:
        payload = load_manifest(self.store)
        all_cases = []
        all_lesions = []
        all_episodes = []
        all_states = []
        case_rows = []
        quality_rows = []
        for row in payload["papers"]:
            paper_id = row.get("paper_id")
            if paper_id is None:
                continue
            cases, phase2, phase3 = seed_cases_and_runs(session, paper_id)
            recon = latest_reconciliation_runs(session, paper_id)
            run_ids = [run.id for run in phase3]
            recon_ids = [run.id for run in recon]
            case_ids = [case.id for case in cases]
            cases, lesions, historical_episodes, states = load_seed_entities(
                session, case_ids, run_ids
            )
            if recon_ids:
                _cases, _lesions, recon_episodes, _states = load_seed_entities(
                    session, case_ids, recon_ids
                )
                episodes = recon_episodes or historical_episodes
            else:
                episodes = historical_episodes
            all_cases.extend(cases)
            all_lesions.extend(lesions)
            all_episodes.extend(episodes)
            all_states.extend(states)
            row["case_count"] = len(cases)
            row["lesion_count"] = len(lesions)
            row["episode_count"] = len(episodes)
            for case in cases:
                case_rows.append(
                    build_case_row(
                        session,
                        case,
                        run_ids,
                        phase2.id if phase2 else None,
                    )
                )
                quality_rows.append(
                    score_case(
                        session,
                        case,
                        observation_run_ids=run_ids,
                        event_run_id=phase2.id if phase2 else None,
                    )
                )
        indexes = index_payload(all_cases, all_lesions, all_episodes, all_states)
        lesion_rows = [
            {
                "row_type": "lesion",
                "case_id": item["case_id"],
                "lesion_id": item["lesion_id"],
                "cells": {column: empty_cell() for column in MATRIX_COLUMNS},
            }
            for item in indexes["lesion_index"]
        ]
        episode_rows = [
            {
                "row_type": "episode",
                "case_id": item["case_id"],
                "episode_id": item["episode_id"],
                "cells": {column: empty_cell() for column in MATRIX_COLUMNS},
            }
            for item in indexes["episode_index"]
        ]
        matrix = skeleton(
            case_rows=case_rows, lesion_rows=lesion_rows, episode_rows=episode_rows
        )
        self.store.write_json("frozen_ontology.json", frozen_ontology(), snapshot=True)
        self.store.write_json("case_index.json", indexes["case_index"], snapshot=True)
        self.store.write_json("lesion_index.json", indexes["lesion_index"], snapshot=True)
        self.store.write_json(
            "episode_index.json", indexes["episode_index"], snapshot=True
        )
        self.store.write_json("observation_matrix.json", matrix, snapshot=True)
        self.store.write_json(
            "quality_scores.json",
            {"version": CORPUS_INFRA_VERSION, "cases": quality_rows},
            snapshot=True,
        )
        save_manifest(self.store, payload)
        return {
            "cases": len(all_cases),
            "lesions": len(all_lesions),
            "episodes": len(all_episodes),
            "matrix_columns": len(MATRIX_COLUMNS),
            "quality_cases": len(quality_rows),
        }


def source_is_legal(url: str | None, access_source: str | None) -> bool:
    blob = f"{url or ''} {access_source or ''}".casefold()
    if any(token in blob for token in ("sci-hub", "libgen", "z-library", "shadow")):
        return False
    return True
