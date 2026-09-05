from app.corpus.inclusion_gate import (
    DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION,
    INCLUDED_SPONTANEOUS_REGRESSION,
    RETROSPECTIVELY_SUPPORTED_REGRESSION,
    TREATMENT_ASSOCIATED_REFERENCE,
    TREATMENT_ASSOCIATED_REGRESSION,
    biopsy_is_not_causal_fact,
    classify_inclusion,
    fever_or_infection_is_not_causal_fact,
    has_treatment_associated_regression,
)
from app.corpus.polarity import PolarityDecision, check_claim_against_quote
from app.corpus.versions import CORPUS_INFRA_VERSION, CORPUS_RULE_VERSION, frozen_ontology
from app.corpus.states import ExclusionReason


def test_batch5_keeps_frozen_ontology():
    frozen = frozen_ontology()
    assert frozen["corpus_infra_version"] == "phase4a.2"
    assert frozen["corpus_rule_version"] == CORPUS_RULE_VERSION
    assert frozen["phase2_schema"] == "phase2.3"
    assert frozen["phase2_rule"] == "phase2.3-case-scope-v1"
    assert frozen["phase3_schema"] == "phase3.4"
    assert frozen["phase3_rule"] == "phase3.4-stability-v1"
    assert frozen["phase3_prompt"] == "biological_observation_extraction:v5"
    assert CORPUS_INFRA_VERSION == "phase4a.2"
    assert CORPUS_RULE_VERSION == "phase4a2-collection-episode-v1"


def test_metastatic_spontaneous_case_is_directly_documented():
    text = (
        "Spontaneous regression of a pulmonary metastasis from melanoma. "
        "The 18 mm nodule disappeared on CT. No systemic treatment was given."
    )
    decision = classify_inclusion(
        candidate_id="batch5-davidfilho-2020",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert decision.intake_class == INCLUDED_SPONTANEOUS_REGRESSION
    assert decision.research_class == DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION


def test_biopsy_preceding_event_is_not_causal_fact():
    text = (
        "After incisional biopsy of an inguinal nodal metastasis the lesion "
        "disappeared. The authors suggest biopsy may have triggered regression."
    )
    assert biopsy_is_not_causal_fact(text) is True
    decision = classify_inclusion(
        candidate_id="batch5-hurwitz-1991",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert "caused" not in decision.note.casefold()


def test_fever_or_infection_context_is_not_causal_fact():
    text = (
        "Melanoma metastases regressed during an episode of fever and "
        "erysipelas. Infection is a temporal context, not a proven cause."
    )
    assert fever_or_infection_is_not_causal_fact(text) is True


def test_krebbers_histologic_absence_is_retrospectively_supported():
    text = (
        "Spontaneous regression of a middle ear melanoma. After subtotal "
        "petrosectomy histology showed only fibrosis and histiocytic infiltrate, "
        "no residual melanoma. Postoperative radiotherapy was given."
    )
    decision = classify_inclusion(candidate_id="batch5-krebbers-2021", text=text)
    assert decision.extract is True
    assert decision.research_class == RETROSPECTIVELY_SUPPORTED_REGRESSION


def test_krebbers_without_regression_evidence_is_treatment_associated():
    text = (
        "Middle ear melanoma treated by petrosectomy and adjuvant radiotherapy. "
        "No mention of residual-tumor absence or spontaneous change."
    )
    decision = classify_inclusion(candidate_id="batch5-krebbers-2021", text=text)
    assert decision.extract is False
    assert decision.intake_class == TREATMENT_ASSOCIATED_REFERENCE
    assert decision.research_class == TREATMENT_ASSOCIATED_REGRESSION
    assert decision.exclusion_reason == ExclusionReason.NOT_SPONTANEOUS_REGRESSION.value


def test_checkpoint_inhibitor_brain_regression_is_treatment_associated():
    text = (
        "Complete regression of melanoma brain metastases after pembrolizumab "
        "immunotherapy."
    )
    assert has_treatment_associated_regression(text) is True
    decision = classify_inclusion(
        candidate_id="batch5-pembrolizumab-brain",
        text=text,
        forced=TREATMENT_ASSOCIATED_REFERENCE,
    )
    assert decision.extract is False
    assert decision.research_class == TREATMENT_ASSOCIATED_REGRESSION


def test_batch5_polarity_guard_still_blocks_inversion():
    result = check_claim_against_quote(
        "lentigines remained",
        "lentigines disappeared",
        subject="lentigines",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION
