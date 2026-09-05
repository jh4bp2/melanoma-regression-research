from pathlib import Path

from app.llm.fake import FakeLLMProvider
from app.models import (
    AnalysisStatus,
    BiologicalObservation,
    Case,
    Event,
    EventType,
    ExtractionRun,
    ExtractionStatus,
    FieldEvidenceLink,
    Paper,
    PaperType,
)
from app.schemas.extraction import BiologicalObservationCandidate
from app.services.biological_observation_pipeline import (
    BiologicalObservationPipeline,
)


SOURCE_TEXT = """=== PAGE 1 ===
Case Report
A patient with metastatic melanoma was observed.
The lesion SUV decreased from 3.4 to 0.9 during regression.
The tumor consisted entirely of necrotic cells with no viable melanoma cells.
No inflammatory infiltrate was observed.
The biopsied left lower lobe lesion showed minimal FDG uptake with SUV 2.5.
The bilateral upper-lobe lesions were markedly hypermetabolic with SUV 15.2.
=== PAGE 2 ===
Discussion
The lesion SUV decreased from 3.4 to 0.9 during regression.
We believe immune activation caused the regression.
"""


def _setup_case(db_session, tmp_path: Path):
    source_path = tmp_path / "phase3.txt"
    source_path.write_text(SOURCE_TEXT, encoding="utf-8")
    paper = Paper(
        title="PHASE 3 fixture",
        authors=[],
        full_text_path="phase3.pdf",
        extracted_text_path=str(source_path),
        paper_type=PaperType.CASE_REPORT,
        analysis_status=AnalysisStatus.EXTRACTED,
        content_sha256="c" * 64,
        page_count=2,
        raw_metadata={},
    )
    db_session.add(paper)
    db_session.flush()
    source_run = ExtractionRun(
        paper_id=paper.id,
        run_type="case_timeline",
        model="fake",
        prompt_version="fixture",
        status=ExtractionStatus.COMPLETED,
        retry_count=0,
    )
    db_session.add(source_run)
    db_session.flush()
    case = Case(
        paper_id=paper.id,
        patient_identifier="phase3-patient",
        extraction_run_id=source_run.id,
        field_statuses={},
    )
    db_session.add(case)
    db_session.flush()
    event = Event(
        case_id=case.id,
        extraction_run_id=source_run.id,
        event_type=EventType.TUMOR_REGRESSION,
        description="The lesion SUV decreased from 3.4 to 0.9.",
    )
    db_session.add(event)
    db_session.commit()
    return case, source_run, event


def _reference(quote: str, page: int = 1, section: str = "Case Report"):
    return {
        "page": page,
        "quote": quote,
        "section": section,
        "evidence_type": "OBSERVED_FACT",
    }


def _suv_observation(evidence_refs=None):
    return {
        "category": "METABOLIC",
        "variable_name": "lesion SUV",
        "normalized_variable": "SUV",
        "value": "3.4 to 0.9",
        "normalized_value": [3.4, 0.9],
        "unit": "SUV",
        "direction": "DECREASED",
        "status": "REPORTED",
        "time_relation": "DURING_REGRESSION",
        "temporal_precision": "RELATIVE",
        "observation_context": "serial metabolic imaging",
        "related_event_description": "The lesion SUV decreased from 3.4 to 0.9.",
        "confidence": 0.98,
        "evidence_refs": evidence_refs
        or [
            _reference(
                "The lesion SUV decreased from 3.4 to 0.9 during regression."
            )
        ],
    }


def test_explicit_numeric_temporal_observation_and_multiple_evidence(
    db_session, tmp_path
):
    case, source_run, event = _setup_case(db_session, tmp_path)
    payload = _suv_observation(
        [
            _reference(
                "The lesion SUV decreased from 3.4 to 0.9 during regression."
            ),
            _reference(
                "The lesion SUV decreased from 3.4 to 0.9 during regression.",
                page=2,
                section="Discussion",
            ),
        ]
    )
    payload["related_event_description"] = None
    provider = FakeLLMProvider(
        [{"observations": [payload], "rejected_interpretations": []}]
    )

    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )

    observations = (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert len(observations) == 1
    observation = observations[0]
    assert observation.value == "3.4 to 0.9"
    assert observation.normalized_value == [3.4, 0.9]
    assert observation.direction == "DECREASED"
    assert observation.time_relation == "DURING_REGRESSION"
    assert observation.linked_event_id == event.id
    evidence_ids = {
        link.evidence_id
        for link in db_session.query(FieldEvidenceLink)
        .filter_by(
            extraction_run_id=run.id,
            entity_type="biological_observation",
            entity_id=observation.id,
        )
    }
    assert len(evidence_ids) == 2
    assert run.result_json["metrics"]["verified_evidence"] == 2


def test_reported_absent_and_not_reported_are_distinct():
    absent = BiologicalObservationCandidate(
        category="PATHOLOGIC",
        variable_name="inflammatory infiltrate",
        normalized_variable="IMMUNE_INFILTRATION",
        direction="ABSENT",
        status="REPORTED_ABSENT",
        time_relation="AT_CONFIRMATION",
        temporal_precision="UNKNOWN",
        confidence=0.95,
        evidence_refs=[
            _reference("No inflammatory infiltrate was observed.")
        ],
    )
    missing = BiologicalObservationCandidate(
        category="IMMUNE",
        variable_name="CD8 T cells",
        normalized_variable="CD8_T_CELL",
        direction="UNKNOWN",
        status="NOT_REPORTED",
        time_relation="UNKNOWN",
        temporal_precision="UNKNOWN",
        confidence=1.0,
        evidence_refs=[],
    )
    assert absent.status.value == "REPORTED_ABSENT"
    assert missing.status.value == "NOT_REPORTED"


def test_duration_expression_cannot_be_exact_temporal_precision():
    candidate = BiologicalObservationCandidate(
        category="METABOLIC",
        variable_name="SUV",
        normalized_variable="SUV",
        value="reduced to 0.9 at 6 months",
        normalized_value=0.9,
        unit="SUV",
        direction="DECREASED",
        status="REPORTED",
        time_relation="DURING_REGRESSION",
        temporal_precision="EXACT",
        confidence=0.95,
        evidence_refs=[
            _reference("The lesion SUV was reduced to 0.9 at 6 months.")
        ],
    )
    assert candidate.temporal_precision.value == "RELATIVE"


def test_single_point_minimal_suv_and_normal_cbc_have_unknown_direction():
    minimal_suv = BiologicalObservationCandidate(
        category="METABOLIC",
        observation_domain="BIOLOGICAL_STATE",
        measurement_semantics="IMAGING_PROXY",
        variable_name="FDG uptake",
        normalized_variable="FDG_UPTAKE",
        value="minimal FDG uptake with SUV 2.5",
        normalized_value=2.5,
        unit="SUV",
        direction="DECREASED",
        status="REPORTED",
        time_relation="DURING_REGRESSION",
        temporal_precision="RELATIVE",
        scope_type="LESION",
        lesion_identifier="left lower lobe pulmonary nodule",
        regression_role="REGRESSING_TARGET",
        qualitative_level="MINIMAL",
        confidence=0.98,
        evidence_refs=[
            _reference(
                "The biopsied left lower lobe lesion showed minimal FDG "
                "uptake with SUV 2.5."
            )
        ],
    )
    normal_cbc = BiologicalObservationCandidate(
        category="OTHER",
        observation_domain="BIOLOGICAL_STATE",
        measurement_semantics="LAB_MEASUREMENT",
        variable_name="complete blood count",
        normalized_variable="COMPLETE_BLOOD_COUNT",
        value="NORMAL",
        direction="UNCHANGED",
        status="REPORTED",
        time_relation="BEFORE_REGRESSION",
        temporal_precision="UNKNOWN",
        scope_type="SYSTEMIC",
        regression_role="UNKNOWN",
        qualitative_level="NORMAL",
        confidence=0.95,
        evidence_refs=[_reference("While the complete blood count was normal")],
    )
    BiologicalObservationPipeline._harden_ontology(minimal_suv)
    BiologicalObservationPipeline._harden_ontology(normal_cbc)
    assert minimal_suv.direction.value == "UNKNOWN"
    assert minimal_suv.lesion_identifier == "left lower lobe biopsied lesion"
    assert normal_cbc.direction.value == "UNKNOWN"
    assert normal_cbc.scope_type.value == "SYSTEMIC"
    assert normal_cbc.normalized_value == "NORMAL"


def test_regressing_and_progressing_lesion_observations_do_not_merge(
    db_session, tmp_path
):
    case, source_run, _ = _setup_case(db_session, tmp_path)
    common = {
        "category": "METABOLIC",
        "observation_domain": "BIOLOGICAL_STATE",
        "measurement_semantics": "IMAGING_PROXY",
        "normalized_variable": "FDG_UPTAKE",
        "unit": "SUV",
        "direction": "DECREASED",
        "status": "REPORTED",
        "time_relation": "DURING_REGRESSION",
        "temporal_precision": "RELATIVE",
        "qualitative_level": "UNKNOWN",
        "observation_context": None,
        "related_event_description": None,
        "confidence": 0.97,
    }
    target = {
        **common,
        "variable_name": "FDG uptake in biopsied left lower lobe lesion",
        "value": "minimal FDG uptake with SUV 2.5",
        "normalized_value": 2.5,
        "scope_type": "LESION",
        "lesion_identifier": "left lower lobe biopsied lesion",
        "regression_role": "REGRESSING_TARGET",
        "qualitative_level": "MINIMAL",
        "evidence_refs": [
            _reference(
                "The biopsied left lower lobe lesion showed minimal FDG "
                "uptake with SUV 2.5."
            )
        ],
    }
    non_target = {
        **common,
        "variable_name": "FDG uptake in bilateral upper-lobe lesions",
        "value": "markedly hypermetabolic with SUV 15.2",
        "normalized_value": 15.2,
        "scope_type": "LESION",
        "lesion_identifier": "bilateral upper-lobe lesions",
        "regression_role": "PROGRESSING_NON_TARGET",
        "qualitative_level": "MARKED",
        "evidence_refs": [
            _reference(
                "The bilateral upper-lobe lesions were markedly "
                "hypermetabolic with SUV 15.2."
            )
        ],
    }
    provider = FakeLLMProvider(
        [
            {
                "observations": [target, non_target],
                "rejected_interpretations": [],
            }
        ]
    )

    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    observations = (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id)
        .order_by(BiologicalObservation.id)
        .all()
    )
    assert len(observations) == 2
    assert {row.lesion_identifier for row in observations} == {
        "left lower lobe biopsied lesion",
        "bilateral upper-lobe lesions",
    }
    assert {row.regression_role for row in observations} == {
        "REGRESSING_TARGET",
        "PROGRESSING_NON_TARGET",
    }
    assert all(row.observation_domain == "BIOLOGICAL_STATE" for row in observations)
    assert all(row.direction == "UNKNOWN" for row in observations)
    assert run.result_json["metrics"]["duplicate_merges"] == 0


def test_upper_lung_size_claim_is_non_target_disease_phenotype():
    candidate = BiologicalObservationCandidate(
        category="OTHER",
        observation_domain="BIOLOGICAL_STATE",
        measurement_semantics="IMAGING_PROXY",
        variable_name="bilateral upper-lung cavitary lesion size and number",
        normalized_variable="CAVITARY_LESION_SIZE_AND_NUMBER",
        value="increased in size and number",
        direction="INCREASED",
        status="REPORTED",
        time_relation="DURING_REGRESSION",
        temporal_precision="RELATIVE",
        scope_type="LESION",
        lesion_identifier="left lower lobe biopsied lesion",
        regression_role="PROGRESSING_NON_TARGET",
        confidence=0.98,
        evidence_refs=[
            _reference(
                "The bilateral upper-lung cavitary lesions increased in size "
                "and number."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.lesion_identifier == "bilateral upper-lobe lesions"
    assert candidate.regression_role.value == "PROGRESSING_NON_TARGET"
    assert candidate.measurement_semantics.value == "MORPHOLOGIC_FINDING"
    assert candidate.observation_domain.value == "DISEASE_PHENOTYPE"
    assert candidate.direction.value == "INCREASED"


def test_melanin_stain_remains_diagnostic_not_biological_state():
    candidate = BiologicalObservationCandidate(
        category="PATHOLOGIC",
        observation_domain="BIOLOGICAL_STATE",
        measurement_semantics="PATHOLOGIC_FINDING",
        variable_name="melanin pigment within necrotic cells",
        normalized_variable="MELANIN_PIGMENT",
        value="present by Mason Fontana stain",
        direction="PRESENT",
        status="REPORTED",
        time_relation="AT_CONFIRMATION",
        temporal_precision="RELATIVE",
        scope_type="LESION",
        lesion_identifier="left upper lobe target lesion",
        regression_role="REGRESSING_TARGET",
        confidence=0.98,
        evidence_refs=[
            _reference(
                "Mason Fontana stain showed melanin pigment within necrotic cells."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.observation_domain.value == "DIAGNOSTIC_EVIDENCE"


def test_author_hypothesis_and_mechanistic_speculation_are_not_stored(
    db_session, tmp_path
):
    case, source_run, _ = _setup_case(db_session, tmp_path)
    mechanistic_candidate = {
        "category": "IMMUNE",
        "variable_name": "immune activation",
        "normalized_variable": "IMMUNE_ACTIVATION",
        "value": "caused regression",
        "normalized_value": None,
        "unit": None,
        "direction": "INCREASED",
        "status": "REPORTED",
        "time_relation": "DURING_REGRESSION",
        "temporal_precision": "UNKNOWN",
        "observation_context": "proposed mechanism",
        "related_event_description": None,
        "confidence": 0.8,
        "evidence_refs": [
            _reference(
                "We believe immune activation caused the regression.",
                page=2,
                section="Discussion",
            )
        ],
    }
    provider = FakeLLMProvider(
        [
            {
                "observations": [mechanistic_candidate],
                "rejected_interpretations": [],
            }
        ]
    )

    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )

    assert (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id)
        .count()
        == 0
    )
    rejected = run.result_json["rejected_as_interpretation"]
    assert len(rejected) == 1
    assert "Mechanistic" in rejected[0]["reason"]


def test_duplicate_observations_merge_and_keep_both_sources(db_session, tmp_path):
    case, source_run, _ = _setup_case(db_session, tmp_path)
    first = _suv_observation()
    second = _suv_observation(
        [
            _reference(
                "The lesion SUV decreased from 3.4 to 0.9 during regression.",
                page=2,
                section="Discussion",
            )
        ]
    )
    provider = FakeLLMProvider(
        [
            {
                "observations": [first, second],
                "rejected_interpretations": [],
            }
        ]
    )

    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )

    observations = (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert len(observations) == 1
    assert len(run.result_json["duplicate_merges"]) == 1
    evidence_ids = {
        link.evidence_id
        for link in db_session.query(FieldEvidenceLink)
        .filter_by(
            extraction_run_id=run.id,
            entity_type="biological_observation",
            entity_id=observations[0].id,
        )
    }
    assert len(evidence_ids) == 2


def test_unverified_quote_is_rejected(db_session, tmp_path):
    case, source_run, _ = _setup_case(db_session, tmp_path)
    payload = _suv_observation(
        [_reference("The lesion SUV decreased from 10.0 to 0.1.")]
    )
    provider = FakeLLMProvider(
        [{"observations": [payload], "rejected_interpretations": []}]
    )

    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )

    assert run.status == ExtractionStatus.PARTIAL
    assert (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id)
        .count()
        == 0
    )
    assert len(run.result_json["verification_failures"]) == 1
