import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.models import (
    AnalysisStatus,
    Evidence,
    EvidenceStatus,
    EvidenceType,
    Paper,
    PaperType,
    SupportType,
)
from app.schemas.records import EvidenceCreate


def _paper() -> Paper:
    return Paper(
        title="Test paper",
        authors=[],
        full_text_path="paper.pdf",
        extracted_text_path="paper.txt",
        paper_type=PaperType.OTHER,
        analysis_status=AnalysisStatus.INGESTED,
        content_sha256="a" * 64,
        page_count=1,
        raw_metadata={},
    )


def test_supported_evidence_requires_quote_and_locator():
    with pytest.raises(ValidationError):
        EvidenceCreate(
            paper_id=1,
            evidence_type=EvidenceType.OBSERVED_FACT,
            claim="Regression was observed.",
            source_quote=None,
            confidence=0.9,
        )


def test_system_inference_cannot_be_supported_in_phase_one():
    with pytest.raises(ValidationError):
        EvidenceCreate(
            paper_id=1,
            evidence_type=EvidenceType.SYSTEM_INFERENCE,
            claim="Inflammation caused regression.",
            source_quote="Inflammatory markers were elevated.",
            page=3,
            confidence=0.4,
        )


def test_unsupported_claim_is_explicitly_storable():
    record = EvidenceCreate(
        paper_id=1,
        evidence_type=EvidenceType.SYSTEM_INFERENCE,
        claim="A proposed but currently unsupported relation.",
        confidence=0.1,
        status=EvidenceStatus.UNSUPPORTED,
    )
    assert record.status == EvidenceStatus.UNSUPPORTED


def test_database_rejects_supported_evidence_without_provenance(db_session):
    paper = _paper()
    db_session.add(paper)
    db_session.commit()

    invalid = Evidence(
        paper_id=paper.id,
        evidence_type=EvidenceType.OBSERVED_FACT,
        claim="Regression was observed.",
        source_quote=None,
        confidence=0.9,
        support_type=SupportType.NEUTRAL,
        status=EvidenceStatus.SUPPORTED,
    )
    db_session.add(invalid)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
