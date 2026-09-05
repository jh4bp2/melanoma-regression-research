from __future__ import annotations

from typing import Any

from app.corpus.states import (
    ExclusionReason,
    PaperIntakeState,
    QualityStatus,
    can_transition,
)
from app.corpus.store import CorpusStore
from app.corpus.versions import CORPUS_INFRA_VERSION, frozen_ontology


MANIFEST_NAME = "corpus_manifest.json"
REQUIRED_FIELDS = (
    "candidate_id",
    "title",
    "doi",
    "pmid",
    "pmcid",
    "year",
    "journal",
    "selection_reason",
    "source_url",
    "access_source",
    "fulltext_status",
    "ingestion_status",
    "extraction_status",
    "paper_id",
    "sha256",
    "page_count",
    "case_count",
    "lesion_count",
    "episode_count",
    "quality_status",
    "notes",
)


class CorpusManifestError(ValueError):
    pass


def empty_manifest() -> dict[str, Any]:
    return {
        "purpose": (
            "Research corpus intake metadata. selection_reason is not Evidence."
        ),
        "version": CORPUS_INFRA_VERSION,
        "frozen_ontology": frozen_ontology(),
        "papers": [],
        "pressure_points": [],
    }


def load_manifest(store: CorpusStore) -> dict[str, Any]:
    payload = store.read_json(MANIFEST_NAME, empty_manifest())
    validate_manifest(payload)
    return payload


def save_manifest(store: CorpusStore, payload: dict[str, Any]) -> None:
    validate_manifest(payload)
    store.write_json(MANIFEST_NAME, payload, snapshot=True)


def validate_manifest(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict) or "papers" not in payload:
        raise CorpusManifestError("Manifest must contain a papers list")
    seen_ids: set[str] = set()
    seen_doi: set[str] = set()
    seen_pmid: set[str] = set()
    for row in payload["papers"]:
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            raise CorpusManifestError(
                f"{row.get('candidate_id')} missing fields: {missing}"
            )
        candidate_id = row["candidate_id"]
        if candidate_id in seen_ids:
            raise CorpusManifestError(f"Duplicate candidate_id: {candidate_id}")
        seen_ids.add(candidate_id)
        PaperIntakeState(row["fulltext_status"])
        PaperIntakeState(row["ingestion_status"])
        PaperIntakeState(row["extraction_status"])
        QualityStatus(row["quality_status"])
        if row.get("exclusion_reason"):
            ExclusionReason(row["exclusion_reason"])
        doi = _norm_id(row.get("doi"))
        pmid = _norm_id(row.get("pmid"))
        if doi:
            if doi in seen_doi:
                raise CorpusManifestError(f"Duplicate DOI: {doi}")
            seen_doi.add(doi)
        if pmid:
            if pmid in seen_pmid:
                raise CorpusManifestError(f"Duplicate PMID: {pmid}")
            seen_pmid.add(pmid)


def _norm_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text.casefold() or None


def find_duplicate(
    payload: dict[str, Any],
    *,
    doi: str | None = None,
    pmid: str | None = None,
    sha256: str | None = None,
    candidate_id: str | None = None,
) -> dict[str, Any] | None:
    doi_n = _norm_id(doi)
    pmid_n = _norm_id(pmid)
    sha_n = _norm_id(sha256)
    for row in payload["papers"]:
        if candidate_id and row["candidate_id"] == candidate_id:
            return row
        if doi_n and _norm_id(row.get("doi")) == doi_n:
            return row
        if pmid_n and _norm_id(row.get("pmid")) == pmid_n:
            return row
        if sha_n and _norm_id(row.get("sha256")) == sha_n:
            return row
    return None


def add_or_update_paper(
    payload: dict[str, Any],
    row: dict[str, Any],
    *,
    allow_duplicate_update: bool = True,
) -> dict[str, Any]:
    for field in REQUIRED_FIELDS:
        row.setdefault(field, None)
    existing = find_duplicate(
        payload,
        doi=row.get("doi"),
        pmid=row.get("pmid"),
        sha256=row.get("sha256"),
        candidate_id=row.get("candidate_id"),
    )
    if existing is not None:
        if not allow_duplicate_update:
            raise CorpusManifestError(
                f"Duplicate paper already in corpus: {existing['candidate_id']}"
            )
        if existing["candidate_id"] != row["candidate_id"]:
            raise CorpusManifestError(
                f"Identifier collision between {existing['candidate_id']} "
                f"and {row['candidate_id']}"
            )
        existing.update(row)
        validate_manifest(payload)
        return existing
    payload["papers"].append(row)
    validate_manifest(payload)
    return row


def transition_paper(
    row: dict[str, Any],
    field: str,
    nxt: PaperIntakeState,
) -> None:
    current = PaperIntakeState(row[field])
    if not can_transition(current, nxt):
        raise CorpusManifestError(
            f"Illegal {field} transition {current.value} -> {nxt.value}"
        )
    row[field] = nxt.value


def record_pressure_point(
    payload: dict[str, Any],
    *,
    candidate_id: str,
    note: str,
) -> None:
    payload.setdefault("pressure_points", []).append(
        {
            "type": "ONTOLOGY_PRESSURE_POINT",
            "candidate_id": candidate_id,
            "note": note,
            "action": "Do not change frozen schema/rule/prompt until batch review.",
        }
    )
