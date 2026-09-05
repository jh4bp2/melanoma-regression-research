from __future__ import annotations

import enum


class PaperIntakeState(str, enum.Enum):
    CANDIDATE = "CANDIDATE"
    FULLTEXT_FOUND = "FULLTEXT_FOUND"
    FULLTEXT_UNAVAILABLE = "FULLTEXT_UNAVAILABLE"
    INGESTED = "INGESTED"
    EXTRACTED = "EXTRACTED"
    AUDITED = "AUDITED"
    EXCLUDED = "EXCLUDED"


class ExclusionReason(str, enum.Enum):
    NOT_MELANOMA = "NOT_MELANOMA"
    NOT_SPONTANEOUS_REGRESSION = "NOT_SPONTANEOUS_REGRESSION"
    NO_PATIENT_CASE = "NO_PATIENT_CASE"
    NO_FULLTEXT = "NO_FULLTEXT"
    DUPLICATE_REPORT = "DUPLICATE_REPORT"
    INSUFFICIENT_CASE_DATA = "INSUFFICIENT_CASE_DATA"
    OTHER = "OTHER"


class QualityStatus(str, enum.Enum):
    SEED = "SEED"
    PENDING = "PENDING"
    PASS = "PASS"
    REVIEW = "REVIEW"
    FAIL = "FAIL"


class MeasurementStatus(str, enum.Enum):
    MEASURED = "MEASURED"
    REPORTED_QUALITATIVELY = "REPORTED_QUALITATIVELY"
    REPORTED_ABSENT = "REPORTED_ABSENT"
    NOT_REPORTED = "NOT_REPORTED"
    UNCERTAIN = "UNCERTAIN"


ALLOWED_TRANSITIONS = {
    PaperIntakeState.CANDIDATE: {
        PaperIntakeState.FULLTEXT_FOUND,
        PaperIntakeState.FULLTEXT_UNAVAILABLE,
        PaperIntakeState.EXCLUDED,
    },
    PaperIntakeState.FULLTEXT_FOUND: {
        PaperIntakeState.INGESTED,
        PaperIntakeState.FULLTEXT_UNAVAILABLE,
        PaperIntakeState.EXCLUDED,
    },
    PaperIntakeState.FULLTEXT_UNAVAILABLE: {
        PaperIntakeState.FULLTEXT_FOUND,
        PaperIntakeState.EXCLUDED,
    },
    PaperIntakeState.INGESTED: {
        PaperIntakeState.EXTRACTED,
        PaperIntakeState.EXCLUDED,
    },
    PaperIntakeState.EXTRACTED: {
        PaperIntakeState.AUDITED,
    },
    PaperIntakeState.AUDITED: set(),
    PaperIntakeState.EXCLUDED: set(),
}


def can_transition(current: PaperIntakeState, nxt: PaperIntakeState) -> bool:
    if current == nxt:
        return True
    return nxt in ALLOWED_TRANSITIONS[current]
