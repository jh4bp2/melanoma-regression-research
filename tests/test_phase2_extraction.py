import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.llm.base import StructuredExtractionError
from app.llm.fake import FakeLLMProvider
from app.models import (
    AnalysisStatus,
    Evidence,
    Event,
    ExtractionStatus,
    FieldEvidenceLink,
    Paper,
    PaperType,
)
from app.schemas.extraction import (
    BiologicalObservationCandidate,
    CaseCandidate,
    CaseDetectionResult,
    EvidenceReference,
    TimelineEventCandidate,
)
from app.services.chunking import TextChunk, chunk_pages, read_page_text
from app.services.evidence_verifier import EvidenceVerifier, normalize_text
from app.services.extraction_pipeline import ExtractionPipeline


FIXTURES = Path(__file__).parent / "fixtures"


def _not_reported():
    return {"value": None, "status": "NOT_REPORTED", "evidence_refs": []}


def _metadata_response():
    return {
        key: _not_reported()
        for key in (
            "title",
            "authors",
            "year",
            "journal",
            "doi",
            "pmid",
            "abstract",
            "paper_type",
        )
    }


def _detection_yes(quote="A 67-year-old man was diagnosed with metastatic melanoma."):
    return {
        "existence": "YES",
        "confidence": 0.98,
        "evidence_refs": [
            {
                "page": 2,
                "quote": quote,
                "section": "Case Presentation",
                "evidence_type": "OBSERVED_FACT",
            }
        ],
    }


def _empty_case(identifier, quote, page=2):
    fields = {
        key: _not_reported()
        for key in (
            "age",
            "sex",
            "melanoma_subtype",
            "primary_site",
            "stage",
            "metastatic_sites",
            "diagnosis_date",
            "regression_start_date",
            "first_observed_reduction",
            "regression_confirmed_date",
            "regression_duration",
            "regression_type",
            "regression_extent_clinical",
            "viable_tumor_at_pathology",
            "treatment_before_regression",
            "treatment_status",
            "preceding_events",
            "outcome",
            "follow_up_duration",
        )
    }
    fields["patient_identifier"] = {
        "value": identifier,
        "status": "REPORTED",
        "evidence_refs": [
            {
                "page": page,
                "quote": quote,
                "section": "Case Presentation",
                "evidence_type": "OBSERVED_FACT",
            }
        ],
    }
    fields["confidence"] = 0.9
    return fields


def _timeline_response():
    return {
        "events": [
            {
                "event_type": "biopsy",
                "description": "A biopsy was performed.",
                "event_date": None,
                "relative_time": "Two weeks before regression",
                "date_precision": "RELATIVE",
                "relation_to_regression": "BEFORE",
                "temporal_order_confidence": 0.95,
                "evidence_refs": [
                    {
                        "page": 2,
                        "quote": "Two weeks before regression, a biopsy was performed.",
                        "section": "Case Presentation",
                        "evidence_type": "OBSERVED_FACT",
                    }
                ],
            }
        ]
    }


def _paper(db_session, extracted_path):
    paper = Paper(
        title=None,
        authors=[],
        full_text_path="fixture.pdf",
        extracted_text_path=str(extracted_path),
        paper_type=PaperType.OTHER,
        analysis_status=AnalysisStatus.INGESTED,
        content_sha256="b" * 64,
        page_count=3,
        raw_metadata={},
    )
    db_session.add(paper)
    db_session.commit()
    db_session.refresh(paper)
    return paper


def test_valid_golden_case_and_relative_timeline(db_session):
    expected_case = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    paper = _paper(db_session, FIXTURES / "melanoma_case.txt")
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            _detection_yes(),
            {"cases": [expected_case]},
            _timeline_response(),
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)

    assert run.status == ExtractionStatus.COMPLETED
    assert len(paper.cases) == 1
    case = paper.cases[0]
    assert case.age == 67
    assert case.melanoma_subtype is None
    assert case.field_statuses["melanoma_subtype"]["status"] == "NOT_REPORTED"
    assert len(case.events) == 1
    assert case.events[0].relative_time == "Two weeks before regression"
    assert case.events[0].relative_day == -14
    assert case.events[0].date_precision.value == "relative"
    assert db_session.query(Evidence).count() > 0


def test_hallucinated_quote_is_not_persisted_as_confirmed_fact(db_session):
    expected_case = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    expected_case["age"]["evidence_refs"][0]["quote"] = "The patient was 99 years old."
    paper = _paper(db_session, FIXTURES / "melanoma_case.txt")
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            _detection_yes(),
            {"cases": [expected_case]},
            {"events": []},
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)

    case = paper.cases[0]
    assert run.status == ExtractionStatus.PARTIAL
    assert "PARTIAL_UNVERIFIED_QUOTE" in run.reason_codes
    assert "PARTIAL_FIELD_WITHOUT_EVIDENCE" in run.reason_codes
    assert case.age is None
    assert case.field_statuses["age"]["status"] == "UNCERTAIN"
    assert run.result_json["verification_failures"][0]["status"] == "UNVERIFIED"
    assert not any(
        evidence.source_quote == "The patient was 99 years old."
        for evidence in db_session.query(Evidence)
    )


def test_multi_case_paper(db_session, tmp_path):
    text = (FIXTURES / "melanoma_case.txt").read_text(encoding="utf-8")
    text = text.replace(
        "A 67-year-old man was diagnosed with metastatic melanoma.",
        "A 67-year-old man was diagnosed with metastatic melanoma.\n"
        "A 54-year-old woman was also diagnosed with metastatic melanoma.",
    )
    path = tmp_path / "multi.txt"
    path.write_text(text, encoding="utf-8")
    paper = _paper(db_session, path)
    first_quote = "A 67-year-old man was diagnosed with metastatic melanoma."
    second_quote = "A 54-year-old woman was also diagnosed with metastatic melanoma."
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            _detection_yes(first_quote),
            {
                "cases": [
                    _empty_case("patient-1", first_quote),
                    _empty_case("patient-2", second_quote),
                ]
            },
            {"events": []},
            {"events": []},
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)

    assert run.status == ExtractionStatus.COMPLETED
    assert len(paper.cases) == 2


def test_no_case_paper_creates_no_case(db_session):
    paper = _paper(db_session, FIXTURES / "melanoma_case.txt")
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            {"existence": "NO", "confidence": 0.99, "evidence_refs": []},
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)

    assert run.status == ExtractionStatus.COMPLETED
    assert paper.cases == []


def test_invalid_json_is_retried():
    provider = FakeLLMProvider(
        [
            "not json",
            {"existence": "NO", "confidence": 0.9, "evidence_refs": []},
        ],
        max_retries=1,
    )
    result = provider.extract_structured(
        "No patient case is described.",
        CaseDetectionResult,
        "Return only supported information.",
    )
    assert result.retry_count == 1
    assert len(provider.calls) == 2
    assert "Repair the previous response" in provider.calls[1]["user_prompt"]


def test_invalid_json_stops_after_retry_limit():
    provider = FakeLLMProvider(["bad", "still bad"], max_retries=1)
    with pytest.raises(StructuredExtractionError) as exc_info:
        provider.extract_structured("text", CaseDetectionResult, "system")
    assert exc_info.value.retry_count == 1


def test_pipeline_records_failed_audit_after_retry_limit(db_session):
    paper = _paper(db_session, FIXTURES / "melanoma_case.txt")
    provider = FakeLLMProvider(["bad", "still bad"], max_retries=1)

    with pytest.raises(StructuredExtractionError):
        ExtractionPipeline(provider).run(db_session, paper.id)

    run = paper.extraction_runs[0]
    assert run.status == ExtractionStatus.FAILED
    assert run.retry_count == 1
    assert run.error
    assert paper.analysis_status == AnalysisStatus.FAILED


def test_not_reported_and_no_change_are_distinct_observation_states():
    not_reported = BiologicalObservationCandidate(
        category="immune",
        variable_name="CD8_T_cell",
        status="NOT_REPORTED",
    )
    assert not_reported.status.value == "NOT_REPORTED"

    with pytest.raises(ValueError):
        BiologicalObservationCandidate(
            category="immune",
            variable_name="CD8_T_cell",
            status="NO_CHANGE",
        )


def test_discussion_explanation_is_author_interpretation():
    pages = read_page_text(FIXTURES / "melanoma_case.txt")
    chunks = chunk_pages(1, pages)
    verifier = EvidenceVerifier(pages, chunks)
    result = verifier.verify(
        EvidenceReference(
            page=3,
            quote=(
                "The authors suggest that biopsy-induced inflammation may have "
                "contributed to regression."
            ),
            section="Discussion",
            evidence_type="OBSERVED_FACT",
        )
    )
    assert result.verified is True
    assert result.evidence_type.value == "AUTHOR_INTERPRETATION"


def test_discussion_documented_observation_can_be_observed_fact():
    quote = "The pulmonary lesion decreased from 25 mm to 8 mm."
    chunks = [
        TextChunk(
            paper_id=1,
            page_start=3,
            page_end=3,
            section="Discussion",
            chunk_index=0,
            text=quote,
        )
    ]
    result = EvidenceVerifier({3: quote}, chunks).verify(
        EvidenceReference(
            page=3,
            quote=quote,
            section="Discussion",
            evidence_type="AUTHOR_INTERPRETATION",
        )
    )
    assert result.verified is True
    assert result.evidence_type.value == "OBSERVED_FACT"


def test_standalone_likely_language_is_author_interpretation():
    quote = "This immune response likely contributed to tumor regression."
    chunks = [TextChunk(1, 3, 3, "Discussion", 0, quote)]
    result = EvidenceVerifier({3: quote}, chunks).verify(
        EvidenceReference(
            page=3,
            quote=quote,
            section="Discussion",
            evidence_type="OBSERVED_FACT",
        )
    )
    assert result.evidence_type.value == "AUTHOR_INTERPRETATION"


def test_surgery_cannot_be_a_treatment_status():
    payload = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    payload["treatment_status"]["value"] = "surgery at month 8"
    with pytest.raises(ValidationError):
        CaseCandidate.model_validate(payload)


def test_reported_absent_primary_and_split_regression_extent(db_session, tmp_path):
    source = (FIXTURES / "melanoma_case.txt").read_text(encoding="utf-8")
    source = source.replace(
        "A 67-year-old man was diagnosed with metastatic melanoma.",
        "A 67-year-old man was diagnosed with metastatic melanoma.\n"
        "No cutaneous primary melanoma was identified.\n"
        "Histopathology showed no viable tumor cells.",
    )
    source_path = tmp_path / "adjudicated.txt"
    source_path.write_text(source, encoding="utf-8")
    candidate = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    candidate["primary_site"] = {
        "value": None,
        "status": "REPORTED_ABSENT",
        "evidence_refs": [
            {
                "page": 2,
                "quote": "No cutaneous primary melanoma was identified.",
                "section": "Case Presentation",
                "evidence_type": "OBSERVED_FACT",
            }
        ],
    }
    pathology_ref = {
        "page": 2,
        "quote": "Histopathology showed no viable tumor cells.",
        "section": "Case Presentation",
        "evidence_type": "OBSERVED_FACT",
    }
    candidate["regression_extent_clinical"] = {
        "value": "UNCERTAIN",
        "status": "UNCERTAIN",
        "evidence_refs": [pathology_ref],
    }
    candidate["viable_tumor_at_pathology"] = {
        "value": "ABSENT",
        "status": "REPORTED",
        "evidence_refs": [pathology_ref],
    }
    paper = _paper(db_session, source_path)
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            _detection_yes(),
            {"cases": [candidate]},
            {"events": []},
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)
    case = paper.cases[0]

    assert run.schema_version == "phase2.3"
    assert case.primary_site is None
    assert case.primary_site_status == "REPORTED_ABSENT"
    assert case.field_statuses["primary_site"]["status"] == "REPORTED_ABSENT"
    assert case.regression_extent_clinical == "UNCERTAIN"
    assert case.viable_tumor_at_pathology == "ABSENT"


def test_duplicate_regression_observations_merge_into_one_event(
    db_session, tmp_path
):
    source_path = tmp_path / "duplicate.txt"
    source_path.write_text(
        "=== PAGE 1 ===\nCase Presentation\n"
        "A 67-year-old man was diagnosed with metastatic melanoma.\n"
        "The lesion SUV decreased to 0.9 at 6 months.\n"
        "=== PAGE 2 ===\nDiscussion\n"
        "At six months, the pulmonary lesion showed reduced FDG uptake with SUV 0.9.\n",
        encoding="utf-8",
    )
    quote = "A 67-year-old man was diagnosed with metastatic melanoma."
    paper = _paper(db_session, source_path)
    timeline = {
        "events": [
            {
                "event_type": "tumor_regression",
                "description": "The lesion SUV decreased to 0.9 at 6 months.",
                "event_date": None,
                "relative_time": "at 6 months",
                "date_precision": "RELATIVE",
                "relation_to_regression": "DURING",
                "temporal_order_confidence": 0.9,
                "evidence_refs": [
                    {
                        "page": 1,
                        "quote": "The lesion SUV decreased to 0.9 at 6 months.",
                    }
                ],
            },
            {
                "event_type": "tumor_regression",
                "description": (
                    "At six months, pulmonary lesion FDG uptake was reduced "
                    "to SUV 0.9."
                ),
                "event_date": None,
                "relative_time": "At six months",
                "date_precision": "RELATIVE",
                "relation_to_regression": "DURING",
                "temporal_order_confidence": 0.9,
                "evidence_refs": [
                    {
                        "page": 2,
                        "quote": (
                            "At six months, the pulmonary lesion showed reduced "
                            "FDG uptake with SUV 0.9."
                        ),
                    }
                ],
            },
        ]
    }
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            _detection_yes(quote),
            {"cases": [_empty_case("patient-1", quote)]},
            timeline,
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)

    events = db_session.query(Event).filter_by(extraction_run_id=run.id).all()
    evidence_ids = {
        link.evidence_id
        for link in db_session.query(FieldEvidenceLink)
        .filter_by(
            extraction_run_id=run.id,
            entity_type="event",
            entity_id=events[0].id,
        )
        .all()
    }
    assert len(events) == 1
    assert len(evidence_ids) == 2
    assert len(run.result_json["event_canonicalization"]) == 1


def test_regression_duration_does_not_populate_start_date():
    candidate = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    candidate["regression_start_date"] = _not_reported()
    candidate["regression_duration"] = {
        "value": "throughout 19 months after initial diagnosis",
        "status": "REPORTED",
        "evidence_refs": [
            {
                "page": 3,
                "quote": (
                    "The lesion continued to decrease throughout 19 months "
                    "after initial diagnosis."
                ),
            }
        ],
    }
    parsed = CaseCandidate.model_validate(candidate)
    assert parsed.regression_start_date.status.value == "NOT_REPORTED"
    assert parsed.regression_duration.value.startswith("throughout 19 months")


def test_sequence_phrase_is_not_a_regression_start_date():
    candidate = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    candidate["regression_start_date"] = {
        "value": "following biopsy",
        "status": "REPORTED",
        "evidence_refs": [
            {
                "page": 1,
                "quote": (
                    "Spontaneous regression of a metastatic melanoma pulmonary "
                    "deposit following biopsy."
                ),
            }
        ],
    }
    with pytest.raises(ValidationError, match="explicit onset"):
        CaseCandidate.model_validate(candidate)


def test_no_viable_cells_without_clinical_extent_becomes_uncertain():
    candidate = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    pathology_ref = {
        "page": 2,
        "quote": "Histopathology showed no viable tumor cells.",
    }
    candidate["regression_extent_clinical"] = _not_reported()
    candidate["viable_tumor_at_pathology"] = {
        "value": "ABSENT",
        "status": "REPORTED",
        "evidence_refs": [pathology_ref],
    }
    parsed = CaseCandidate.model_validate(candidate)
    assert parsed.regression_extent_clinical.status.value == "UNCERTAIN"
    assert parsed.regression_extent_clinical.value.value == "UNCERTAIN"


def test_pathology_absence_alone_cannot_mean_complete_clinical_regression():
    candidate = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    pathology_ref = {
        "page": 2,
        "quote": "Histopathology showed no viable tumor cells.",
    }
    candidate["regression_extent_clinical"] = {
        "value": "COMPLETE",
        "status": "REPORTED",
        "evidence_refs": [pathology_ref],
    }
    candidate["viable_tumor_at_pathology"] = {
        "value": "ABSENT",
        "status": "REPORTED",
        "evidence_refs": [pathology_ref],
    }
    with pytest.raises(ValidationError, match="explicit clinical extent"):
        CaseCandidate.model_validate(candidate)


def test_noncontiguous_ellipsis_quote_is_rejected():
    source = "Sentence A reports a biopsy. Sentence B reports regression."
    chunks = [
        TextChunk(1, 1, 1, "Case Report", 0, source),
    ]
    result = EvidenceVerifier({1: source}, chunks).verify(
        EvidenceReference(
            page=1,
            quote="Sentence A reports a biopsy... Sentence B reports regression.",
        )
    )
    assert result.verified is False
    assert "contiguous" in result.reason


def test_uncertain_temporal_relation_does_not_create_calendar_date():
    event = TimelineEventCandidate(
        event_type="treatment",
        description="The patient previously received ipilimumab.",
        event_date=None,
        relative_time="years earlier",
        date_precision="RELATIVE",
        relation_to_regression="UNKNOWN",
        temporal_order_confidence=0.3,
        evidence_refs=[
            {
                "page": 2,
                "quote": "The patient previously received ipilimumab.",
            }
        ],
    )
    assert event.event_date is None
    assert event.relative_time == "years earlier"


def test_textual_approximate_time_is_compatible_with_legacy_database(db_session):
    expected_case = json.loads(
        (FIXTURES / "melanoma_case_expected.json").read_text(encoding="utf-8")
    )
    paper = _paper(db_session, FIXTURES / "melanoma_case.txt")
    provider = FakeLLMProvider(
        [
            _metadata_response(),
            _detection_yes(),
            {"cases": [expected_case]},
            {
                "events": [
                    {
                        "event_type": "other",
                        "description": (
                            "At 12 months, he remained free of recurrence."
                        ),
                        "event_date": None,
                        "relative_time": "At 12 months",
                        "date_precision": "APPROXIMATE",
                        "relation_to_regression": "AFTER",
                        "temporal_order_confidence": 0.9,
                        "evidence_refs": [
                            {
                                "page": 2,
                                "quote": (
                                    "At 12 months, he remained free of recurrence."
                                ),
                                "section": "Case Presentation",
                                "evidence_type": "OBSERVED_FACT",
                            }
                        ],
                    }
                ]
            },
        ]
    )

    run = ExtractionPipeline(provider).run(db_session, paper.id)

    event = paper.cases[0].events[0]
    assert run.status == ExtractionStatus.COMPLETED
    assert event.date_precision.value == "unknown"
    assert event.source_date_precision == "APPROXIMATE"
    assert event.relative_time == "At 12 months"


def test_pdf_line_wrap_hyphenation_is_normalized():
    assert normalize_text("com-\npletely infarcted") == normalize_text(
        "completely infarcted"
    )
    assert normalize_text("Post-\noperative CT") == normalize_text(
        "Post-operative CT"
    )
    assert normalize_text("com- pletely necrotic") == normalize_text(
        "completely necrotic"
    )
