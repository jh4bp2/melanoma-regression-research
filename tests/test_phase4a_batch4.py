from app.corpus.inclusion_gate import (
    DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION,
    INCLUDED_SPONTANEOUS_REGRESSION,
    LATENT_OR_HYPOTHESIZED_REGRESSION,
    LATENT_REGRESSION_DISCOVERY_SOURCE,
    RETROSPECTIVELY_SUPPORTED_REGRESSION,
    TREATMENT_ASSOCIATED_REFERENCE,
    TREATMENT_ASSOCIATED_REGRESSION,
    classify_inclusion,
    has_treatment_associated_regression,
    is_unproven_tumoral_melanosis,
    pregnancy_is_not_causal_fact,
)
from app.corpus.polarity import PolarityDecision, check_claim_against_quote
from app.corpus.versions import CORPUS_INFRA_VERSION, frozen_ontology
from app.corpus.states import ExclusionReason


def test_batch4_keeps_frozen_ontology():
    frozen = frozen_ontology()
    assert frozen["corpus_infra_version"] == "phase4a.2"
    assert frozen["phase2_schema"] == "phase2.3"
    assert frozen["phase3_schema"] == "phase3.4"
    assert frozen["phase3_prompt"] == "biological_observation_extraction:v5"
    assert CORPUS_INFRA_VERSION == "phase4a.2"


def test_fully_regressive_melanoma_is_included():
    text = (
        "Fully regressive melanoma without any metastases. "
        "Dermoscopy and absence of melanoma on final biopsy confirmed the diagnosis. "
        "Fibrosis and melanophages replaced the lesion."
    )
    decision = classify_inclusion(
        candidate_id="batch4-ehrsam-2016",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert decision.intake_class == INCLUDED_SPONTANEOUS_REGRESSION
    assert decision.research_class == RETROSPECTIVELY_SUPPORTED_REGRESSION


def test_pregnancy_paper_is_included_but_not_causal():
    text = (
        "Malignant melanoma recurred in widely disseminated form during pregnancy "
        "and disappeared spontaneously after delivery."
    )
    decision = classify_inclusion(
        candidate_id="batch4-allen-1955",
        text=text,
        forced=INCLUDED_SPONTANEOUS_REGRESSION,
    )
    assert decision.extract is True
    assert decision.research_class == DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION
    assert pregnancy_is_not_causal_fact(text) is True


def test_unproven_tumoral_melanosis_is_latent():
    text = (
        "Tumoral melanosis. No atypical melanocytes. It is believed that the "
        "patient had a thin melanoma that progressed into complete regression."
    )
    assert is_unproven_tumoral_melanosis(text) is True
    decision = classify_inclusion(
        candidate_id="batch4-tumoral-melanosis-2021",
        text=text,
        forced=LATENT_REGRESSION_DISCOVERY_SOURCE,
    )
    assert decision.extract is False
    assert decision.intake_class == LATENT_REGRESSION_DISCOVERY_SOURCE
    assert decision.research_class == LATENT_OR_HYPOTHESIZED_REGRESSION
    assert decision.exclusion_reason == ExclusionReason.NOT_SPONTANEOUS_REGRESSION.value


def test_braf_inhibitor_regression_is_treatment_associated():
    text = (
        "Complete regression of primary melanoma and involution of papillomatous "
        "nevi under BRAF inhibitors. Vemurafenib then dabrafenib."
    )
    assert has_treatment_associated_regression(text) is True
    decision = classify_inclusion(
        candidate_id="batch4-braf-2019",
        text=text,
        forced=TREATMENT_ASSOCIATED_REFERENCE,
    )
    assert decision.extract is False
    assert decision.intake_class == TREATMENT_ASSOCIATED_REFERENCE
    assert decision.research_class == TREATMENT_ASSOCIATED_REGRESSION


def test_pembrolizumab_tumoral_melanosis_is_treatment_associated():
    text = (
        "Metastatic melanoma treated with pembrolizumab who developed tumoral "
        "melanosis at previous sites of metastases."
    )
    decision = classify_inclusion(
        candidate_id="batch4-pembrolizumab-2017",
        text=text,
        forced=TREATMENT_ASSOCIATED_REFERENCE,
    )
    assert decision.extract is False
    assert decision.intake_class == TREATMENT_ASSOCIATED_REFERENCE
    assert "spontaneous" not in (decision.discovery_track or "").casefold()


def test_batch4_polarity_guard_still_blocks_inversion():
    result = check_claim_against_quote(
        "lentigines remained",
        "lentigines disappeared",
        subject="lentigines",
    )
    assert result.decision == PolarityDecision.FACT_INVERSION


def test_exclusion_reason_stays_on_frozen_enum():
    assert ExclusionReason.NOT_SPONTANEOUS_REGRESSION.value == "NOT_SPONTANEOUS_REGRESSION"
