from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.corpus.versions import CORPUS_INFRA_VERSION
from app.models import Case, Lesion, LesionState, RegressionEpisode


def build_case_index(cases: list[Case]) -> list[dict[str, Any]]:
    rows = []
    for case in cases:
        rows.append(
            {
                "paper_id": case.paper_id,
                "case_id": case.id,
                "patient_marker": case.patient_identifier,
                "year": case.paper.year if case.paper else None,
                "melanoma_context": case.melanoma_subtype or case.primary_site,
            }
        )
    _assert_unique(rows, ("paper_id", "case_id"), "CaseIndex")
    return rows


def build_lesion_index(
    lesions: list[Lesion],
    states: list[LesionState] | None = None,
) -> list[dict[str, Any]]:
    role_by_lesion = {}
    for state in states or []:
        if state.lesion_id is not None:
            role_by_lesion[state.lesion_id] = state.regression_status
    rows = []
    for lesion in lesions:
        rows.append(
            {
                "case_id": lesion.case_id,
                "lesion_id": lesion.id,
                "organ": lesion.organ,
                "location": lesion.anatomical_location,
                "laterality": lesion.laterality,
                "collection_id": None,
                "regression_role": role_by_lesion.get(lesion.id),
            }
        )
    _assert_unique(rows, ("case_id", "lesion_id"), "LesionIndex")
    return rows


def build_episode_index(episodes: list[RegressionEpisode]) -> list[dict[str, Any]]:
    rows = []
    for episode in episodes:
        rows.append(
            {
                "case_id": episode.case_id,
                "episode_id": episode.id,
                "episode_type": (
                    episode.episode_type.value
                    if hasattr(episode.episode_type, "value")
                    else episode.episode_type
                ),
                "extent": (
                    episode.extent.value
                    if hasattr(episode.extent, "value")
                    else episode.extent
                ),
                "associated_lesions": episode.associated_lesion_ids or [],
                "temporal_relation": episode.spontaneous_status,
            }
        )
    _assert_unique(rows, ("case_id", "episode_id"), "RegressionEpisodeIndex")
    return rows


def load_seed_entities(
    session: Session, case_ids: list[int], run_ids: list[int]
) -> tuple[list[Case], list[Lesion], list[RegressionEpisode], list[LesionState]]:
    cases = list(
        session.scalars(select(Case).where(Case.id.in_(case_ids or [-1])).order_by(Case.id))
    )
    lesions = list(
        session.scalars(
            select(Lesion)
            .where(
                Lesion.case_id.in_(case_ids or [-1]),
                Lesion.created_from_run_id.in_(run_ids or [-1]),
            )
            .order_by(Lesion.id)
        )
    )
    episodes = list(
        session.scalars(
            select(RegressionEpisode)
            .where(
                RegressionEpisode.case_id.in_(case_ids or [-1]),
                RegressionEpisode.created_from_run_id.in_(run_ids or [-1]),
            )
            .order_by(RegressionEpisode.id)
        )
    )
    states = list(
        session.scalars(
            select(LesionState)
            .where(
                LesionState.case_id.in_(case_ids or [-1]),
                LesionState.created_from_run_id.in_(run_ids or [-1]),
            )
        )
    )
    return cases, lesions, episodes, states


def index_payload(
    cases: list[Case],
    lesions: list[Lesion],
    episodes: list[RegressionEpisode],
    states: list[LesionState] | None = None,
) -> dict[str, Any]:
    return {
        "version": CORPUS_INFRA_VERSION,
        "analysis_enabled": False,
        "case_index": build_case_index(cases),
        "lesion_index": build_lesion_index(lesions, states),
        "episode_index": build_episode_index(episodes),
    }


def _assert_unique(
    rows: list[dict[str, Any]], keys: tuple[str, ...], label: str
) -> None:
    seen: set[tuple[Any, ...]] = set()
    for row in rows:
        item = tuple(row[key] for key in keys)
        if item in seen:
            raise ValueError(f"{label} duplicate {item}")
        seen.add(item)
