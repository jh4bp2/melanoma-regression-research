from __future__ import annotations

import enum
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaperType(str, enum.Enum):
    CASE_REPORT = "case_report"
    CASE_SERIES = "case_series"
    REVIEW = "review"
    MECHANISTIC_STUDY = "mechanistic_study"
    CLINICAL_STUDY = "clinical_study"
    OTHER = "other"


class AnalysisStatus(str, enum.Enum):
    INGESTED = "ingested"
    EXTRACTION_PENDING = "extraction_pending"
    EXTRACTION_RUNNING = "extraction_running"
    EXTRACTED = "extracted"
    PARTIAL = "partial"
    FAILED = "failed"


class DatePrecision(str, enum.Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    RELATIVE = "relative"
    UNKNOWN = "unknown"


class EventType(str, enum.Enum):
    INFECTION = "infection"
    FEVER = "fever"
    SURGERY = "surgery"
    BIOPSY = "biopsy"
    TRAUMA = "trauma"
    VACCINATION = "vaccination"
    DRUG_EXPOSURE = "drug_exposure"
    IMMUNE_ACTIVATION = "immune_activation"
    TREATMENT = "treatment"
    TUMOR_PROGRESSION = "tumor_progression"
    TUMOR_REGRESSION = "tumor_regression"
    DIAGNOSIS = "diagnosis"
    METASTASIS = "metastasis"
    HOSPITALIZATION = "hospitalization"
    OTHER = "other"


class EvidenceType(str, enum.Enum):
    OBSERVED_FACT = "OBSERVED_FACT"
    AUTHOR_INTERPRETATION = "AUTHOR_INTERPRETATION"
    SYSTEM_INFERENCE = "SYSTEM_INFERENCE"


class SupportType(str, enum.Enum):
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    NEUTRAL = "neutral"


class EvidenceStatus(str, enum.Enum):
    SUPPORTED = "SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    UNSUPPORTED = "UNSUPPORTED"


class ExtractionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class PartialReasonCode(str, enum.Enum):
    UNVERIFIED_QUOTE = "PARTIAL_UNVERIFIED_QUOTE"
    FIELD_WITHOUT_EVIDENCE = "PARTIAL_FIELD_WITHOUT_EVIDENCE"
    TEMPORAL_UNCERTAINTY = "PARTIAL_TEMPORAL_UNCERTAINTY"
    SCHEMA_RECOVERY = "PARTIAL_SCHEMA_RECOVERY"
    FIELD_SEMANTIC_VIOLATION = "PARTIAL_FIELD_SEMANTIC_VIOLATION"
    CASE_EXISTENCE_UNCERTAIN = "PARTIAL_CASE_EXISTENCE_UNCERTAIN"
    CASE_SCOPE_UNCERTAIN = "PARTIAL_CASE_SCOPE_UNCERTAIN"
    RECONCILIATION_REQUIRED = "PARTIAL_RECONCILIATION_REQUIRED"


class ObservationCategory(str, enum.Enum):
    IMMUNE = "IMMUNE"
    INFLAMMATORY = "INFLAMMATORY"
    METABOLIC = "METABOLIC"
    VASCULAR = "VASCULAR"
    ENDOCRINE = "ENDOCRINE"
    NEURAL = "NEURAL"
    MICROBIOME = "MICROBIOME"
    TUMOR_MICROENVIRONMENT = "TUMOR_MICROENVIRONMENT"
    GENETIC = "GENETIC"
    PATHOLOGIC = "PATHOLOGIC"
    DERMATOLOGIC_PHENOTYPE = "DERMATOLOGIC_PHENOTYPE"
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            normalized = value.upper()
            return next(
                (member for member in cls if member.value == normalized),
                None,
            )
        return None


class BiologicalStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    REPORTED_ABSENT = "REPORTED_ABSENT"
    NOT_REPORTED = "NOT_REPORTED"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"


class BiologicalDirection(str, enum.Enum):
    INCREASED = "INCREASED"
    DECREASED = "DECREASED"
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNCHANGED = "UNCHANGED"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class BiologicalTimeRelation(str, enum.Enum):
    BEFORE_REGRESSION = "BEFORE_REGRESSION"
    DURING_REGRESSION = "DURING_REGRESSION"
    AFTER_REGRESSION = "AFTER_REGRESSION"
    AT_CONFIRMATION = "AT_CONFIRMATION"
    LONG_TERM_FOLLOWUP = "LONG_TERM_FOLLOWUP"
    UNKNOWN = "UNKNOWN"


class TemporalPrecision(str, enum.Enum):
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    RELATIVE = "RELATIVE"
    UNKNOWN = "UNKNOWN"


class ObservationDomain(str, enum.Enum):
    BIOLOGICAL_STATE = "BIOLOGICAL_STATE"
    DISEASE_PHENOTYPE = "DISEASE_PHENOTYPE"
    DIAGNOSTIC_EVIDENCE = "DIAGNOSTIC_EVIDENCE"
    CLINICAL_CONTEXT = "CLINICAL_CONTEXT"
    TREATMENT_RESPONSE = "TREATMENT_RESPONSE"


class MeasurementSemantics(str, enum.Enum):
    DIRECT_MEASUREMENT = "DIRECT_MEASUREMENT"
    IMAGING_PROXY = "IMAGING_PROXY"
    PATHOLOGIC_FINDING = "PATHOLOGIC_FINDING"
    LAB_MEASUREMENT = "LAB_MEASUREMENT"
    MORPHOLOGIC_FINDING = "MORPHOLOGIC_FINDING"
    SYMPTOM = "SYMPTOM"
    CLINICAL_FINDING = "CLINICAL_FINDING"
    UNKNOWN = "UNKNOWN"


class ScopeType(str, enum.Enum):
    PATIENT = "PATIENT"
    SYSTEMIC = "SYSTEMIC"
    LESION = "LESION"
    LYMPH_NODE = "LYMPH_NODE"
    OTHER = "OTHER"


class RegressionRole(str, enum.Enum):
    REGRESSING_TARGET = "REGRESSING_TARGET"
    PROGRESSING_NON_TARGET = "PROGRESSING_NON_TARGET"
    STABLE_NON_TARGET = "STABLE_NON_TARGET"
    UNKNOWN = "UNKNOWN"


class QualitativeLevel(str, enum.Enum):
    LOW = "LOW"
    MINIMAL = "MINIMAL"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    MARKED = "MARKED"
    UNKNOWN = "UNKNOWN"


class LesionScopeKind(str, enum.Enum):
    SINGLE_LESION = "SINGLE_LESION"
    LESION_COLLECTION = "LESION_COLLECTION"
    MULTIFOCAL_DISEASE = "MULTIFOCAL_DISEASE"
    METASTATIC_LESION_GROUP = "METASTATIC_LESION_GROUP"
    MELANOCYTIC_NEVI_GROUP = "MELANOCYTIC_NEVI_GROUP"
    UNKNOWN = "UNKNOWN"


class CollectionCountSemantics(str, enum.Enum):
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    MULTIPLE_UNSPECIFIED = "MULTIPLE_UNSPECIFIED"
    UNKNOWN = "UNKNOWN"


class CollectionMembershipStatus(str, enum.Enum):
    INDIVIDUAL_MEMBERS_KNOWN = "INDIVIDUAL_MEMBERS_KNOWN"
    PARTIAL_MEMBERS_KNOWN = "PARTIAL_MEMBERS_KNOWN"
    COLLECTION_ONLY = "COLLECTION_ONLY"


class LesionAliasStatus(str, enum.Enum):
    CONFIRMED_ALIAS = "CONFIRMED_ALIAS"
    POSSIBLE_SAME_LESION = "POSSIBLE_SAME_LESION"


class TemporalSemanticPrecision(str, enum.Enum):
    EXACT_DATE = "EXACT_DATE"
    APPROXIMATE_DATE = "APPROXIMATE_DATE"
    RELATIVE_TIME = "RELATIVE_TIME"
    INTERVAL = "INTERVAL"
    UNKNOWN = "UNKNOWN"


class GenotypeState(str, enum.Enum):
    WILD_TYPE = "WILD_TYPE"
    MUTATED = "MUTATED"
    VARIANT_PRESENT = "VARIANT_PRESENT"
    AMPLIFIED = "AMPLIFIED"
    DELETED = "DELETED"
    NOT_DETECTED = "NOT_DETECTED"
    UNKNOWN = "UNKNOWN"


class GenotypeOrigin(str, enum.Enum):
    GERMLINE = "GERMLINE"
    SOMATIC = "SOMATIC"
    UNKNOWN = "UNKNOWN"


class GenotypeVariantType(str, enum.Enum):
    SNV = "SNV"
    INDEL = "INDEL"
    DELETION = "DELETION"
    CYTOGENETIC = "CYTOGENETIC"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class QuoteVerificationStatus(str, enum.Enum):
    VERIFIED_EXACT = "VERIFIED_EXACT"
    VERIFIED_NORMALIZED = "VERIFIED_NORMALIZED"
    UNVERIFIED = "UNVERIFIED"


class CaseScopeStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    SHARED_BOTH = "SHARED_BOTH"
    CASE_SCOPE_UNCERTAIN = "CASE_SCOPE_UNCERTAIN"


class ClinicalContextSubtype(str, enum.Enum):
    IRAE = "IRAE"
    INFECTION = "INFECTION"
    FEVER = "FEVER"
    VACCINE = "VACCINE"
    DERMATOLOGIC_PHENOTYPE = "DERMATOLOGIC_PHENOTYPE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class RegressionEpisodeType(str, enum.Enum):
    SPONTANEOUS = "SPONTANEOUS"
    TREATMENT_ASSOCIATED = "TREATMENT_ASSOCIATED"
    UNCERTAIN = "UNCERTAIN"
    OTHER = "OTHER"


class RegressionExtent(str, enum.Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MIXED = "MIXED"
    UNCERTAIN = "UNCERTAIN"


class ExplanatoryAlternativeStatus(str, enum.Enum):
    POSSIBLE = "POSSIBLE"
    PLAUSIBLE = "PLAUSIBLE"
    AUTHOR_SUGGESTED = "AUTHOR_SUGGESTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    authors: Mapped[list[str]] = mapped_column(JSON, default=list)
    year: Mapped[int | None] = mapped_column(Integer)
    journal: Mapped[str | None] = mapped_column(String(500))
    doi: Mapped[str | None] = mapped_column(String(255), unique=True)
    pmid: Mapped[str | None] = mapped_column(String(32), unique=True)
    source_url: Mapped[str | None] = mapped_column(Text)
    abstract: Mapped[str | None] = mapped_column(Text)
    full_text_path: Mapped[str] = mapped_column(Text)
    extracted_text_path: Mapped[str] = mapped_column(Text)
    paper_type: Mapped[PaperType] = mapped_column(
        Enum(PaperType, native_enum=False), default=PaperType.OTHER
    )
    analysis_status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, native_enum=False), default=AnalysisStatus.INGESTED
    )
    content_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    page_count: Mapped[int] = mapped_column(Integer)
    raw_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cases: Mapped[list[Case]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )
    evidence: Mapped[list[Evidence]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )
    extraction_runs: Mapped[list[ExtractionRun]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    patient_identifier: Mapped[str] = mapped_column(String(255))
    age: Mapped[int | None] = mapped_column(Integer)
    sex: Mapped[str | None] = mapped_column(String(50))
    melanoma_subtype: Mapped[str | None] = mapped_column(String(255))
    primary_site: Mapped[str | None] = mapped_column(String(255))
    primary_site_status: Mapped[str | None] = mapped_column(String(32))
    stage: Mapped[str | None] = mapped_column(String(100))
    metastatic_sites: Mapped[list[str]] = mapped_column(JSON, default=list)
    diagnosis_date: Mapped[date | None] = mapped_column(Date)
    regression_start_date: Mapped[date | None] = mapped_column(Date)
    first_observed_reduction: Mapped[str | None] = mapped_column(Text)
    regression_confirmed_date: Mapped[date | None] = mapped_column(Date)
    regression_duration: Mapped[str | None] = mapped_column(Text)
    regression_type: Mapped[str | None] = mapped_column(String(255))
    partial_or_complete: Mapped[str | None] = mapped_column(String(50))
    regression_extent_clinical: Mapped[str | None] = mapped_column(String(32))
    viable_tumor_at_pathology: Mapped[str | None] = mapped_column(String(32))
    treatment_before_regression: Mapped[str | None] = mapped_column(Text)
    treatment_status: Mapped[str | None] = mapped_column(String(100))
    preceding_event: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)
    follow_up_duration: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    extraction_confidence: Mapped[float | None] = mapped_column(Float)
    field_statuses: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    extraction_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL")
    )

    paper: Mapped[Paper] = relationship(back_populates="cases")
    events: Mapped[list[Event]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    evidence: Mapped[list[Evidence]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    biological_observations: Mapped[list[BiologicalObservation]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    lesions: Mapped[list[Lesion]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    lesion_collections: Mapped[list[LesionCollection]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    temporal_records: Mapped[list[TemporalRecord]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    genotype_observations: Mapped[list[GenotypeObservation]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    explanatory_alternatives: Mapped[list[ExplanatoryAlternative]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    regression_episodes: Mapped[list["RegressionEpisode"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    lesion_states: Mapped[list["LesionState"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    immune_related_adverse_events: Mapped[list["ImmuneRelatedAdverseEvent"]] = (
        relationship(back_populates="case", cascade="all, delete-orphan")
    )

    __table_args__ = (
        UniqueConstraint("paper_id", "patient_identifier", name="uq_case_paper_patient"),
        CheckConstraint("age IS NULL OR age >= 0", name="age_nonnegative"),
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    event_date: Mapped[date | None] = mapped_column(Date)
    date_precision: Mapped[DatePrecision] = mapped_column(
        Enum(DatePrecision, native_enum=False), default=DatePrecision.UNKNOWN
    )
    relative_day: Mapped[int | None] = mapped_column(Integer)
    relative_time: Mapped[str | None] = mapped_column(Text)
    source_date_precision: Mapped[str | None] = mapped_column(String(32))
    relation_to_regression: Mapped[str | None] = mapped_column(String(32))
    temporal_order_confidence: Mapped[float | None] = mapped_column(Float)
    temporal_value: Mapped[float | None] = mapped_column(Float)
    temporal_unit: Mapped[str | None] = mapped_column(String(32))
    temporal_relation: Mapped[str | None] = mapped_column(String(32))
    temporal_precision: Mapped[str | None] = mapped_column(String(32))
    anchor_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL"), index=True
    )
    extraction_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL")
    )
    event_type: Mapped[EventType] = mapped_column(Enum(EventType, native_enum=False))
    description: Mapped[str] = mapped_column(Text)

    case: Mapped[Case] = relationship(back_populates="events")

    __table_args__ = (
        CheckConstraint(
            "date_precision = 'UNKNOWN' OR event_date IS NOT NULL "
            "OR relative_day IS NOT NULL OR relative_time IS NOT NULL",
            name="event_has_temporal_anchor",
        ),
        CheckConstraint(
            "temporal_order_confidence IS NULL OR "
            "(temporal_order_confidence >= 0.0 AND temporal_order_confidence <= 1.0)",
            name="temporal_confidence_range",
        ),
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, native_enum=False)
    )
    claim: Mapped[str] = mapped_column(Text)
    source_quote: Mapped[str | None] = mapped_column(Text)
    raw_source_quote: Mapped[str | None] = mapped_column(Text)
    normalized_source_quote: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str | None] = mapped_column(String(32))
    page: Mapped[int | None] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(500))
    paragraph: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float)
    support_type: Mapped[SupportType] = mapped_column(
        Enum(SupportType, native_enum=False), default=SupportType.NEUTRAL
    )
    status: Mapped[EvidenceStatus] = mapped_column(
        Enum(EvidenceStatus, native_enum=False), default=EvidenceStatus.SUPPORTED
    )

    paper: Mapped[Paper] = relationship(back_populates="evidence")
    case: Mapped[Case | None] = relationship(back_populates="evidence")

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0", name="confidence_range"
        ),
        CheckConstraint("length(trim(claim)) > 0", name="claim_nonempty"),
        CheckConstraint(
            "status != 'SUPPORTED' OR "
            "(source_quote IS NOT NULL AND length(trim(source_quote)) > 0 "
            "AND (page IS NOT NULL OR "
            "(section IS NOT NULL AND length(trim(section)) > 0)))",
            name="supported_source_required",
        ),
        CheckConstraint("page IS NULL OR page > 0", name="page_positive"),
        CheckConstraint("paragraph IS NULL OR paragraph > 0", name="paragraph_positive"),
    )


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    source_extraction_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL")
    )
    run_type: Mapped[str | None] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(255))
    prompt_version: Mapped[str] = mapped_column(String(100))
    status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus, native_enum=False), default=ExtractionStatus.PENDING
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    error: Mapped[str | None] = mapped_column(Text)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    reason_codes: Mapped[list[str] | None] = mapped_column(JSON)
    schema_version: Mapped[str | None] = mapped_column(String(50))
    rule_version: Mapped[str | None] = mapped_column(String(100))

    paper: Mapped[Paper] = relationship(back_populates="extraction_runs")

    __table_args__ = (
        CheckConstraint("retry_count >= 0", name="retry_count_nonnegative"),
    )


class FieldEvidenceLink(Base):
    __tablename__ = "field_evidence_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    extraction_run_id: Mapped[int] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="CASCADE"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(32), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    field_name: Mapped[str] = mapped_column(String(100))
    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id", ondelete="CASCADE"), index=True
    )

    evidence: Mapped[Evidence] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "entity_type",
            "entity_id",
            "field_name",
            "evidence_id",
            name="uq_field_evidence_link",
        ),
        CheckConstraint(
            "entity_type IN ('case', 'event', 'paper', 'biological_observation')",
            name="known_entity_type",
        ),
    )


class BiologicalObservation(Base):
    __tablename__ = "biological_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int | None] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[ObservationCategory] = mapped_column(
        Enum(ObservationCategory, native_enum=False)
    )
    variable_name: Mapped[str] = mapped_column(String(255))
    normalized_variable: Mapped[str | None] = mapped_column(String(255), index=True)
    value: Mapped[str | None] = mapped_column(Text)
    normalized_value: Mapped[Any | None] = mapped_column(JSON)
    unit: Mapped[str | None] = mapped_column(String(100))
    direction: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    time_relation: Mapped[str | None] = mapped_column(String(32))
    temporal_precision: Mapped[str | None] = mapped_column(String(32))
    observation_domain: Mapped[str | None] = mapped_column(String(32), index=True)
    domain_secondary: Mapped[str | None] = mapped_column(String(32), index=True)
    measurement_semantics: Mapped[str | None] = mapped_column(String(32))
    scope_type: Mapped[str | None] = mapped_column(String(32), index=True)
    lesion_identifier: Mapped[str | None] = mapped_column(String(255), index=True)
    lesion_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesions.lesion_id", ondelete="SET NULL"), index=True
    )
    lesion_collection_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesion_collections.id", ondelete="SET NULL"), index=True
    )
    regression_role: Mapped[str | None] = mapped_column(String(32), index=True)
    qualitative_level: Mapped[str | None] = mapped_column(String(32))
    temporal_text: Mapped[str | None] = mapped_column(Text)
    temporal_value: Mapped[float | None] = mapped_column(Float)
    temporal_unit: Mapped[str | None] = mapped_column(String(32))
    temporal_relation: Mapped[str | None] = mapped_column(String(32))
    anchor_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL"), index=True
    )
    observation_context: Mapped[str | None] = mapped_column(Text)
    evidence_type: Mapped[str | None] = mapped_column(String(32))
    confidence: Mapped[float | None] = mapped_column(Float)
    linked_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL"), index=True
    )
    clinical_context_subtype: Mapped[str | None] = mapped_column(String(32))
    case_scope_status: Mapped[str | None] = mapped_column(String(32))
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )
    extraction_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )

    case: Mapped[Case] = relationship(back_populates="biological_observations")

    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="biological_observation_confidence_range",
        ),
    )


class Lesion(Base):
    __tablename__ = "lesions"

    id: Mapped[int] = mapped_column("lesion_id", primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    canonical_name: Mapped[str] = mapped_column(String(255))
    organ: Mapped[str | None] = mapped_column(String(100))
    anatomical_location: Mapped[str | None] = mapped_column(String(255))
    laterality: Mapped[str | None] = mapped_column(String(32))
    lesion_type: Mapped[str | None] = mapped_column(String(100))
    identity_key: Mapped[str] = mapped_column(String(255), index=True)
    reconciled_canonical_name: Mapped[str | None] = mapped_column(String(255))
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="lesions")
    aliases: Mapped[list[LesionAlias]] = relationship(
        back_populates="lesion",
        cascade="all, delete-orphan",
        foreign_keys="LesionAlias.lesion_id",
    )

    __table_args__ = (
        UniqueConstraint(
            "case_id", "created_from_run_id", "identity_key", name="uq_run_lesion_key"
        ),
    )


class LesionAlias(Base):
    __tablename__ = "lesion_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesion_id: Mapped[int] = mapped_column(
        ForeignKey("lesions.lesion_id", ondelete="CASCADE"), index=True
    )
    possible_same_lesion_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesions.lesion_id", ondelete="SET NULL"), index=True
    )
    source_text: Mapped[str] = mapped_column(Text)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    page: Mapped[int | None] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[LesionAliasStatus] = mapped_column(
        Enum(LesionAliasStatus, native_enum=False)
    )
    evidence_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"), index=True
    )

    lesion: Mapped[Lesion] = relationship(
        back_populates="aliases", foreign_keys=[lesion_id]
    )

    __table_args__ = (
        UniqueConstraint(
            "lesion_id",
            "source_text",
            "page",
            "section",
            name="uq_lesion_alias_source",
        ),
    )


class LesionCollection(Base):
    __tablename__ = "lesion_collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    canonical_name: Mapped[str] = mapped_column(String(255))
    collection_type: Mapped[LesionScopeKind] = mapped_column(
        Enum(LesionScopeKind, native_enum=False)
    )
    organ: Mapped[str | None] = mapped_column(String(100))
    anatomical_location: Mapped[str | None] = mapped_column(String(255))
    source_text: Mapped[str | None] = mapped_column(Text)
    laterality: Mapped[str | None] = mapped_column(String(32))
    normalized_label: Mapped[str | None] = mapped_column(String(255))
    member_count_reported: Mapped[int | None] = mapped_column(Integer)
    count_semantics: Mapped[str | None] = mapped_column(String(32))
    membership_status: Mapped[str | None] = mapped_column(String(32))
    membership_confidence: Mapped[float | None] = mapped_column(Float)
    collection_only: Mapped[bool] = mapped_column(default=True)
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="lesion_collections")
    memberships: Mapped[list[LesionCollectionMembership]] = relationship(
        back_populates="collection", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "created_from_run_id",
            "canonical_name",
            name="uq_run_lesion_collection",
        ),
    )


class LesionCollectionMembership(Base):
    __tablename__ = "lesion_collection_memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("lesion_collections.id", ondelete="CASCADE"), index=True
    )
    lesion_id: Mapped[int] = mapped_column(
        ForeignKey("lesions.lesion_id", ondelete="CASCADE"), index=True
    )
    evidence_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"), index=True
    )
    membership_confidence: Mapped[float | None] = mapped_column(Float)

    collection: Mapped[LesionCollection] = relationship(back_populates="memberships")

    __table_args__ = (
        UniqueConstraint(
            "collection_id", "lesion_id", name="uq_collection_lesion_membership"
        ),
    )


class TemporalRecord(Base):
    __tablename__ = "temporal_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    field_name: Mapped[str] = mapped_column(String(100))
    temporal_text: Mapped[str] = mapped_column(Text)
    temporal_value: Mapped[float | None] = mapped_column(Float)
    temporal_unit: Mapped[str | None] = mapped_column(String(32))
    temporal_relation: Mapped[str | None] = mapped_column(String(32))
    temporal_precision: Mapped[TemporalSemanticPrecision] = mapped_column(
        Enum(TemporalSemanticPrecision, native_enum=False)
    )
    anchor_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL"), index=True
    )
    evidence_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"), index=True
    )
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="temporal_records")


class GenotypeObservation(Base):
    __tablename__ = "genotype_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    biological_observation_id: Mapped[int | None] = mapped_column(
        ForeignKey("biological_observations.id", ondelete="SET NULL"), index=True
    )
    gene: Mapped[str] = mapped_column(String(100), index=True)
    variant: Mapped[str | None] = mapped_column(String(255))
    transcript: Mapped[str | None] = mapped_column(String(100))
    coding_change: Mapped[str | None] = mapped_column(String(255))
    protein_change: Mapped[str | None] = mapped_column(String(255))
    rs_id: Mapped[str | None] = mapped_column(String(64))
    variant_type: Mapped[str | None] = mapped_column(String(32))
    zygosity: Mapped[str | None] = mapped_column(String(32))
    origin: Mapped[str | None] = mapped_column(String(32))
    assay: Mapped[str | None] = mapped_column(String(255))
    source_context: Mapped[str | None] = mapped_column(Text)
    state: Mapped[GenotypeState] = mapped_column(
        Enum(GenotypeState, native_enum=False)
    )
    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id", ondelete="CASCADE"), index=True
    )
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="genotype_observations")

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "created_from_run_id",
            "gene",
            "variant",
            "state",
            "evidence_id",
            name="uq_genotype_observation_evidence",
        ),
    )


class ExplanatoryAlternative(Base):
    __tablename__ = "explanatory_alternatives"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    alternative_type: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text)
    temporal_relation: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[ExplanatoryAlternativeStatus] = mapped_column(
        Enum(ExplanatoryAlternativeStatus, native_enum=False)
    )
    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id", ondelete="CASCADE"), index=True
    )
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="explanatory_alternatives")

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "created_from_run_id",
            "alternative_type",
            "evidence_id",
            name="uq_explanatory_alternative_evidence",
        ),
    )


class RegressionEpisode(Base):
    __tablename__ = "regression_episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    episode_index: Mapped[int] = mapped_column(Integer)
    episode_type: Mapped[RegressionEpisodeType] = mapped_column(
        Enum(RegressionEpisodeType, native_enum=False)
    )
    onset_temporal_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("temporal_records.id", ondelete="SET NULL"), index=True
    )
    confirmation_temporal_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("temporal_records.id", ondelete="SET NULL"), index=True
    )
    extent: Mapped[RegressionExtent] = mapped_column(
        Enum(RegressionExtent, native_enum=False),
        default=RegressionExtent.UNCERTAIN,
    )
    spontaneous_status: Mapped[str | None] = mapped_column(String(32))
    associated_lesion_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    associated_event_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    associated_collection_ids: Mapped[list[int] | None] = mapped_column(JSON)
    anatomic_scope: Mapped[str | None] = mapped_column(String(255))
    milestones: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    source_episode_ids: Mapped[list[int] | None] = mapped_column(JSON)
    extent_transition: Mapped[str | None] = mapped_column(String(64))
    is_canonical: Mapped[bool | None] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    evidence_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"), index=True
    )
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="regression_episodes")

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "created_from_run_id",
            "episode_index",
            name="uq_run_regression_episode_index",
        ),
    )


class LesionState(Base):
    __tablename__ = "lesion_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    lesion_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesions.lesion_id", ondelete="SET NULL"), index=True
    )
    lesion_collection_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesion_collections.id", ondelete="SET NULL"), index=True
    )
    temporal_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("temporal_records.id", ondelete="SET NULL"), index=True
    )
    regression_status: Mapped[str | None] = mapped_column(String(64))
    viability_status: Mapped[str | None] = mapped_column(String(64))
    morphology_status: Mapped[str | None] = mapped_column(String(255))
    metabolic_status: Mapped[str | None] = mapped_column(String(255))
    pathology_status: Mapped[str | None] = mapped_column(String(255))
    evidence_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"), index=True
    )
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="lesion_states")

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "created_from_run_id",
            "lesion_id",
            "lesion_collection_id",
            name="uq_run_lesion_state",
        ),
    )


class ImmuneRelatedAdverseEvent(Base):
    __tablename__ = "immune_related_adverse_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(100))
    organ_system: Mapped[str | None] = mapped_column(String(100))
    grade: Mapped[str | None] = mapped_column(String(32))
    onset_relation_to_treatment: Mapped[str | None] = mapped_column(String(100))
    resolution_status: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    evidence_id: Mapped[int | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"), index=True
    )
    created_from_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("extraction_runs.id", ondelete="SET NULL"), index=True
    )

    case: Mapped[Case] = relationship(back_populates="immune_related_adverse_events")

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "created_from_run_id",
            "event_type",
            "description",
            name="uq_run_irae_description",
        ),
    )
