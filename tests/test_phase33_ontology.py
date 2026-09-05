from app.models import (
    CaseScopeStatus,
    GenotypeOrigin,
    GenotypeState,
    ObservationCategory,
    ObservationDomain,
)
from app.schemas.extraction import BiologicalObservationCandidate, SourceEvidenceType
from app.services.biological_observation_pipeline import BiologicalObservationPipeline
from app.services.case_scope import classify_sentence, other_patient_quote
from app.services.evidence_verifier import (
    EvidenceVerifier,
    exact_normalize,
    normalize_text,
)
from app.services.genotype_semantics import parse_genotype
from app.services.lesion_identity import parse_lesion_text
from app.services.pathology_split import split_pathology_observations
from app.services.regression_episodes import build_regression_episodes
from tests.test_phase3_biological_observations import _reference


def test_braf_v600e_wild_type_is_not_mutated():
    parsed = parse_genotype("BRAF V600E mutation status", "wild type")
    assert parsed is not None
    assert parsed.gene == "BRAF"
    assert parsed.variant == "V600E"
    assert parsed.state == GenotypeState.WILD_TYPE.value
    assert parsed.state != GenotypeState.MUTATED.value


def test_mefv_germline_variant_is_variant_present():
    parsed = parse_genotype(
        "germline pyrin variant MEFV P369S/R408Q",
        "rs11466023",
    )
    assert parsed is not None
    assert parsed.gene == "MEFV"
    assert parsed.protein_change == "P369S/R408Q"
    assert parsed.origin == GenotypeOrigin.GERMLINE.value
    assert parsed.state == GenotypeState.VARIANT_PRESENT.value
    assert parsed.rs_id == "rs11466023"


def test_cytogenetic_deletion_is_representable():
    parsed = parse_genotype("bone marrow karyotype", "del(5q)")
    assert parsed is not None
    assert parsed.gene == "del(5q)"
    assert parsed.variant_type == "CYTOGENETIC"


def test_harden_wild_type_with_space_is_not_absent():
    candidate = BiologicalObservationCandidate(
        category="GENETIC",
        observation_domain="DIAGNOSTIC_EVIDENCE",
        variable_name="BRAF V600E mutation status",
        value="wild type",
        direction="ABSENT",
        status="REPORTED",
        evidence_refs=[_reference("Molecular testing for the BRAF V600E mutation yielded wild type.")],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.normalized_value == "WILD_TYPE"
    assert candidate.direction.value == "UNKNOWN"


def test_leukoderma_is_not_regression_or_viability():
    candidate = BiologicalObservationCandidate(
        category="PATHOLOGIC",
        observation_domain="DISEASE_PHENOTYPE",
        measurement_semantics="PATHOLOGIC_FINDING",
        variable_name="complete regression with leukoderma",
        value="complete regression and a patch of leukoderma",
        direction="ABSENT",
        status="REPORTED",
        scope_type="LESION",
        lesion_identifier="medial right ankle leukoderma patch",
        regression_role="UNKNOWN",
        evidence_refs=[
            _reference(
                "Further examination revealed a patch of leukoderma on the medial aspect of her right ankle."
            )
        ],
    )
    BiologicalObservationPipeline._harden_ontology(candidate)
    assert candidate.category == ObservationCategory.DERMATOLOGIC_PHENOTYPE
    assert candidate.observation_domain == ObservationDomain.CLINICAL_CONTEXT
    assert candidate.measurement_semantics.value == "CLINICAL_FINDING"


def test_pathology_sentence_is_split():
    candidate = BiologicalObservationCandidate(
        category="PATHOLOGIC",
        observation_domain="DIAGNOSTIC_EVIDENCE",
        measurement_semantics="PATHOLOGIC_FINDING",
        variable_name="heel biopsy",
        value="fibrosis, melanophages, and absence of neoplastic cells",
        direction="MIXED",
        status="REPORTED",
        scope_type="LESION",
        lesion_identifier="right heel nodule",
        evidence_refs=[
            _reference(
                "These findings were consistent with complete regression with "
                "absence of neoplastic cells replaced by fibrosis and melanophages."
            )
        ],
    )
    rows = split_pathology_observations([candidate])
    names = {row.variable_name for row in rows}
    assert "fibrosis" in names
    assert "melanophages" in names
    assert "viable malignant cells" in names
    assert len(rows) >= 3


def test_canonical_name_is_not_generic_skin_lesion():
    parsed = parse_lesion_text("right heel primary melanoma lesion")
    assert parsed is not None
    assert "heel" in parsed.canonical_name
    assert parsed.canonical_name not in {"right lesion", "skin lesion"}


def test_lymph_node_name_is_not_duplicated():
    parsed = parse_lesion_text("right inguinal lymph node metastasis")
    assert parsed is not None
    assert "lymph node lymph node" not in parsed.canonical_name
    assert "inguinal" in parsed.canonical_name


def test_quote_hyphen_join_is_verified_normalized():
    pages = {1: "positron emission tomography-\ncomputed tomography showed uptake."}
    verifier = EvidenceVerifier(pages, [])
    verified = verifier.verify(
        type(
            "Ref",
            (),
            {
                "quote": "positron emission tomography-computed tomography showed uptake.",
                "page": 1,
                "section": "Case Report",
                "evidence_type": SourceEvidenceType.OBSERVED_FACT,
            },
        )()
    )
    assert verified.verified is True
    assert verified.verification_status.value in {
        "VERIFIED_EXACT",
        "VERIFIED_NORMALIZED",
    }


def test_exact_and_normalized_quotes_are_both_kept():
    raw = "wild-type"
    assert "wild" in exact_normalize(raw)
    assert "type" in normalize_text(raw)


def test_synthetic_case_id_does_not_activate_scope():
    class _Case:
        patient_identifier = "paper-2-case-1 [run 58]"
        age = None
        sex = None

    from app.services.case_scope import case_markers

    assert case_markers(_Case()) == set()


def test_other_patient_quote_is_rejected():
    class _Case:
        patient_identifier = "Patient A"
        age = 71
        sex = "male"

    assert other_patient_quote(
        "Patient B presented with unexplained right axillary lymphadenopathy.",
        _Case(),
    )
    assert classify_sentence(
        "Both patients presented with isolated lymphadenopathy.",
        {"a"},
    ).value == CaseScopeStatus.SHARED_BOTH.value


def test_regression_episodes_split_by_organ():
    from app.models import Event, EventType

    events = [
        Event(
            case_id=1,
            event_type=EventType.TUMOR_REGRESSION,
            description="Pathologic spontaneous regression of a left axillary lymph node.",
            relation_to_regression="DURING",
        ),
        Event(
            case_id=1,
            event_type=EventType.TUMOR_REGRESSION,
            description="Two of three hepatic lesions were smaller on October 2018 PET-CT.",
            relation_to_regression="DURING",
        ),
    ]
    drafts = build_regression_episodes(events)
    assert len(drafts) == 2
    organs = {draft.organ_key for draft in drafts}
    assert "AXILLA" in organs
    assert "LIVER" in organs
