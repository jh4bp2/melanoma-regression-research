from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.corpus.states import MeasurementStatus
from app.corpus.versions import CORPUS_INFRA_VERSION
from app.models import (
    BiologicalObservation,
    Case,
    Event,
    EventType,
    ExplanatoryAlternative,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    ObservationDomain,
    RegressionEpisode,
)
from app.services.evidence_verifier import normalize_text


MATRIX_COLUMNS = (
    "infection",
    "fever",
    "surgery",
    "biopsy",
    "vaccination",
    "immunotherapy_history",
    "immune_infiltration",
    "CD3",
    "CD8",
    "NK",
    "macrophage",
    "FDG_SUV",
    "necrosis",
    "viable_tumor",
    "hypoxia",
    "metabolic_marker",
    "genotype",
    "irAE",
    "leukoderma",
    "regression_extent",
    "progression_elsewhere",
)

EVENT_COLUMNS = {
    "infection": EventType.INFECTION,
    "fever": EventType.FEVER,
    "surgery": EventType.SURGERY,
    "biopsy": EventType.BIOPSY,
    "vaccination": EventType.VACCINATION,
}


def empty_cell() -> dict[str, str]:
    return {
        "value": "UNKNOWN",
        "measurement_status": MeasurementStatus.NOT_REPORTED.value,
    }


def measured_cell(value: str, qualitative: bool = True) -> dict[str, str]:
    return {
        "value": value,
        "measurement_status": (
            MeasurementStatus.REPORTED_QUALITATIVELY.value
            if qualitative
            else MeasurementStatus.MEASURED.value
        ),
    }


def absent_cell() -> dict[str, str]:
    return {
        "value": "ABSENT",
        "measurement_status": MeasurementStatus.REPORTED_ABSENT.value,
    }


def skeleton(
    *,
    case_rows: list[dict[str, Any]] | None = None,
    lesion_rows: list[dict[str, Any]] | None = None,
    episode_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "version": CORPUS_INFRA_VERSION,
        "analysis_enabled": False,
        "note": "Skeleton only. Do not compute correlations or causal scores.",
        "columns": list(MATRIX_COLUMNS),
        "value_and_status_separated": True,
        "case_rows": case_rows or [],
        "lesion_rows": lesion_rows or [],
        "episode_rows": episode_rows or [],
    }


def build_case_row(
    session: Session,
    case: Case,
    observation_run_ids: list[int],
    event_run_id: int | None,
) -> dict[str, Any]:
    observations = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.case_id == case.id,
                BiologicalObservation.created_from_run_id.in_(observation_run_ids or [-1]),
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
    genotypes = list(
        session.scalars(
            select(GenotypeObservation).where(
                GenotypeObservation.case_id == case.id,
                GenotypeObservation.created_from_run_id.in_(observation_run_ids or [-1]),
            )
        )
    )
    iraes = list(
        session.scalars(
            select(ImmuneRelatedAdverseEvent).where(
                ImmuneRelatedAdverseEvent.case_id == case.id,
                ImmuneRelatedAdverseEvent.created_from_run_id.in_(
                    observation_run_ids or [-1]
                ),
            )
        )
    )
    alternatives = list(
        session.scalars(
            select(ExplanatoryAlternative).where(
                ExplanatoryAlternative.case_id == case.id,
                ExplanatoryAlternative.created_from_run_id.in_(
                    observation_run_ids or [-1]
                ),
            )
        )
    )
    episodes = list(
        session.scalars(
            select(RegressionEpisode).where(
                RegressionEpisode.case_id == case.id,
                RegressionEpisode.created_from_run_id.in_(observation_run_ids or [-1]),
            )
        )
    )
    cells = {column: empty_cell() for column in MATRIX_COLUMNS}
    _fill_event_cells(cells, events)
    _fill_observation_cells(cells, observations)
    if genotypes:
        cells["genotype"] = measured_cell(
            ",".join(sorted({row.gene for row in genotypes}))
        )
    if iraes:
        cells["irAE"] = measured_cell(
            ",".join(sorted({row.event_type for row in iraes}))
        )
    if alternatives:
        cells["immunotherapy_history"] = _prefer(
            cells["immunotherapy_history"],
            measured_cell("AUTHOR_ALTERNATIVE_PRESENT"),
        )
    if episodes:
        extents = sorted(
            {
                row.extent.value if hasattr(row.extent, "value") else str(row.extent)
                for row in episodes
            }
        )
        cells["regression_extent"] = measured_cell("|".join(extents))
    return {
        "row_type": "case",
        "paper_id": case.paper_id,
        "case_id": case.id,
        "cells": cells,
    }


def _fill_event_cells(cells: dict[str, dict[str, str]], events: list[Event]) -> None:
    for column, event_type in EVENT_COLUMNS.items():
        matched = [event for event in events if event.event_type == event_type]
        if matched:
            cells[column] = measured_cell("PRESENT")
    if any(
        re.search(
            r"\b(?:ipilimumab|nivolumab|pembrolizumab|checkpoint)\b",
            normalize_text(event.description),
        )
        for event in events
    ):
        cells["immunotherapy_history"] = measured_cell("PRESENT")
    if any(event.event_type == EventType.TUMOR_PROGRESSION for event in events):
        cells["progression_elsewhere"] = measured_cell("PRESENT")


def _fill_observation_cells(
    cells: dict[str, dict[str, str]],
    observations: list[BiologicalObservation],
) -> None:
    for observation in observations:
        text = normalize_text(
            f"{observation.variable_name} {observation.value or ''} "
            f"{observation.normalized_variable or ''}"
        )
        status = observation.status
        if "infect" in text:
            cells["infection"] = _status_cell(observation, "PRESENT")
        if "fever" in text:
            cells["fever"] = _status_cell(observation, "PRESENT")
        if re.search(r"\bvaccin", text):
            cells["vaccination"] = _status_cell(observation, "PRESENT")
        if re.search(r"\b(?:cd3|cd8|nk|macrophage|infiltrat)\b", text):
            cells["immune_infiltration"] = _status_cell(observation, "PRESENT")
        if re.search(r"\bcd3\b", text):
            cells["CD3"] = _status_cell(observation, "PRESENT")
        if re.search(r"\bcd8\b", text):
            cells["CD8"] = _status_cell(observation, "PRESENT")
        if re.search(r"\bnk\b", text):
            cells["NK"] = _status_cell(observation, "PRESENT")
        if "macrophage" in text:
            cells["macrophage"] = _status_cell(observation, "PRESENT")
        if re.search(r"\b(?:suv|fdg)\b", text):
            cells["FDG_SUV"] = _status_cell(
                observation, observation.value or "REPORTED", qualitative=False
            )
        if "necro" in text:
            cells["necrosis"] = _status_cell(observation, observation.value or "PRESENT")
        if re.search(r"\bviable\b", text):
            value = (
                "ABSENT"
                if status == "REPORTED_ABSENT"
                or re.search(r"\bno viable|absent\b", text)
                else (observation.value or "PRESENT")
            )
            cells["viable_tumor"] = _status_cell(observation, value)
        if "hypox" in text:
            cells["hypoxia"] = _status_cell(observation, observation.value or "PRESENT")
        if re.search(r"\b(?:metabol|lactate|glucose)\b", text):
            cells["metabolic_marker"] = _status_cell(
                observation, observation.value or "PRESENT"
            )
        if re.search(r"\b(?:leukoderma|vitiligo)\b", text):
            cells["leukoderma"] = _status_cell(observation, "PRESENT")
        if (
            observation.observation_domain
            == ObservationDomain.DISEASE_PHENOTYPE.value
            and re.search(r"\bprogress", text)
        ):
            cells["progression_elsewhere"] = _status_cell(observation, "PRESENT")


def _status_cell(
    observation: BiologicalObservation, value: str, qualitative: bool = True
) -> dict[str, str]:
    if observation.status == "REPORTED_ABSENT":
        return absent_cell()
    if observation.status == "UNCERTAIN":
        return {
            "value": value,
            "measurement_status": MeasurementStatus.UNCERTAIN.value,
        }
    if observation.status == "NOT_REPORTED":
        return empty_cell()
    return measured_cell(value, qualitative=qualitative)


def _prefer(
    current: dict[str, str], incoming: dict[str, str]
) -> dict[str, str]:
    if current["measurement_status"] == MeasurementStatus.NOT_REPORTED.value:
        return incoming
    return current
