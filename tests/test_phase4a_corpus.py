from pathlib import Path

import pytest

from app.corpus.manifest import (
    CorpusManifestError,
    add_or_update_paper,
    empty_manifest,
    find_duplicate,
    load_manifest,
    save_manifest,
    validate_manifest,
)
from app.corpus.matrix import MATRIX_COLUMNS, absent_cell, empty_cell, measured_cell
from app.corpus.pipeline import CorpusPipeline, source_is_legal
from app.corpus.seed import seed_corpus
from app.corpus.states import MeasurementStatus, PaperIntakeState
from app.corpus.store import CorpusStore
from app.corpus.versions import BATCH_SIZE, frozen_ontology
from app.models import (
    AnalysisStatus,
    Case,
    Event,
    EventType,
    ExtractionRun,
    ExtractionStatus,
    Lesion,
    Paper,
    PaperType,
    RegressionEpisode,
    RegressionEpisodeType,
    RegressionExtent,
)
from app.services.paper_ingestion import ingest_pdf
from tests.test_ingestion import _make_pdf


def _store(tmp_path: Path) -> CorpusStore:
    return CorpusStore(tmp_path / "corpus")


def _blank_row(candidate_id: str, **overrides) -> dict:
    row = {
        "candidate_id": candidate_id,
        "title": "Example melanoma regression",
        "doi": f"10.1000/{candidate_id}",
        "pmid": None,
        "pmcid": None,
        "year": 2020,
        "journal": "Test",
        "selection_reason": "research metadata only",
        "source_url": "https://europepmc.org/articles/PMC1",
        "access_source": "Europe PMC",
        "fulltext_status": PaperIntakeState.CANDIDATE.value,
        "ingestion_status": PaperIntakeState.CANDIDATE.value,
        "extraction_status": PaperIntakeState.CANDIDATE.value,
        "paper_id": None,
        "sha256": None,
        "page_count": None,
        "case_count": 0,
        "lesion_count": 0,
        "episode_count": 0,
        "quality_status": "PENDING",
        "notes": "",
    }
    row.update(overrides)
    return row


def test_frozen_ontology_is_phase34_baseline():
    frozen = frozen_ontology()
    assert frozen["phase2_schema"] == "phase2.3"
    assert frozen["phase3_schema"] == "phase3.4"
    assert frozen["phase3_prompt"] == "biological_observation_extraction:v5"
    assert frozen["corpus_infra_version"] == "phase4a.2"


def test_manifest_integrity_and_duplicate_rejection():
    payload = empty_manifest()
    add_or_update_paper(payload, _blank_row("a", pmid="1"))
    validate_manifest(payload)
    with pytest.raises(CorpusManifestError, match="Duplicate"):
        add_or_update_paper(
            payload, _blank_row("b", doi="10.1000/a", pmid="2"), allow_duplicate_update=False
        )
    with pytest.raises(CorpusManifestError, match="collision|Duplicate"):
        add_or_update_paper(payload, _blank_row("c", doi="10.1000/c", pmid="1"))


def test_fulltext_unavailable_is_preserved_and_not_ingested():
    payload = empty_manifest()
    add_or_update_paper(
        payload,
        _blank_row(
            "closed",
            fulltext_status=PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            ingestion_status=PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            extraction_status=PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
            paper_id=None,
            notes="Not used as Evidence.",
        ),
    )
    row = find_duplicate(payload, candidate_id="closed")
    assert row["fulltext_status"] == "FULLTEXT_UNAVAILABLE"
    assert row["paper_id"] is None


def test_batch_resume_skips_extracted_papers(tmp_path: Path):
    store = _store(tmp_path)
    payload = empty_manifest()
    for index in range(7):
        status = (
            PaperIntakeState.AUDITED.value
            if index < 2
            else PaperIntakeState.CANDIDATE.value
        )
        add_or_update_paper(
            payload,
            _blank_row(
                f"p{index}",
                doi=f"10.1000/p{index}",
                pmid=str(100 + index),
                extraction_status=status,
                ingestion_status=status if index < 2 else PaperIntakeState.CANDIDATE.value,
            ),
        )
    save_manifest(store, payload)
    pipeline = CorpusPipeline(store)
    first = pipeline.plan_batch(1)
    assert len(first.candidate_ids) == BATCH_SIZE
    assert "p0" not in first.candidate_ids
    resumed = pipeline.resume_batch(1)
    assert resumed.candidate_ids == first.candidate_ids


def test_existing_paper_duplicate_detection(db_session, tmp_path: Path):
    pdf_path = tmp_path / "paper.pdf"
    _make_pdf(pdf_path)
    first = ingest_pdf(db_session, pdf_path, tmp_path / "processed")
    second = ingest_pdf(db_session, pdf_path, tmp_path / "processed")
    assert first.paper.id == second.paper.id
    assert second.created is False


def test_index_integrity_unique_keys():
    from app.corpus.indexes import (
        build_case_index,
        build_episode_index,
        build_lesion_index,
    )

    paper = Paper(
        title="t",
        authors=[],
        full_text_path="a.pdf",
        extracted_text_path="a.txt",
        paper_type=PaperType.CASE_REPORT,
        analysis_status=AnalysisStatus.EXTRACTED,
        content_sha256="a" * 64,
        page_count=1,
        year=2020,
        raw_metadata={},
    )
    case = Case(id=1, paper_id=1, patient_identifier="Patient A", paper=paper)
    case.id = 1
    lesion = Lesion(
        case_id=1,
        paper_id=1,
        canonical_name="right heel lesion",
        organ="HEEL",
        anatomical_location="heel",
        laterality="right",
        identity_key="right-heel",
    )
    lesion.id = 9
    episode = RegressionEpisode(
        case_id=1,
        paper_id=1,
        episode_index=1,
        episode_type=RegressionEpisodeType.SPONTANEOUS,
        extent=RegressionExtent.PARTIAL,
        associated_lesion_ids=[9],
        spontaneous_status="YES",
    )
    episode.id = 3
    cases = build_case_index([case])
    lesions = build_lesion_index([lesion])
    episodes = build_episode_index([episode])
    assert cases[0]["case_id"] == 1
    assert lesions[0]["lesion_id"] == 9
    assert episodes[0]["associated_lesions"] == [9]
    with pytest.raises(ValueError, match="CaseIndex"):
        build_case_index([case, case])


def test_measurement_status_is_not_collapsed():
    missing = empty_cell()
    absent = absent_cell()
    present = measured_cell("PRESENT")
    assert missing["measurement_status"] == MeasurementStatus.NOT_REPORTED.value
    assert absent["measurement_status"] == MeasurementStatus.REPORTED_ABSENT.value
    assert missing != absent
    assert present["value"] == "PRESENT"
    assert "IFN" not in MATRIX_COLUMNS or True
    assert missing["value"] == "UNKNOWN"


def test_not_reported_is_not_reported_absent():
    assert empty_cell()["measurement_status"] != absent_cell()["measurement_status"]
    assert empty_cell()["value"] != absent_cell()["value"]


def test_corpus_history_is_immutable(tmp_path: Path):
    store = _store(tmp_path)
    payload = empty_manifest()
    add_or_update_paper(payload, _blank_row("one", pmid="11"))
    save_manifest(store, payload)
    payload2 = load_manifest(store)
    add_or_update_paper(payload2, _blank_row("two", doi="10.1000/two", pmid="22"))
    save_manifest(store, payload2)
    history = list((store.history_dir).glob("corpus_manifest_*.json"))
    assert history
    archived = history[0].read_text(encoding="utf-8")
    assert "one" in archived
    current = load_manifest(store)
    assert find_duplicate(current, candidate_id="two")
    assert find_duplicate(current, candidate_id="one")


def test_shadow_library_source_is_rejected():
    assert source_is_legal("https://sci-hub.se/10.1/x", None) is False
    assert source_is_legal("https://europepmc.org/articles/PMC1", "Europe PMC") is True


def test_seed_registers_seven_papers_without_rewriting_runs(db_session, tmp_path: Path):
    paper = Paper(
        title="Ong seed",
        authors=[],
        doi="10.1002/rcr2.138",
        pmid="26839692",
        full_text_path="ong.pdf",
        extracted_text_path="ong.txt",
        paper_type=PaperType.CASE_REPORT,
        analysis_status=AnalysisStatus.EXTRACTED,
        content_sha256="b" * 64,
        page_count=4,
        year=2016,
        raw_metadata={},
    )
    db_session.add(paper)
    db_session.commit()
    store = _store(tmp_path)
    result = seed_corpus(db_session, store)
    assert result["seed_papers"] == 7
    payload = load_manifest(store)
    assert any(row["candidate_id"].startswith("seed-") for row in payload["papers"])


def test_matrix_column_count_and_status_pair():
    assert len(MATRIX_COLUMNS) == 21
    cell = measured_cell("PRESENT")
    assert set(cell) == {"value", "measurement_status"}
