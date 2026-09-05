from __future__ import annotations

import re
from dataclasses import dataclass

from app.corpus.states import ExclusionReason


INCLUDED_SPONTANEOUS_REGRESSION = "INCLUDED_SPONTANEOUS_REGRESSION"
EXCLUDED_NOT_SPONTANEOUS = "EXCLUDED_NOT_SPONTANEOUS"
LATENT_REGRESSION_DISCOVERY_SOURCE = "LATENT_REGRESSION_DISCOVERY_SOURCE"
TREATMENT_ASSOCIATED_REFERENCE = "TREATMENT_ASSOCIATED_REFERENCE"
UNCERTAIN_INCLUSION = "UNCERTAIN_INCLUSION"

DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION = (
    "DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION"
)
RETROSPECTIVELY_SUPPORTED_REGRESSION = "RETROSPECTIVELY_SUPPORTED_REGRESSION"
LATENT_OR_HYPOTHESIZED_REGRESSION = "LATENT_OR_HYPOTHESIZED_REGRESSION"
TREATMENT_ASSOCIATED_REGRESSION = "TREATMENT_ASSOCIATED_REGRESSION"
NOT_REGRESSION = "NOT_REGRESSION"

TREATMENT_MARKERS = (
    "pembrolizumab",
    "ipilimumab",
    "nivolumab",
    "vemurafenib",
    "dabrafenib",
    "trametinib",
    "braf inhibitor",
    "braf inhibitors",
    "chemotherapy",
    "immunotherapy",
    "targeted therapy",
)
TUMORAL_MELANOSIS_RE = re.compile(r"\btumoral melanosis\b", re.I)
PROVEN_MELANOMA_RE = re.compile(
    r"\b(?:histologically (?:verified|confirmed|proven) melanoma|"
    r"malignant melanoma|primary cutaneous melanoma|"
    r"lentigo maligna melanoma)\b",
    re.I,
)
HYPOTHESIS_RE = re.compile(
    r"\b(?:it is believed|may represent|could represent|"
    r"difficult to state|uncertain origin|unknown primary)\b",
    re.I,
)
NO_ATYPICAL_MELANOCYTES_RE = re.compile(
    r"\bno atypical melanocytes\b|\batypical melanocytes (?:were )?absent\b|"
    r"\bno (?:viable )?melanoma cells\b",
    re.I,
)
SPONTANEOUS_RE = re.compile(r"\bspontaneous(?:ly)? regress", re.I)
PREGNANCY_RE = re.compile(r"\b(?:pregnan|postpartum|after delivery|post-partum)\b", re.I)


@dataclass(frozen=True)
class InclusionDecision:
    intake_class: str
    research_class: str
    extract: bool
    exclusion_reason: str | None
    discovery_track: str | None
    note: str


def compact_text(text: str) -> str:
    return (
        text.casefold()
        .replace("-\n", "")
        .replace("\n", " ")
        .replace("  ", " ")
    )


def has_treatment_associated_regression(text: str) -> bool:
    compact = compact_text(text)
    if not any(marker in compact for marker in TREATMENT_MARKERS):
        return False
    return bool(
        TUMORAL_MELANOSIS_RE.search(compact)
        or "regress" in compact
        or "involution" in compact
    )


def is_unproven_tumoral_melanosis(text: str) -> bool:
    compact = compact_text(text)
    if not TUMORAL_MELANOSIS_RE.search(compact):
        return False
    hypothesized = bool(HYPOTHESIS_RE.search(compact))
    no_atypical = bool(NO_ATYPICAL_MELANOCYTES_RE.search(compact))
    proven = bool(PROVEN_MELANOMA_RE.search(compact))
    if hypothesized and no_atypical and not proven:
        return True
    if hypothesized and "thin melanoma that progressed into complete regression" in compact:
        return True
    return hypothesized and no_atypical


def classify_inclusion(
    *,
    candidate_id: str,
    text: str,
    forced: str | None = None,
) -> InclusionDecision:
    compact = compact_text(text)
    treatment_paper = (
        "braf" in candidate_id
        or "pembrolizumab" in candidate_id
        or forced == TREATMENT_ASSOCIATED_REFERENCE
    )
    if treatment_paper and (
        forced == TREATMENT_ASSOCIATED_REFERENCE
        or has_treatment_associated_regression(compact)
    ):
        return InclusionDecision(
            intake_class=TREATMENT_ASSOCIATED_REFERENCE,
            research_class=TREATMENT_ASSOCIATED_REGRESSION,
            extract=False,
            exclusion_reason=ExclusionReason.NOT_SPONTANEOUS_REGRESSION.value,
            discovery_track="TREATMENT_ASSOCIATED",
            note=(
                "Treatment-associated regression / tumoral melanosis. "
                "Not ingested as a spontaneous-regression corpus case."
            ),
        )
    if forced == LATENT_REGRESSION_DISCOVERY_SOURCE or (
        candidate_id.endswith("tumoral-melanosis-2021")
        or is_unproven_tumoral_melanosis(compact)
    ):
        return InclusionDecision(
            intake_class=LATENT_REGRESSION_DISCOVERY_SOURCE,
            research_class=LATENT_OR_HYPOTHESIZED_REGRESSION,
            extract=False,
            exclusion_reason=ExclusionReason.NOT_SPONTANEOUS_REGRESSION.value,
            discovery_track="LATENT_REGRESSION",
            note=(
                "Tumoral melanosis without a directly proven prior melanoma. "
                "LATENT/uncertain origin; no forced RegressionEpisode."
            ),
        )
    if candidate_id.endswith("krebbers-2021"):
        histologic_absence = (
            "no residual melanoma" in compact
            or "only fibrosis" in compact
            or bool(NO_ATYPICAL_MELANOCYTES_RE.search(compact))
        )
        if histologic_absence or SPONTANEOUS_RE.search(compact):
            return InclusionDecision(
                intake_class=INCLUDED_SPONTANEOUS_REGRESSION,
                research_class=RETROSPECTIVELY_SUPPORTED_REGRESSION,
                extract=True,
                exclusion_reason=None,
                discovery_track=None,
                note=(
                    "Histologic absence of residual melanoma documented at "
                    "resection. Surgery and adjuvant radiotherapy remain Events; "
                    "they are not promoted to a spontaneous-regression cause."
                ),
            )
        return InclusionDecision(
            intake_class=TREATMENT_ASSOCIATED_REFERENCE,
            research_class=TREATMENT_ASSOCIATED_REGRESSION,
            extract=False,
            exclusion_reason=ExclusionReason.NOT_SPONTANEOUS_REGRESSION.value,
            discovery_track="TREATMENT_ASSOCIATED",
            note=(
                "Middle-ear melanoma course could not be separated from "
                "surgery/radiotherapy. Kept as treatment-associated reference."
            ),
        )
    if forced == INCLUDED_SPONTANEOUS_REGRESSION or (
        candidate_id.endswith("ehrsam-2016")
        or candidate_id.endswith("allen-1955")
    ):
        research = (
            DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION
            if SPONTANEOUS_RE.search(compact) or "disappeared spontaneously" in compact
            else RETROSPECTIVELY_SUPPORTED_REGRESSION
        )
        if candidate_id.endswith("ehrsam-2016"):
            research = RETROSPECTIVELY_SUPPORTED_REGRESSION
        return InclusionDecision(
            intake_class=INCLUDED_SPONTANEOUS_REGRESSION,
            research_class=research,
            extract=True,
            exclusion_reason=None,
            discovery_track=None,
            note="Documented patient-level regression retained for extraction.",
        )
    return InclusionDecision(
        intake_class=UNCERTAIN_INCLUSION,
        research_class=LATENT_OR_HYPOTHESIZED_REGRESSION,
        extract=False,
        exclusion_reason=ExclusionReason.INSUFFICIENT_CASE_DATA.value,
        discovery_track="UNCERTAIN_INCLUSION",
        note="Inclusion remained uncertain after the frozen gate.",
    )


def pregnancy_is_not_causal_fact(text: str) -> bool:
    """Pregnancy/postpartum timing may be present; causation is not a fact."""
    compact = compact_text(text)
    return bool(PREGNANCY_RE.search(compact))


def preceding_event_is_not_causal_fact(text: str, *event_terms: str) -> bool:
    """A documented preceding event is not automatically a causal fact."""
    compact = compact_text(text)
    return any(term.casefold() in compact for term in event_terms)


def biopsy_is_not_causal_fact(text: str) -> bool:
    return preceding_event_is_not_causal_fact(text, "biopsy")


def fever_or_infection_is_not_causal_fact(text: str) -> bool:
    return preceding_event_is_not_causal_fact(text, "fever", "infection", "erysipelas")


def exposure_is_not_causal_fact(text: str) -> bool:
    """Diet/supplement/fucoidan exposure may be present; causation is not a fact."""
    return preceding_event_is_not_causal_fact(
        text, "fucoidan", "green tea", "antioxidant", "pineapple", "supplement", "diet"
    )


def vitiligo_is_not_causal_fact(text: str) -> bool:
    """Vitiligo/leukoderma may be a phenotype; it is not a causal fact."""
    return preceding_event_is_not_causal_fact(text, "vitiligo", "leukoderma")
