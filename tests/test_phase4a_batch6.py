from app.corpus.inclusion_gate import (
    DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION,
    INCLUDED_SPONTANEOUS_REGRESSION,
    RETROSPECTIVELY_SUPPORTED_REGRESSION,
    TREATMENT_ASSOCIATED_REFERENCE,
    TREATMENT_ASSOCIATED_REGRESSION,
    classify_inclusion,
    exposure_is_not_causal_fact,
    has_treatment_associated_regression,
    vitiligo_is_not_causal_fact,
)
from app.corpus.polarity import PolarityDecision, check_claim_against_quote
from app.corpus.versions import CORPUS_INFRA_VERSION, CORPUS_RULE_VERSION, frozen_ontology


def test_batch6_keeps_frozen_ontology():
    frozen = frozen_ontology()
    assert frozen["corpus_infra_version"] == "phase4a.2"
    assert frozen["phase2_schema"] == "phase2.3"
    assert frozen["phase3_schema"] == "phase3.4"
    assert frozen["phase3_prompt"] == "biological_observation_extraction:v5"
    assert CORPUS_INFRA_VERSION == "phase4a.2"
    assert CORPUS_RULE_VERSION == "phase4a2-collection-episode-v1"


def test_vitiligo_paper_is_included_but_not_causal():
    text = (
        "Complete regression of melanoma associated with vitiligo. "
        "Neither nevus nor melanoma cells were found. Later inguinal "
        "lymph-node metastasis. Interferon was given after metastasis."
    )
    assert vitiligo_is_not_causal_fact(text) is True
    decision = classify_inclusion(
        candidate_id="batch6-pique-2011",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert decision.intake_class == INCLUDED_SPONTANEOUS_REGRESSION


def test_choroidal_partial_regression_is_directly_documented():
    text = (
        "Partial spontaneous regression of choroidal melanoma. "
        "Ultrasound decreased from 9.0 x 12.4 x 15.3 mm to 3.2 x 7.2 x 10.5 mm."
    )
    decision = classify_inclusion(
        candidate_id="batch6-patel-2022",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert decision.research_class == DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION


def test_fucoidan_exposure_is_not_causal_fact():
    text = (
        "Spontaneous regression of metastases. The patient independently used "
        "fucoidan and did not receive anti-tumor therapy."
    )
    assert exposure_is_not_causal_fact(text) is True
    decision = classify_inclusion(
        candidate_id="batch6-goncharov-2025",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True


def test_checkpoint_inhibitor_covid_regression_is_treatment_associated():
    text = (
        "Blue nevus melanoma refractory to pembrolizumab, nivolumab and "
        "ipilimumab later showed regression after COVID-19."
    )
    assert has_treatment_associated_regression(text) is True
    decision = classify_inclusion(
        candidate_id="batch6-covid-ici-2025",
        text=text,
        forced=TREATMENT_ASSOCIATED_REFERENCE,
    )
    assert decision.extract is False
    assert decision.research_class == TREATMENT_ASSOCIATED_REGRESSION


def test_lallas_fully_regressed_primary_is_included():
    text = (
        "The fully regressed melanoma was found on the arm of a 50-year-old man "
        "recently diagnosed with metastatic melanoma of the ipsilateral axillary "
        "lymph nodes. Histopathology showed scar-like fibrosis and melanophages."
    )
    decision = classify_inclusion(
        candidate_id="batch6-lallas-2012",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert decision.research_class == RETROSPECTIVELY_SUPPORTED_REGRESSION


def test_batch6_polarity_guard_still_blocks_inversion():
    result = check_claim_against_quote(
        "lentigines remained",
        "lentigines disappeared",
        subject="lentigines",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION
