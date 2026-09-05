from __future__ import annotations

import re
from copy import deepcopy

from app.models import (
    BiologicalDirection,
    BiologicalStatus,
    MeasurementSemantics,
    ObservationCategory,
    ObservationDomain,
    RegressionRole,
    ScopeType,
)
from app.schemas.extraction import BiologicalObservationCandidate
from app.services.evidence_verifier import normalize_text


FINDINGS = (
    (
        r"\bno viable (?:malignant |tumor |neoplastic )?cells?\b|"
        r"\babsence of (?:neoplastic|malignant) cells\b",
        "viable malignant cells",
        "ABSENT",
        ObservationDomain.BIOLOGICAL_STATE,
        ObservationCategory.PATHOLOGIC,
        MeasurementSemantics.PATHOLOGIC_FINDING,
        "VIABLE_TUMOR_CELLS",
    ),
    (
        r"\bfibrosis\b",
        "fibrosis",
        "PRESENT",
        ObservationDomain.DIAGNOSTIC_EVIDENCE,
        ObservationCategory.PATHOLOGIC,
        MeasurementSemantics.PATHOLOGIC_FINDING,
        "FIBROSIS",
    ),
    (
        r"\bmelanophages?\b",
        "melanophages",
        "PRESENT",
        ObservationDomain.DIAGNOSTIC_EVIDENCE,
        ObservationCategory.PATHOLOGIC,
        MeasurementSemantics.PATHOLOGIC_FINDING,
        "MELANOPHAGES",
    ),
    (
        r"\bleukoderma\b|\bvitiligo(?:-like)?\b",
        "leukoderma",
        "PRESENT",
        ObservationDomain.CLINICAL_CONTEXT,
        ObservationCategory.DERMATOLOGIC_PHENOTYPE,
        MeasurementSemantics.CLINICAL_FINDING,
        "LEUKODERMA",
    ),
    (
        r"\blymphocyt\w* infiltrat",
        "lymphocytic infiltration",
        "PRESENT",
        ObservationDomain.BIOLOGICAL_STATE,
        ObservationCategory.IMMUNE,
        MeasurementSemantics.PATHOLOGIC_FINDING,
        "LYMPHOCYTIC_INFILTRATION",
    ),
    (
        r"\bnecros",
        "necrosis",
        "PRESENT",
        ObservationDomain.BIOLOGICAL_STATE,
        ObservationCategory.PATHOLOGIC,
        MeasurementSemantics.PATHOLOGIC_FINDING,
        "TUMOR_NECROSIS",
    ),
)


def split_pathology_observations(
    candidates: list[BiologicalObservationCandidate],
) -> list[BiologicalObservationCandidate]:
    expanded: list[BiologicalObservationCandidate] = []
    for candidate in candidates:
        text = normalize_text(
            " ".join(
                [
                    candidate.variable_name,
                    candidate.value or "",
                    *(reference.quote for reference in candidate.evidence_refs),
                ]
            )
        )
        matches = [
            finding for finding in FINDINGS if re.search(finding[0], text, re.IGNORECASE)
        ]
        if len(matches) < 2:
            expanded.append(candidate)
            continue
        used_names: set[str] = set()
        for (
            _pattern,
            label,
            direction,
            domain,
            category,
            semantics,
            normalized,
        ) in matches:
            if label in used_names:
                continue
            used_names.add(label)
            clone = candidate.model_copy(deep=True)
            clone.variable_name = label
            clone.normalized_variable = normalized
            clone.value = label if direction == "PRESENT" else "absent"
            clone.direction = (
                BiologicalDirection.ABSENT
                if direction == "ABSENT"
                else BiologicalDirection.PRESENT
            )
            clone.observation_domain = domain
            clone.category = category
            clone.measurement_semantics = semantics
            clone.status = BiologicalStatus.REPORTED
            if category == ObservationCategory.IMMUNE:
                clone.domain_secondary = ObservationDomain.DIAGNOSTIC_EVIDENCE
            if category == ObservationCategory.DERMATOLOGIC_PHENOTYPE:
                clone.scope_type = (
                    ScopeType.LESION
                    if candidate.lesion_identifier
                    else ScopeType.PATIENT
                )
                if (
                    clone.regression_role != RegressionRole.UNKNOWN
                    and not clone.lesion_identifier
                ):
                    clone.regression_role = RegressionRole.UNKNOWN
            expanded.append(clone)
    return expanded


def deepcopy_candidates(candidates: list[BiologicalObservationCandidate]):
    return [deepcopy(row) for row in candidates]
