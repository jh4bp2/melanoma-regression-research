from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import (
    AnalysisStatus,
    BiologicalDirection,
    BiologicalStatus,
    BiologicalTimeRelation,
    DatePrecision,
    EventType,
    EvidenceStatus,
    EvidenceType,
    ExplanatoryAlternativeStatus,
    ExtractionStatus,
    GenotypeState,
    LesionAliasStatus,
    LesionScopeKind,
    MeasurementSemantics,
    ObservationCategory,
    ObservationDomain,
    PaperType,
    QualitativeLevel,
    RegressionRole,
    ScopeType,
    SupportType,
    TemporalSemanticPrecision,
    TemporalPrecision,
)


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaperRead(OrmModel):
    id: int
    title: str | None
    authors: list[str]
    year: int | None
    journal: str | None
    doi: str | None
    pmid: str | None
    source_url: str | None
    abstract: str | None
    full_text_path: str
    extracted_text_path: str
    paper_type: PaperType
    analysis_status: AnalysisStatus
    content_sha256: str
    page_count: int
    created_at: datetime


class IngestRequest(BaseModel):
    filename: str = Field(min_length=1, description="PDF filename inside data/papers")


class CaseCreate(BaseModel):
    paper_id: int
    patient_identifier: str = Field(min_length=1, max_length=255)
    age: int | None = Field(default=None, ge=0)
    sex: str | None = None
    melanoma_subtype: str | None = None
    primary_site: str | None = None
    primary_site_status: str | None = None
    stage: str | None = None
    metastatic_sites: list[str] = Field(default_factory=list)
    diagnosis_date: date | None = None
    regression_start_date: date | None = None
    first_observed_reduction: str | None = None
    regression_confirmed_date: date | None = None
    regression_duration: str | None = None
    regression_type: str | None = None
    partial_or_complete: str | None = None
    regression_extent_clinical: str | None = None
    viable_tumor_at_pathology: str | None = None
    treatment_before_regression: str | None = None
    treatment_status: str | None = None
    preceding_event: str | None = None
    outcome: str | None = None
    follow_up_duration: str | None = None
    notes: str | None = None


class CaseRead(CaseCreate, OrmModel):
    id: int
    extraction_confidence: float | None = None
    field_statuses: dict | None = None
    extraction_run_id: int | None = None


class EventCreate(BaseModel):
    case_id: int
    event_date: date | None = None
    date_precision: DatePrecision = DatePrecision.UNKNOWN
    relative_day: int | None = None
    relative_time: str | None = None
    source_date_precision: str | None = None
    relation_to_regression: str | None = None
    temporal_order_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    temporal_value: float | None = None
    temporal_unit: str | None = None
    temporal_relation: str | None = None
    temporal_precision: str | None = None
    anchor_event_id: int | None = None
    extraction_run_id: int | None = None
    event_type: EventType
    description: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_temporal_anchor(self) -> "EventCreate":
        if (
            self.date_precision != DatePrecision.UNKNOWN
            and self.event_date is None
            and self.relative_day is None
            and self.relative_time is None
        ):
            raise ValueError("Exact or approximate events require a date or relative_day")
        return self


class EventRead(EventCreate, OrmModel):
    id: int

    @model_validator(mode="after")
    def expose_source_precision(self) -> "EventRead":
        if self.source_date_precision:
            self.date_precision = DatePrecision(self.source_date_precision.lower())
        return self


class EvidenceCreate(BaseModel):
    paper_id: int
    case_id: int | None = None
    evidence_type: EvidenceType
    claim: str = Field(min_length=1)
    source_quote: str | None = None
    page: int | None = Field(default=None, gt=0)
    section: str | None = None
    paragraph: int | None = Field(default=None, gt=0)
    confidence: float = Field(ge=0.0, le=1.0)
    support_type: SupportType = SupportType.NEUTRAL
    status: EvidenceStatus = EvidenceStatus.SUPPORTED

    @model_validator(mode="after")
    def validate_provenance(self) -> "EvidenceCreate":
        if self.status == EvidenceStatus.SUPPORTED:
            if not self.source_quote or not self.source_quote.strip():
                raise ValueError("Supported evidence requires a non-empty source_quote")
            if self.page is None and not (self.section and self.section.strip()):
                raise ValueError("Supported evidence requires a page or section locator")
        if (
            self.evidence_type == EvidenceType.SYSTEM_INFERENCE
            and self.status == EvidenceStatus.SUPPORTED
        ):
            raise ValueError(
                "SYSTEM_INFERENCE cannot be supported until linked-evidence validation "
                "is implemented"
            )
        return self


class EvidenceRead(EvidenceCreate, OrmModel):
    id: int


class FieldEvidenceRead(BaseModel):
    field_name: str
    evidence: EvidenceRead


class CaseDetailRead(BaseModel):
    case: CaseRead
    evidence: list[FieldEvidenceRead]


class TimelineEventDetailRead(BaseModel):
    event: EventRead
    evidence: list[FieldEvidenceRead]


class BiologicalObservationRead(OrmModel):
    id: int
    paper_id: int
    case_id: int
    category: ObservationCategory
    variable_name: str
    normalized_variable: str | None
    value: str | None
    normalized_value: Any | None
    unit: str | None
    direction: BiologicalDirection
    status: BiologicalStatus
    time_relation: BiologicalTimeRelation
    temporal_precision: TemporalPrecision
    observation_domain: ObservationDomain
    domain_secondary: ObservationDomain | None
    measurement_semantics: MeasurementSemantics
    scope_type: ScopeType
    lesion_identifier: str | None
    lesion_id: int | None
    lesion_collection_id: int | None
    regression_role: RegressionRole
    qualitative_level: QualitativeLevel
    temporal_text: str | None
    temporal_value: float | None
    temporal_unit: str | None
    temporal_relation: str | None
    anchor_event_id: int | None
    observation_context: str | None
    evidence_type: EvidenceType
    confidence: float
    linked_event_id: int | None
    created_from_run_id: int
    created_at: datetime | None


class BiologicalObservationDetailRead(BaseModel):
    observation: BiologicalObservationRead
    evidence: list[FieldEvidenceRead]


class LesionAliasRead(OrmModel):
    id: int
    lesion_id: int
    possible_same_lesion_id: int | None
    source_text: str
    paper_id: int
    page: int | None
    section: str | None
    status: LesionAliasStatus
    evidence_id: int | None


class LesionRead(OrmModel):
    id: int
    paper_id: int
    case_id: int
    canonical_name: str
    organ: str | None
    anatomical_location: str | None
    laterality: str | None
    lesion_type: str | None
    identity_key: str
    created_from_run_id: int | None
    aliases: list[LesionAliasRead] = Field(default_factory=list)


class LesionCollectionRead(OrmModel):
    id: int
    paper_id: int
    case_id: int
    canonical_name: str
    collection_type: LesionScopeKind
    organ: str | None
    anatomical_location: str | None
    source_text: str | None
    created_from_run_id: int | None


class TemporalRecordRead(OrmModel):
    id: int
    paper_id: int
    case_id: int
    entity_type: str
    entity_id: int
    field_name: str
    temporal_text: str
    temporal_value: float | None
    temporal_unit: str | None
    temporal_relation: str | None
    temporal_precision: TemporalSemanticPrecision
    anchor_event_id: int | None
    evidence_id: int | None
    created_from_run_id: int | None


class GenotypeObservationRead(OrmModel):
    id: int
    paper_id: int
    case_id: int
    biological_observation_id: int | None
    gene: str
    variant: str | None
    state: GenotypeState
    evidence_id: int
    created_from_run_id: int | None


class ExplanatoryAlternativeRead(OrmModel):
    id: int
    paper_id: int
    case_id: int
    alternative_type: str
    description: str
    temporal_relation: str | None
    status: ExplanatoryAlternativeStatus
    evidence_id: int
    created_from_run_id: int | None


class ExtractionRunRead(OrmModel):
    id: int
    paper_id: int
    case_id: int | None = None
    source_extraction_run_id: int | None = None
    run_type: str | None = None
    model: str
    prompt_version: str
    status: ExtractionStatus
    retry_count: int
    started_at: datetime
    finished_at: datetime | None
    error: str | None
    reason_codes: list[str] | None = None
    schema_version: str | None = None
    rule_version: str | None = None
