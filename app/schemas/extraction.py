from __future__ import annotations

import enum
import re
from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import (
    BiologicalDirection,
    BiologicalStatus,
    BiologicalTimeRelation,
    EventType,
    LesionScopeKind,
    MeasurementSemantics,
    ObservationCategory,
    ObservationDomain,
    PaperType,
    QualitativeLevel,
    RegressionRole,
    ScopeType,
    TemporalPrecision,
)


class FieldStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    REPORTED_ABSENT = "REPORTED_ABSENT"
    NOT_REPORTED = "NOT_REPORTED"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"


class ObservationStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    NOT_REPORTED = "NOT_REPORTED"
    NO_CHANGE = "NO_CHANGE"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"


class CaseExistence(str, enum.Enum):
    YES = "YES"
    NO = "NO"
    UNCERTAIN = "UNCERTAIN"


class SourceEvidenceType(str, enum.Enum):
    OBSERVED_FACT = "OBSERVED_FACT"
    AUTHOR_INTERPRETATION = "AUTHOR_INTERPRETATION"


class TimelineDatePrecision(str, enum.Enum):
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    RELATIVE = "RELATIVE"
    UNKNOWN = "UNKNOWN"


class RegressionRelation(str, enum.Enum):
    BEFORE = "BEFORE"
    DURING = "DURING"
    AFTER = "AFTER"
    UNKNOWN = "UNKNOWN"


class TreatmentStatusValue(str, enum.Enum):
    NO_TREATMENT = "no_treatment"
    ACTIVE_TREATMENT = "active_treatment"
    PRIOR_TREATMENT = "prior_treatment"
    TREATMENT_STOPPED = "treatment_stopped"
    TREATMENT_COMPLETED = "treatment_completed"
    UNKNOWN = "unknown"


class RegressionExtentClinical(str, enum.Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNCERTAIN = "UNCERTAIN"
    NOT_REPORTED = "NOT_REPORTED"


class ViableTumorAtPathology(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    NOT_ASSESSED = "NOT_ASSESSED"
    UNCERTAIN = "UNCERTAIN"


class StrictExtractionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceReference(StrictExtractionModel):
    page: int = Field(gt=0)
    quote: str = Field(min_length=1)
    section: str | None = None
    evidence_type: SourceEvidenceType = SourceEvidenceType.OBSERVED_FACT


ValueT = TypeVar("ValueT")


class ExtractedField(StrictExtractionModel, Generic[ValueT]):
    value: ValueT | None = None
    status: FieldStatus
    evidence_refs: list[EvidenceReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_reported_value(self) -> "ExtractedField[ValueT]":
        if self.status == FieldStatus.REPORTED:
            if self.value is None:
                raise ValueError("REPORTED fields require a value")
            if not self.evidence_refs:
                raise ValueError("REPORTED fields require source evidence")
        if self.status == FieldStatus.REPORTED_ABSENT:
            if self.value is not None:
                raise ValueError("REPORTED_ABSENT fields must have a null value")
            if not self.evidence_refs:
                raise ValueError("REPORTED_ABSENT fields require source evidence")
        if self.status == FieldStatus.NOT_REPORTED:
            if self.value is not None:
                raise ValueError("NOT_REPORTED fields cannot contain a value")
            if self.evidence_refs:
                raise ValueError("NOT_REPORTED fields cannot claim source evidence")
        if self.status == FieldStatus.CONFLICTING and len(self.evidence_refs) < 2:
            raise ValueError("CONFLICTING fields require at least two evidence references")
        return self


class PaperMetadataCandidate(StrictExtractionModel):
    title: ExtractedField[str]
    authors: ExtractedField[list[str]]
    year: ExtractedField[int]
    journal: ExtractedField[str]
    doi: ExtractedField[str]
    pmid: ExtractedField[str]
    abstract: ExtractedField[str]
    paper_type: ExtractedField[PaperType]


class CaseDetectionResult(StrictExtractionModel):
    existence: CaseExistence
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[EvidenceReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_yes_evidence(self) -> "CaseDetectionResult":
        if self.existence == CaseExistence.YES and not self.evidence_refs:
            raise ValueError("YES case detection requires source evidence")
        return self


class CaseCandidate(StrictExtractionModel):
    patient_identifier: ExtractedField[str]
    age: ExtractedField[int]
    sex: ExtractedField[str]
    melanoma_subtype: ExtractedField[str]
    primary_site: ExtractedField[str]
    stage: ExtractedField[str]
    metastatic_sites: ExtractedField[list[str]]
    diagnosis_date: ExtractedField[str]
    regression_start_date: ExtractedField[str]
    first_observed_reduction: ExtractedField[str]
    regression_confirmed_date: ExtractedField[str]
    regression_duration: ExtractedField[str]
    regression_type: ExtractedField[str]
    regression_extent_clinical: ExtractedField[RegressionExtentClinical]
    viable_tumor_at_pathology: ExtractedField[ViableTumorAtPathology]
    treatment_before_regression: ExtractedField[str]
    treatment_status: ExtractedField[TreatmentStatusValue]
    preceding_events: ExtractedField[list[str]]
    outcome: ExtractedField[str]
    follow_up_duration: ExtractedField[str]
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def separate_procedures_from_treatment_history(self) -> "CaseCandidate":
        for field_name in self.__class__.model_fields:
            if field_name in {"confidence", "primary_site"}:
                continue
            field = getattr(self, field_name)
            if isinstance(field, ExtractedField) and (
                field.status == FieldStatus.REPORTED_ABSENT
            ):
                raise ValueError(
                    "REPORTED_ABSENT is currently valid only for primary_site"
                )

        extent = self.regression_extent_clinical
        if extent.status == FieldStatus.UNCERTAIN:
            if extent.value != RegressionExtentClinical.UNCERTAIN:
                raise ValueError(
                    "UNCERTAIN clinical extent must use value UNCERTAIN"
                )
            if not extent.evidence_refs:
                raise ValueError("UNCERTAIN clinical extent requires evidence")
        if extent.status == FieldStatus.REPORTED and extent.value not in {
            RegressionExtentClinical.COMPLETE,
            RegressionExtentClinical.PARTIAL,
        }:
            raise ValueError("Reported clinical extent must be COMPLETE or PARTIAL")
        if extent.status == FieldStatus.REPORTED:
            extent_source = " ".join(
                reference.quote for reference in extent.evidence_refs
            )
            explicit_extent = {
                RegressionExtentClinical.COMPLETE: re.compile(
                    r"\bcomplete(?: clinical)? regression\b|"
                    r"\bcompletely regress\w*\b|\bcomplete disappearance\b|"
                    r"\bno evidence of disease\b",
                    re.IGNORECASE,
                ),
                RegressionExtentClinical.PARTIAL: re.compile(
                    r"\bpartial(?: clinical)? regression\b|"
                    r"\bpartially regress\w*\b",
                    re.IGNORECASE,
                ),
            }
            if not explicit_extent[extent.value].search(extent_source):
                raise ValueError(
                    "COMPLETE or PARTIAL clinical extent requires explicit "
                    "clinical extent wording"
                )

        viability = self.viable_tumor_at_pathology
        if viability.status == FieldStatus.UNCERTAIN:
            if viability.value != ViableTumorAtPathology.UNCERTAIN:
                raise ValueError("UNCERTAIN pathology viability must use UNCERTAIN")
            if not viability.evidence_refs:
                raise ValueError("UNCERTAIN pathology viability requires evidence")
        if viability.status == FieldStatus.REPORTED and viability.value is None:
            raise ValueError("Reported pathology viability requires a value")
        if (
            viability.status == FieldStatus.REPORTED
            and viability.value == ViableTumorAtPathology.ABSENT
            and extent.status == FieldStatus.NOT_REPORTED
        ):
            uncertainty_refs = [
                *self.first_observed_reduction.evidence_refs,
                *viability.evidence_refs,
            ]
            self.regression_extent_clinical = ExtractedField[
                RegressionExtentClinical
            ](
                value=RegressionExtentClinical.UNCERTAIN,
                status=FieldStatus.UNCERTAIN,
                evidence_refs=uncertainty_refs,
            )

        regression_start = self.regression_start_date
        if (
            regression_start.status == FieldStatus.REPORTED
            and isinstance(regression_start.value, str)
        ):
            try:
                date.fromisoformat(regression_start.value)
                explicit_start = True
            except ValueError:
                source_text = " ".join(
                    reference.quote for reference in regression_start.evidence_refs
                )
                explicit_start = bool(
                    re.search(
                        r"\b(regress\w*|decreas\w*|shrink\w*)\b.{0,80}"
                        r"\b(began|begun|started|onset|first (?:noted|observed|"
                        r"detected|seen))\b|"
                        r"\b(began|begun|started|onset|first (?:noted|observed|"
                        r"detected|seen))\b.{0,80}"
                        r"\b(regress\w*|decreas\w*|shrink\w*)\b",
                        source_text,
                        re.IGNORECASE,
                    )
                )
            if not explicit_start:
                raise ValueError(
                    "regression_start_date requires an explicit onset statement; "
                    "sequence phrases such as 'following biopsy' are insufficient"
                )

        field = self.treatment_before_regression
        if field.status != FieldStatus.REPORTED or not isinstance(field.value, str):
            return self
        normalized = field.value.casefold()
        procedure_only = re.search(
            r"\b(biopsy|surgery|resection|hospitali[sz]ation)\b", normalized
        )
        oncologic_treatment = re.search(
            r"\b(ipilimumab|chemotherap|radiotherap|immunotherap|"
            r"systemic therap|targeted therap|drug|medication)\b",
            normalized,
        )
        if procedure_only and not oncologic_treatment:
            raise ValueError(
                "treatment_before_regression cannot contain only a biopsy, surgery, "
                "resection, or hospitalization; represent it as an Event"
            )
        return self


class CaseExtractionResult(StrictExtractionModel):
    cases: list[CaseCandidate] = Field(default_factory=list)


class TimelineEventCandidate(StrictExtractionModel):
    event_type: EventType
    description: str = Field(min_length=1)
    event_date: str | None = None
    relative_time: str | None = None
    date_precision: TimelineDatePrecision
    relation_to_regression: RegressionRelation = RegressionRelation.UNKNOWN
    temporal_order_confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[EvidenceReference] = Field(min_length=1)

    @model_validator(mode="after")
    def preserve_temporal_source(self) -> "TimelineEventCandidate":
        if self.date_precision == TimelineDatePrecision.RELATIVE and not self.relative_time:
            raise ValueError("RELATIVE events require the original relative_time phrase")
        if self.date_precision == TimelineDatePrecision.EXACT and not self.event_date:
            raise ValueError("EXACT events require event_date")
        if self.date_precision == TimelineDatePrecision.EXACT and self.event_date:
            try:
                date.fromisoformat(self.event_date)
            except ValueError as exc:
                raise ValueError("EXACT event_date must use ISO YYYY-MM-DD") from exc
        return self


class TimelineExtractionResult(StrictExtractionModel):
    events: list[TimelineEventCandidate] = Field(default_factory=list)


class BiologicalObservationCandidate(StrictExtractionModel):
    category: ObservationCategory
    observation_domain: ObservationDomain = ObservationDomain.BIOLOGICAL_STATE
    domain_secondary: ObservationDomain | None = None
    measurement_semantics: MeasurementSemantics = MeasurementSemantics.UNKNOWN
    variable_name: str = Field(min_length=1)
    normalized_variable: str | None = None
    value: str | None = None
    normalized_value: str | float | int | list[str | float | int] | None = None
    unit: str | None = None
    direction: BiologicalDirection = BiologicalDirection.UNKNOWN
    status: BiologicalStatus
    time_relation: BiologicalTimeRelation = BiologicalTimeRelation.UNKNOWN
    temporal_precision: TemporalPrecision = TemporalPrecision.UNKNOWN
    scope_type: ScopeType = ScopeType.PATIENT
    lesion_identifier: str | None = None
    lesion_scope_kind: LesionScopeKind = LesionScopeKind.UNKNOWN
    lesion_collection_identifier: str | None = None
    regression_role: RegressionRole = RegressionRole.UNKNOWN
    qualitative_level: QualitativeLevel = QualitativeLevel.UNKNOWN
    temporal_text: str | None = None
    temporal_value: float | None = None
    temporal_unit: str | None = None
    temporal_relation: str | None = None
    anchor_event_description: str | None = None
    observation_context: str | None = None
    related_event_description: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_refs: list[EvidenceReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_observation_evidence(self) -> "BiologicalObservationCandidate":
        if self.status in {
            BiologicalStatus.REPORTED,
            BiologicalStatus.REPORTED_ABSENT,
            BiologicalStatus.UNCERTAIN,
        } and not self.evidence_refs:
            raise ValueError(f"{self.status.value} observations require evidence")
        if (
            self.status == BiologicalStatus.CONFLICTING
            and len(self.evidence_refs) < 2
        ):
            raise ValueError("CONFLICTING observations require at least two sources")
        if self.status == BiologicalStatus.REPORTED_ABSENT:
            if self.direction != BiologicalDirection.ABSENT:
                raise ValueError("REPORTED_ABSENT requires direction ABSENT")
        if self.status == BiologicalStatus.NOT_REPORTED:
            if (
                self.value is not None
                or self.normalized_value is not None
                or self.evidence_refs
            ):
                raise ValueError("NOT_REPORTED cannot contain a value or evidence")
        if self.temporal_precision == TemporalPrecision.EXACT:
            temporal_source = " ".join(
                [
                    self.value or "",
                    self.observation_context or "",
                    *(reference.quote for reference in self.evidence_refs),
                ]
            )
            calendar_date = re.search(
                r"\b\d{4}-\d{2}-\d{2}\b|"
                r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
                r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|"
                r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
                r"\s+\d{1,2},?\s+\d{4}\b",
                temporal_source,
                re.IGNORECASE,
            )
            if not calendar_date:
                relative_duration = re.search(
                    r"\b\d+\s*(?:day|week|month|year)s?\b|"
                    r"\b(?:initial|baseline|follow-up|post-operative|"
                    r"before|after|during|later)\b",
                    temporal_source,
                    re.IGNORECASE,
                )
                self.temporal_precision = (
                    TemporalPrecision.RELATIVE
                    if relative_duration
                    else TemporalPrecision.UNKNOWN
                )
        if self.regression_role != RegressionRole.UNKNOWN:
            if self.scope_type not in {ScopeType.LESION, ScopeType.LYMPH_NODE}:
                raise ValueError(
                    "A known regression_role requires LESION or LYMPH_NODE scope"
                )
            if not self.lesion_identifier:
                raise ValueError(
                    "A known lesion regression_role requires lesion_identifier"
                )

        measurement_text = " ".join(
            [
                self.variable_name,
                self.normalized_variable or "",
                self.value or "",
                *(reference.quote for reference in self.evidence_refs),
            ]
        )
        imaging_measurement = (
            self.measurement_semantics == MeasurementSemantics.IMAGING_PROXY
            and re.search(r"\b(fdg|suv|uptake)\b", measurement_text, re.IGNORECASE)
        )
        numeric_pair = (
            isinstance(self.normalized_value, list)
            and len(self.normalized_value) >= 2
        )
        explicit_imaging_change = bool(
            re.search(
                r"\b(?:suv|fdg uptake|uptake)\b.{0,30}"
                r"\b(?:increased|decreased|reduced|fell|rose)\b|"
                r"\b(?:reduction|increase|decrease)\s+in\s+"
                r"(?:fdg(?: uptake)?|suv|uptake)\b|"
                r"\bfrom\s+\d+(?:\.\d+)?\s+to\s+\d+(?:\.\d+)?\b",
                measurement_text,
                re.IGNORECASE,
            )
        )
        if imaging_measurement and not (numeric_pair or explicit_imaging_change):
            self.direction = BiologicalDirection.UNKNOWN
        static_numeric_range = re.search(
            r"\b(?:measur\w*|ranged|ranging|range)\b.{0,40}"
            r"\d+(?:\.\d+)?\s*(?:mm|cm)?\s*(?:[-\u2013\u2014]|to)\s*"
            r"\d+(?:\.\d+)?\s*(?:mm|cm)?\b|"
            r"\b\d+(?:\.\d+)?\s*[-\u2013\u2014]\s*"
            r"\d+(?:\.\d+)?\s*(?:mm|cm)\b",
            measurement_text,
            re.IGNORECASE,
        )
        explicit_baseline_comparison = re.search(
            r"\b(?:decreas\w*|reduc\w*|fell|shrank|increas\w*|rose|grew)\b"
            r".{0,80}\b(?:from|to|compared with|versus|baseline|previous)\b",
            measurement_text,
            re.IGNORECASE,
        )
        if static_numeric_range and not explicit_baseline_comparison:
            self.direction = BiologicalDirection.UNKNOWN
        if (
            self.qualitative_level == QualitativeLevel.NORMAL
            and re.search(
                r"\b(?:complete blood count|cbc)\b",
                measurement_text,
                re.IGNORECASE,
            )
        ):
            self.direction = BiologicalDirection.UNKNOWN
        return self


class RejectedInterpretationCandidate(StrictExtractionModel):
    statement: str = Field(min_length=1)
    rejection_reason: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[EvidenceReference] = Field(min_length=1)

    @model_validator(mode="after")
    def require_interpretation_evidence(self) -> "RejectedInterpretationCandidate":
        if any(
            reference.evidence_type != SourceEvidenceType.AUTHOR_INTERPRETATION
            for reference in self.evidence_refs
        ):
            raise ValueError(
                "Rejected interpretations must declare AUTHOR_INTERPRETATION evidence"
            )
        return self


class BiologicalObservationExtractionResult(StrictExtractionModel):
    observations: list[BiologicalObservationCandidate] = Field(default_factory=list)
    rejected_interpretations: list[RejectedInterpretationCandidate] = Field(
        default_factory=list
    )
