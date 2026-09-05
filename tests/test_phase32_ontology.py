from pathlib import Path

from app.llm.fake import FakeLLMProvider
from app.models import (
    BiologicalObservation,
    ExplanatoryAlternative,
    GenotypeObservation,
    GenotypeState,
    Lesion,
    LesionAlias,
    LesionAliasStatus,
    LesionCollection,
)
from app.schemas.extraction import BiologicalObservationCandidate
from app.services.biological_observation_pipeline import (
    BiologicalObservationPipeline,
)
from app.services.evidence_verifier import classify_claim
from app.services.lesion_identity import merge_decision, parse_lesion_text
from app.services.temporal_semantics import parse_temporal
from tests.test_phase3_biological_observations import (
    SOURCE_TEXT,
    _reference,
    _setup_case,
    _suv_observation,
)


def test_biopsy_fibrosis_is_pathologic_not_morphologic():
    candidate = BiologicalObservationCandidate(
        category="PATHOLOGIC",
        observation_domain="DIAGNOSTIC_EVIDENCE",
        measurement_semantics="MORPHOLOGIC_FINDING",
        variable_name="left axillary nodule biopsy",
        value="fibrosis, no disease",
        direction="ABSENT",
        status="REPORTED_ABSENT",
        scope_type="LESION",
        lesion_identifier="left axillary nodule",
        evidence_refs=[_reference("Biopsy of the left axillary nodule showed fibrosis, no disease.")],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.measurement_semantics.value == "PATHOLOGIC_FINDING"


def test_static_size_range_does_not_become_decreased():
    candidate = BiologicalObservationCandidate(
        category="OTHER",
        observation_domain="DISEASE_PHENOTYPE",
        measurement_semantics="MORPHOLOGIC_FINDING",
        variable_name="upper right thigh in-transit metastasis morphology and size",
        value="erythematous lesions ranged in size from 1 mm to 10 mm",
        direction="DECREASED",
        status="REPORTED",
        scope_type="LESION",
        lesion_identifier="upper right thigh in-transit metastases",
        regression_role="UNKNOWN",
        evidence_refs=[
            _reference(
                "The erythematous lesions ranged in size from 1 mm to 10 mm."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.direction.value == "UNKNOWN"


def test_explicit_size_change_remains_decreased():
    candidate = BiologicalObservationCandidate(
        category="OTHER",
        observation_domain="DISEASE_PHENOTYPE",
        measurement_semantics="MORPHOLOGIC_FINDING",
        variable_name="target lesion size",
        value="decreased from 15 mm to 8 mm",
        direction="DECREASED",
        status="REPORTED",
        scope_type="LESION",
        lesion_identifier="left lower lobe biopsied lesion",
        regression_role="REGRESSING_TARGET",
        evidence_refs=[_reference("The lesion decreased from 15 mm to 8 mm.")],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.direction.value == "DECREASED"


def test_lesion_aliases_merge_same_biopsied_left_lung_lesion():
    first = parse_lesion_text("left lower lobe nodule")
    second = parse_lesion_text("previously biopsied left lung nodule")
    assert first is not None and second is not None
    assert merge_decision(first, second) == "CONFIRMED_ALIAS"


def test_possible_same_lesion_is_not_forced_merge():
    first = parse_lesion_text("left axillary nodule")
    second = parse_lesion_text("left axillary lymph node")
    assert first is not None and second is not None
    assert merge_decision(first, second) == "POSSIBLE_SAME_LESION"


def test_multifocal_collection_is_not_a_single_lesion():
    parsed = parse_lesion_text("bilateral upper-lobe lesions")
    assert parsed is not None
    assert parsed.is_collection is True


def test_relative_temporal_text_is_preserved():
    parsed = parse_temporal("approximately 2 years later")
    assert parsed is not None
    assert parsed.temporal_precision.value in {
        "APPROXIMATE_DATE",
        "RELATIVE_TIME",
    }
    assert parsed.temporal_unit == "year"
    assert parsed.calendar_date is None


def test_at_n_months_is_relative_time():
    parsed = parse_temporal("at 6 months")
    assert parsed is not None
    assert parsed.temporal_precision.value == "RELATIVE_TIME"
    assert parsed.temporal_value == 6
    assert parsed.temporal_unit == "month"
    assert parsed.calendar_date is None


def test_interval_temporal_text_is_preserved():
    parsed = parse_temporal("during the following 19 months")
    assert parsed is not None
    assert parsed.temporal_precision.value == "INTERVAL"
    assert parsed.temporal_value == 19
    assert parsed.temporal_unit == "month"


def test_cd8_infiltration_is_dual_domain_biological_state():
    candidate = BiologicalObservationCandidate(
        category="IMMUNE",
        observation_domain="DIAGNOSTIC_EVIDENCE",
        measurement_semantics="PATHOLOGIC_FINDING",
        variable_name="CD3+ and CD8+ T-cell infiltration",
        value="brisk infiltration",
        direction="PRESENT",
        status="REPORTED",
        scope_type="LESION",
        lesion_identifier="February 2014 resected in-transit metastasis",
        regression_role="UNKNOWN",
        evidence_refs=[
            _reference(
                "Dual immunohistochemical staining demonstrated brisk "
                "infiltration with CD3+ and CD8+ T cells."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.observation_domain.value == "BIOLOGICAL_STATE"
    assert candidate.domain_secondary.value == "DIAGNOSTIC_EVIDENCE"
    assert candidate.measurement_semantics.value == "PATHOLOGIC_FINDING"
    assert candidate.category.value == "IMMUNE"


def test_braf_wild_type_is_not_absent():
    candidate = BiologicalObservationCandidate(
        category="GENETIC",
        observation_domain="DIAGNOSTIC_EVIDENCE",
        measurement_semantics="PATHOLOGIC_FINDING",
        variable_name="BRAFV600 status",
        value="wild-type",
        direction="ABSENT",
        status="REPORTED",
        evidence_refs=[_reference("The melanoma was BRAF wild-type.")],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.status.value == "REPORTED"
    assert candidate.direction.value == "UNKNOWN"
    assert candidate.normalized_value == "WILD_TYPE"


def test_mutation_not_detected_is_not_wild_type():
    candidate = BiologicalObservationCandidate(
        category="GENETIC",
        observation_domain="DIAGNOSTIC_EVIDENCE",
        measurement_semantics="PATHOLOGIC_FINDING",
        variable_name="BRAF mutation",
        value="not detected",
        direction="ABSENT",
        status="REPORTED_ABSENT",
        evidence_refs=[_reference("BRAF mutation not detected.")],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.normalized_value == "NOT_DETECTED"
    assert candidate.normalized_value != "WILD_TYPE"
    assert candidate.direction.value == "UNKNOWN"


def test_spontaneous_regression_is_disease_phenotype_not_treatment_response():
    candidate = BiologicalObservationCandidate(
        category="OTHER",
        observation_domain="TREATMENT_RESPONSE",
        measurement_semantics="CLINICAL_FINDING",
        variable_name="in-transit metastases",
        value="all in transit metastases had resolved both clinically and radiographically",
        direction="ABSENT",
        status="REPORTED_ABSENT",
        scope_type="LESION",
        lesion_identifier="all right lower-extremity in-transit metastases",
        regression_role="REGRESSING_TARGET",
        evidence_refs=[
            _reference(
                "By August 2016, all in transit metastases had resolved both "
                "clinically and radiographically."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.observation_domain.value == "DISEASE_PHENOTYPE"


def test_named_treatment_response_remains_treatment_response():
    candidate = BiologicalObservationCandidate(
        category="OTHER",
        observation_domain="DISEASE_PHENOTYPE",
        measurement_semantics="CLINICAL_FINDING",
        variable_name="Response of thigh lesions to palliative radiotherapy",
        value="good response",
        direction="DECREASED",
        status="REPORTED",
        scope_type="LESION",
        lesion_identifier="upper right thigh in-transit metastases",
        regression_role="UNKNOWN",
        evidence_refs=[
            _reference(
                "Palliative radiotherapy was delivered to the thigh nodules "
                "with good response."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.observation_domain.value == "TREATMENT_RESPONSE"


def test_direct_size_reduction_is_not_author_interpretation():
    from app.schemas.extraction import SourceEvidenceType

    evidence_type = classify_claim(
        "radiographically, in May 2015 there was a continued mixed response "
        "with most lesions reduced in size.",
        SourceEvidenceType.AUTHOR_INTERPRETATION,
    )
    assert evidence_type.value == "OBSERVED_FACT"


def test_mechanistic_belief_remains_interpretation():
    from app.schemas.extraction import SourceEvidenceType

    evidence_type = classify_claim(
        "We believe these lymphocytes mediated regression.",
        SourceEvidenceType.OBSERVED_FACT,
    )
    assert evidence_type.value == "AUTHOR_INTERPRETATION"


def test_pipeline_persists_genotype_lesion_and_explanatory_alternative(
    db_session, tmp_path: Path
):
    case, source_run, _ = _setup_case(db_session, tmp_path)
    source = Path(case.paper.extracted_text_path)
    source.write_text(
        SOURCE_TEXT.replace(
            "A patient with metastatic melanoma was observed.",
            "A patient with metastatic melanoma was observed.\n"
            "The melanoma was BRAF wild-type.\n"
            "CD8-positive lymphocytes were present.",
        ).replace(
            "We believe immune activation caused the regression.",
            "We believe immune activation caused the regression.\n"
            "It is intriguing to speculate that ipilimumab two years prior contributed.",
        ),
        encoding="utf-8",
    )
    genotype = {
        "category": "GENETIC",
        "observation_domain": "DIAGNOSTIC_EVIDENCE",
        "variable_name": "BRAFV600 status",
        "value": "wild-type",
        "direction": "ABSENT",
        "status": "REPORTED",
        "scope_type": "PATIENT",
        "confidence": 0.9,
        "evidence_refs": [_reference("The melanoma was BRAF wild-type.")],
    }
    immune = {
        "category": "IMMUNE",
        "observation_domain": "DIAGNOSTIC_EVIDENCE",
        "measurement_semantics": "PATHOLOGIC_FINDING",
        "variable_name": "CD8-positive lymphocytes",
        "value": "were present",
        "direction": "PRESENT",
        "status": "REPORTED",
        "scope_type": "LESION",
        "lesion_identifier": "left lower lobe nodule",
        "regression_role": "REGRESSING_TARGET",
        "confidence": 0.9,
        "evidence_refs": [_reference("CD8-positive lymphocytes were present.")],
    }
    alias = {
        **immune,
        "variable_name": "CD8 infiltration in biopsied left lung nodule",
        "lesion_identifier": "previously biopsied left lung nodule",
        "evidence_refs": [_reference("CD8-positive lymphocytes were present.")],
    }
    provider = FakeLLMProvider(
        [
            {
                "observations": [genotype, immune, alias],
                "rejected_interpretations": [
                    {
                        "statement": (
                            "It is intriguing to speculate that ipilimumab "
                            "two years prior contributed."
                        ),
                        "rejection_reason": "Delayed treatment effect is not a fact.",
                        "confidence": 0.8,
                        "evidence_refs": [
                            {
                                "page": 2,
                                "quote": (
                                    "It is intriguing to speculate that "
                                    "ipilimumab two years prior contributed."
                                ),
                                "section": "Discussion",
                                "evidence_type": "AUTHOR_INTERPRETATION",
                            }
                        ],
                    }
                ],
            }
        ]
    )

    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    genotypes = (
        db_session.query(GenotypeObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert len(genotypes) == 1
    assert genotypes[0].gene == "BRAF"
    assert genotypes[0].state == GenotypeState.WILD_TYPE
    lesions = (
        db_session.query(Lesion).filter_by(created_from_run_id=run.id).all()
    )
    assert len(lesions) == 1
    aliases = (
        db_session.query(LesionAlias)
        .filter(LesionAlias.lesion_id == lesions[0].id)
        .all()
    )
    assert len(aliases) >= 2
    assert any(row.status == LesionAliasStatus.CONFIRMED_ALIAS for row in aliases)
    alternatives = (
        db_session.query(ExplanatoryAlternative)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert len(alternatives) == 1
    assert alternatives[0].alternative_type == "delayed_immunotherapy_effect"
    immune_obs = (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id, category="IMMUNE")
        .all()
    )
    assert immune_obs
    assert all(
        row.observation_domain == "BIOLOGICAL_STATE"
        and row.domain_secondary == "DIAGNOSTIC_EVIDENCE"
        for row in immune_obs
    )


def test_infection_event_creates_clinical_context(db_session, tmp_path: Path):
    from app.models import (
        Event,
        EventType,
        Evidence,
        EvidenceType,
        FieldEvidenceLink,
        SupportType,
    )

    case, source_run, _ = _setup_case(db_session, tmp_path)
    event = Event(
        case_id=case.id,
        extraction_run_id=source_run.id,
        event_type=EventType.INFECTION,
        description="The patient had wound dehiscence and recurring infections.",
        relation_to_regression="BEFORE",
    )
    db_session.add(event)
    db_session.flush()
    evidence = Evidence(
        paper_id=case.paper_id,
        case_id=case.id,
        evidence_type=EvidenceType.OBSERVED_FACT,
        claim="event.description: infection",
        source_quote="The patient had wound dehiscence and recurring infections.",
        page=1,
        section="Case Report",
        confidence=0.9,
        support_type=SupportType.NEUTRAL,
    )
    db_session.add(evidence)
    db_session.flush()
    db_session.add(
        FieldEvidenceLink(
            extraction_run_id=source_run.id,
            entity_type="event",
            entity_id=event.id,
            field_name="description",
            evidence_id=evidence.id,
        )
    )
    db_session.commit()
    provider = FakeLLMProvider(
        [{"observations": [_suv_observation()], "rejected_interpretations": []}]
    )
    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    contexts = (
        db_session.query(BiologicalObservation)
        .filter_by(
            created_from_run_id=run.id,
            observation_domain="CLINICAL_CONTEXT",
        )
        .all()
    )
    assert contexts
    assert any("infection" in (row.variable_name or "") for row in contexts)


def test_collection_does_not_create_single_lesion(db_session, tmp_path: Path):
    case, source_run, _ = _setup_case(db_session, tmp_path)
    payload = {
        "category": "OTHER",
        "observation_domain": "DISEASE_PHENOTYPE",
        "measurement_semantics": "MORPHOLOGIC_FINDING",
        "variable_name": "bilateral upper-lobe lesions",
        "value": "increased in size and number",
        "direction": "INCREASED",
        "status": "REPORTED",
        "scope_type": "LESION",
        "lesion_identifier": "bilateral upper-lobe lesions",
        "regression_role": "PROGRESSING_NON_TARGET",
        "confidence": 0.9,
        "evidence_refs": [
            _reference(
                "The bilateral upper-lobe lesions were markedly "
                "hypermetabolic with SUV 15.2."
            )
        ],
    }
    provider = FakeLLMProvider(
        [{"observations": [payload], "rejected_interpretations": []}]
    )
    run = BiologicalObservationPipeline(provider).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    assert db_session.query(Lesion).filter_by(created_from_run_id=run.id).count() == 0
    collections = (
        db_session.query(LesionCollection)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert len(collections) == 1
