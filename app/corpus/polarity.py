from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from app.services.evidence_verifier import normalize_text


class DirectionPolarity(str, Enum):
    DISAPPEARANCE = "DISAPPEARANCE"
    PERSISTENCE = "PERSISTENCE"
    DECREASE = "DECREASE"
    INCREASE = "INCREASE"
    NEGATED_DISAPPEARANCE = "NEGATED_DISAPPEARANCE"
    NEGATED_CHANGE = "NEGATED_CHANGE"
    ABSENT = "ABSENT"
    PRESENT = "PRESENT"
    UNKNOWN = "UNKNOWN"


class PolarityDecision(str, Enum):
    OK = "OK"
    FACT_INVERSION = "FACT_INVERSION"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


OPPOSITES = {
    (DirectionPolarity.DISAPPEARANCE, DirectionPolarity.PERSISTENCE),
    (DirectionPolarity.PERSISTENCE, DirectionPolarity.DISAPPEARANCE),
    (DirectionPolarity.DISAPPEARANCE, DirectionPolarity.NEGATED_DISAPPEARANCE),
    (DirectionPolarity.NEGATED_DISAPPEARANCE, DirectionPolarity.DISAPPEARANCE),
    (DirectionPolarity.DECREASE, DirectionPolarity.INCREASE),
    (DirectionPolarity.INCREASE, DirectionPolarity.DECREASE),
    (DirectionPolarity.DECREASE, DirectionPolarity.NEGATED_CHANGE),
    (DirectionPolarity.ABSENT, DirectionPolarity.PRESENT),
    (DirectionPolarity.PRESENT, DirectionPolarity.ABSENT),
}

LITERATURE_RE = re.compile(
    r"\b(?:it is estimated|reported in the (?:known )?literature|"
    r"according to the (?:known )?literature|most cases|"
    r"has been proposed|ranges from|\d+\s*%|\bpercent of)\b",
    re.I,
)

BUT_NOT_RE = re.compile(
    r"\bbut not (?P<subject>[a-z0-9 \-]+?)(?:,| \(| had | have | were | was )",
    re.I,
)


@dataclass(frozen=True)
class PolarityResult:
    decision: PolarityDecision
    quote_polarity: DirectionPolarity
    claim_polarity: DirectionPolarity
    subject: str | None = None
    reason: str = ""


def is_literature_statement(text: str | None) -> bool:
    return bool(text and LITERATURE_RE.search(normalize_text(text)))


def polarity_of(text: str | None) -> DirectionPolarity:
    if not text:
        return DirectionPolarity.UNKNOWN
    normalized = normalize_text(text)
    if re.search(
        r"\b(?:did not|does not|do not|no)\s+"
        r"(?:disappear|regress|resolve|vanish|reduce)\b",
        normalized,
    ) or re.search(r"\bno regression\b|\bnot reduced\b", normalized):
        return DirectionPolarity.NEGATED_DISAPPEARANCE
    if re.search(
        r"\bremained unchanged\b|\bno (?:change|enlargement)\b|\bnot enlarged\b",
        normalized,
    ):
        return DirectionPolarity.NEGATED_CHANGE
    if re.search(
        r"\bno viable (?:tumor|malignant|melanoma|neoplastic)|"
        r"\babsence of (?:melanocytic|viable|malignant|neoplastic)|"
        r"\bno evidence of (?:disease|recurrence|metastasis)\b",
        normalized,
    ):
        return DirectionPolarity.ABSENT
    if re.search(
        r"\b(?:remained|persisted|still present|continued to be visible|"
        r"retained|unchanged|except)\b",
        normalized,
    ):
        return DirectionPolarity.PERSISTENCE
    if re.search(
        r"\b(?:disappeared|resolved|vanished|no longer visible|"
        r"complete regression|absent at follow-?up)\b",
        normalized,
    ):
        return DirectionPolarity.DISAPPEARANCE
    if re.search(
        r"\b(?:decreased|reduced|smaller|partial regression|diminution)\b",
        normalized,
    ):
        return DirectionPolarity.DECREASE
    if re.search(
        r"\b(?:increased|enlarged|progressed|more numerous|grew)\b",
        normalized,
    ):
        return DirectionPolarity.INCREASE
    if re.search(r"\bviable (?:tumor|malignant|melanoma) cells\b", normalized):
        return DirectionPolarity.PRESENT
    return DirectionPolarity.UNKNOWN


def subject_excluded_from_disappearance(quote: str | None) -> str | None:
    if not quote:
        return None
    normalized = normalize_text(quote)
    match = BUT_NOT_RE.search(normalized)
    if match:
        return match.group("subject").strip()
    except_match = re.search(
        r"\ball (?:the )?(?:her |his )?nevi,? but not (?P<sub>[a-z0-9 \-]+)",
        normalized,
    )
    if except_match:
        return except_match.group("sub").strip()
    return None


def check_claim_against_quote(
    quote: str | None,
    claim: str | None,
    *,
    subject: str | None = None,
) -> PolarityResult:
    quote_polarity = polarity_of(quote)
    claim_polarity = polarity_of(claim)
    excluded = subject_excluded_from_disappearance(quote)
    claim_text = normalize_text(claim or "")
    if excluded:
        excluded_tokens = {token for token in excluded.split() if len(token) > 3}
        subject_text = normalize_text(subject or "")
        mentions_excluded = bool(excluded_tokens & set(claim_text.split())) or bool(
            excluded_tokens & set(subject_text.split())
        )
        if mentions_excluded and claim_polarity == DirectionPolarity.DISAPPEARANCE:
            return PolarityResult(
                PolarityDecision.FACT_INVERSION,
                DirectionPolarity.PERSISTENCE,
                claim_polarity,
                excluded,
                "Quote excludes this subject from disappearance.",
            )
        if mentions_excluded and claim_polarity == DirectionPolarity.PERSISTENCE:
            return PolarityResult(
                PolarityDecision.OK,
                DirectionPolarity.PERSISTENCE,
                claim_polarity,
                excluded,
            )
    if (quote_polarity, claim_polarity) in OPPOSITES:
        return PolarityResult(
            PolarityDecision.FACT_INVERSION,
            quote_polarity,
            claim_polarity,
            subject,
            "Source polarity contradicts the normalized claim.",
        )
    if quote_polarity == DirectionPolarity.UNKNOWN or claim_polarity == DirectionPolarity.UNKNOWN:
        if quote and claim and _loose_opposite(quote, claim):
            return PolarityResult(
                PolarityDecision.RECONCILIATION_REQUIRED,
                quote_polarity,
                claim_polarity,
                subject,
                "Possible polarity conflict; deterministic parser is uncertain.",
            )
        return PolarityResult(
            PolarityDecision.OK, quote_polarity, claim_polarity, subject
        )
    return PolarityResult(
        PolarityDecision.OK, quote_polarity, claim_polarity, subject
    )


def _loose_opposite(quote: str, claim: str) -> bool:
    quote_n = normalize_text(quote)
    claim_n = normalize_text(claim)
    if "remain" in quote_n and "disappear" in claim_n:
        return True
    if "persist" in quote_n and re.search(r"\b(?:disappear|resolv|vanish)\b", claim_n):
        return True
    return False


def deterministic_persistence_claim(quote: str | None, subject: str | None) -> str | None:
    excluded = subject_excluded_from_disappearance(quote)
    target = excluded or subject
    if not target:
        return None
    if polarity_of(quote) in {
        DirectionPolarity.PERSISTENCE,
        DirectionPolarity.NEGATED_DISAPPEARANCE,
    } or excluded:
        return f"{target} remained"
    return None
