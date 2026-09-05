from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    BiologicalObservation,
    Case,
    ExplanatoryAlternative,
    ExtractionRun,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    LesionState,
    ObservationCategory,
    ObservationDomain,
    RegressionEpisode,
)
from app.services.evidence_verifier import normalize_text
from app.services.recall_hardening import core_entity_signature


@dataclass(frozen=True)
class GoldenCheck:
    paper_id: int
    name: str
    kind: str
    matcher: str


GOLDEN_EXPECTATIONS: tuple[GoldenCheck, ...] = (
    GoldenCheck(3, "infection_context", "clinical_context", r"infect"),
    GoldenCheck(3, "cd3_cd8_infiltration", "immune_pathology", r"\bcd3\b|\bcd8\b"),
    GoldenCheck(3, "braf_wild_type", "genotype", r"braf\|wild_type"),
    GoldenCheck(3, "delayed_ipilimumab_alternative", "alternative", r"delayed_immunotherapy"),
    GoldenCheck(5, "multiple_regression_episodes", "episode_count", r">=2"),
    GoldenCheck(5, "irae", "irae", r"."),
    GoldenCheck(5, "mefv_germline_variant", "genotype", r"mefv\|(?:variant_present|mutated)"),
    GoldenCheck(5, "braf_finding", "genotype", r"braf\|"),
    GoldenCheck(7, "two_cases_separate", "case_count", r">=2"),
    GoldenCheck(7, "braf_v600e_wild_type", "genotype", r"braf\|wild_type"),
    GoldenCheck(7, "primary_and_nodal_coexist", "lesion_state", r"regressed|metast"),
    GoldenCheck(6, "leukoderma", "dermatologic", r"\bleukoderma\b|\bvitiligo\b"),
    GoldenCheck(6, "viable_tumor_absence", "observation", r"\bno viable|absence of (?:neoplastic|malignant)|viable"),
    GoldenCheck(6, "fibrosis_melanophages_split", "pathology_split", r"fibrosis|melanophage"),
    GoldenCheck(4, "vaccination_event", "clinical_context", r"\bvaccin"),
    GoldenCheck(4, "fever", "clinical_context", r"\bfever\b"),
    GoldenCheck(4, "causal_not_promoted", "no_causal_observation", r"vaccin"),
    GoldenCheck(2, "suv_decrease", "observation", r"\bsuv\b"),
    GoldenCheck(2, "necrosis", "observation", r"\bnecro"),
    GoldenCheck(2, "viable_cells_absent", "observation", r"\bno viable|viable"),
    GoldenCheck(1, "regressing_vs_progressing", "lesion_role", r"regress|progress"),
)


def evaluate_golden(
    session: Session, paper_id: int, run_ids: list[int]
) -> list[dict[str, str | bool]]:
    runs = list(
        session.scalars(select(ExtractionRun).where(ExtractionRun.id.in_(run_ids)))
    )
    case_ids = {run.case_id for run in runs if run.case_id is not None}
    source_ids = {
        run.source_extraction_run_id
        for run in runs
        if run.source_extraction_run_id is not None
    }
    cases = list(
        session.scalars(
            select(Case).where(
                Case.paper_id == paper_id,
                (Case.id.in_(case_ids) if case_ids else Case.extraction_run_id.in_(source_ids)),
            )
        )
    )
    observations = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.created_from_run_id.in_(run_ids)
            )
        )
    )
    genotypes = list(
        session.scalars(
            select(GenotypeObservation).where(
                GenotypeObservation.created_from_run_id.in_(run_ids)
            )
        )
    )
    alternatives = list(
        session.scalars(
            select(ExplanatoryAlternative).where(
                ExplanatoryAlternative.created_from_run_id.in_(run_ids)
            )
        )
    )
    episodes = list(
        session.scalars(
            select(RegressionEpisode).where(
                RegressionEpisode.created_from_run_id.in_(run_ids)
            )
        )
    )
    iraes = list(
        session.scalars(
            select(ImmuneRelatedAdverseEvent).where(
                ImmuneRelatedAdverseEvent.created_from_run_id.in_(run_ids)
            )
        )
    )
    lesion_states = list(
        session.scalars(
            select(LesionState).where(LesionState.created_from_run_id.in_(run_ids))
        )
    )
    results: list[dict[str, str | bool]] = []
    for check in GOLDEN_EXPECTATIONS:
        if check.paper_id != paper_id:
            continue
        passed = _matches(
            check,
            cases,
            observations,
            genotypes,
            alternatives,
            episodes,
            iraes,
            lesion_states,
        )
        results.append({"name": check.name, "kind": check.kind, "passed": passed})
    return results


def _matches(
    check: GoldenCheck,
    cases,
    observations,
    genotypes,
    alternatives,
    episodes,
    iraes,
    lesion_states,
) -> bool:
    pattern = re.compile(check.matcher, re.IGNORECASE)
    if check.kind == "immune_pathology":
        return any(
            observation.category == ObservationCategory.IMMUNE
            and observation.observation_domain
            == ObservationDomain.BIOLOGICAL_STATE.value
            and pattern.search(
                f"{observation.variable_name} {observation.value or ''}"
            )
            for observation in observations
        )
    if check.kind == "genotype":
        return any(
            pattern.search(
                f"{row.gene}|{row.state.value if hasattr(row.state, 'value') else row.state}"
            )
            for row in genotypes
        )
    if check.kind == "alternative":
        return any(pattern.search(row.alternative_type) for row in alternatives)
    if check.kind == "irae":
        return bool(iraes)
    if check.kind == "episode_count":
        return len({(row.case_id, row.episode_index) for row in episodes}) >= 2
    if check.kind == "case_count":
        identifiers = {
            re.sub(r"\s*\[run \d+\]\s*$", "", case.patient_identifier or "", flags=re.I)
            for case in cases
        }
        return len(cases) >= 2 or len(identifiers) >= 2
    if check.kind == "clinical_context":
        return any(
            observation.observation_domain
            == ObservationDomain.CLINICAL_CONTEXT.value
            and pattern.search(
                f"{observation.variable_name} {observation.value or ''}"
            )
            for observation in observations
        )
    if check.kind == "dermatologic":
        return any(
            observation.category == ObservationCategory.DERMATOLOGIC_PHENOTYPE
            or pattern.search(
                f"{observation.variable_name} {observation.value or ''}"
            )
            for observation in observations
        )
    if check.kind == "pathology_split":
        names = {
            normalize_text(observation.variable_name) for observation in observations
        }
        return "fibrosis" in names and any("melanophage" in name for name in names)
    if check.kind == "no_causal_observation":
        return not any(
            observation.observation_domain
            == ObservationDomain.TREATMENT_RESPONSE.value
            and pattern.search(
                f"{observation.variable_name} {observation.value or ''}"
            )
            for observation in observations
        )
    if check.kind == "lesion_state":
        texts = [
            " ".join(
                part
                for part in [
                    row.regression_status,
                    row.viability_status,
                    row.morphology_status,
                ]
                if part
            )
            for row in lesion_states
        ]
        return any(pattern.search(text) for text in texts) or any(
            pattern.search(f"{observation.variable_name} {observation.value or ''}")
            for observation in observations
        )
    if check.kind == "lesion_role":
        return any(
            re.search(r"regress", observation.regression_role or "", re.I)
            for observation in observations
        ) and any(
            re.search(r"progress", observation.regression_role or "", re.I)
            for observation in observations
        )
    return any(
        pattern.search(f"{observation.variable_name} {observation.value or ''}")
        for observation in observations
    )


def core_signatures_for_run(session: Session, run_id: int) -> set[tuple[str, ...]]:
    signatures: set[tuple[str, ...]] = set()
    for observation in session.scalars(
        select(BiologicalObservation).where(
            BiologicalObservation.created_from_run_id == run_id
        )
    ):
        text = normalize_text(f"{observation.variable_name} {observation.value or ''}")
        if observation.category == ObservationCategory.IMMUNE and re.search(
            r"\b(?:cd3|cd8|cd4|nk|til|macrophage|infiltrat)\b", text
        ):
            signatures.add(core_entity_signature("immune", "infiltration"))
        if observation.category == ObservationCategory.DERMATOLOGIC_PHENOTYPE:
            signatures.add(core_entity_signature("phenotype", "leukoderma"))
    for row in session.scalars(
        select(GenotypeObservation).where(GenotypeObservation.created_from_run_id == run_id)
    ):
        state = row.state.value if hasattr(row.state, "value") else row.state
        signatures.add(core_entity_signature("genotype", row.gene, state))
    for row in session.scalars(
        select(ImmuneRelatedAdverseEvent).where(
            ImmuneRelatedAdverseEvent.created_from_run_id == run_id
        )
    ):
        signatures.add(core_entity_signature("irae", row.event_type))
    for row in session.scalars(
        select(RegressionEpisode).where(RegressionEpisode.created_from_run_id == run_id)
    ):
        signatures.add(
            core_entity_signature(
                "episode",
                row.episode_type.value if hasattr(row.episode_type, "value") else row.episode_type,
                row.extent.value if hasattr(row.extent, "value") else row.extent,
            )
        )
    for row in session.scalars(
        select(ExplanatoryAlternative).where(
            ExplanatoryAlternative.created_from_run_id == run_id
        )
    ):
        signatures.add(core_entity_signature("alternative", row.alternative_type))
    for row in session.scalars(
        select(LesionState).where(LesionState.created_from_run_id == run_id)
    ):
        signatures.add(
            core_entity_signature(
                "lesion_state",
                row.regression_status,
                row.viability_status,
            )
        )
    return signatures


def golden_core_retention(
    session: Session, paper_id: int, run_groups: list[list[int]]
) -> float:
    if not run_groups:
        return 1.0
    names = None
    present: list[set[str]] = []
    for group in run_groups:
        rows = evaluate_golden(session, paper_id, group)
        if names is None:
            names = {row["name"] for row in rows}
        present.append({row["name"] for row in rows if row["passed"]})
    if not names:
        return 1.0
    kept = set.intersection(*present) if present else set()
    return len(kept) / len(names)


def stability_score(signature_sets: list[set[tuple[str, ...]]]) -> float:
    if not signature_sets:
        return 1.0
    union: set[tuple[str, ...]] = set()
    intersection = set(signature_sets[0])
    for item in signature_sets:
        union |= item
        intersection &= item
    if not union:
        return 1.0
    return len(intersection) / len(union)
