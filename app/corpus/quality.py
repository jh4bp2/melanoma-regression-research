from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    BiologicalObservation,
    Case,
    Event,
    Evidence,
    FieldEvidenceLink,
    Lesion,
    QuoteVerificationStatus,
)
from app.services.evidence_verifier import normalize_text


def score_case(
    session: Session,
    case: Case,
    *,
    observation_run_ids: list[int],
    event_run_id: int | None,
) -> dict[str, Any]:
    observations = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.case_id == case.id,
                BiologicalObservation.created_from_run_id.in_(
                    observation_run_ids or [-1]
                ),
            )
        )
    )
    events = list(
        session.scalars(
            select(Event).where(
                Event.case_id == case.id,
                Event.extraction_run_id == event_run_id,
            )
        )
    ) if event_run_id else []
    lesions = list(
        session.scalars(
            select(Lesion).where(
                Lesion.case_id == case.id,
                Lesion.created_from_run_id.in_(observation_run_ids or [-1]),
            )
        )
    )
    links = list(
        session.scalars(
            select(FieldEvidenceLink).where(
                FieldEvidenceLink.extraction_run_id.in_(
                    [*(observation_run_ids or []), *([event_run_id] if event_run_id else [])]
                    or [-1]
                )
            )
        )
    )
    evidence_ids = {link.evidence_id for link in links}
    evidence_rows = list(
        session.scalars(select(Evidence).where(Evidence.id.in_(evidence_ids or [-1])))
    )
    verified = [
        row
        for row in evidence_rows
        if row.verification_status
        in {
            QuoteVerificationStatus.VERIFIED_EXACT.value,
            QuoteVerificationStatus.VERIFIED_NORMALIZED.value,
            "VERIFIED_EXACT",
            "VERIFIED_NORMALIZED",
        }
        or row.status.value == "SUPPORTED"
    ]
    quote_rate = (len(verified) / len(evidence_rows)) if evidence_rows else 0.0
    timed_events = [
        event
        for event in events
        if event.event_date or event.relative_time or event.relative_day is not None
    ]
    named_lesions = [
        lesion
        for lesion in lesions
        if lesion.organ or lesion.laterality or lesion.anatomical_location
    ]
    biological = [
        observation
        for observation in observations
        if observation.observation_domain == "BIOLOGICAL_STATE"
    ]
    uncertain = [
        observation
        for observation in observations
        if "uncertain" in normalize_text(observation.case_scope_status or "")
    ]
    scores = {
        "provenance_completeness": _clip(quote_rate),
        "temporal_completeness": _clip(len(timed_events) / max(len(events), 1)),
        "lesion_identity_quality": _clip(len(named_lesions) / max(len(lesions), 1) if lesions else 0.0),
        "biological_measurement_density": _clip(len(biological) / 8),
        "case_scope_confidence": _clip(1.0 - (len(uncertain) / max(len(observations), 1))),
        "quote_verification_rate": _clip(quote_rate),
    }
    return {
        "paper_id": case.paper_id,
        "case_id": case.id,
        "kind": "data_quality_not_biological_importance",
        "scores": scores,
        "mean": round(sum(scores.values()) / len(scores), 4),
    }


def _clip(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)
