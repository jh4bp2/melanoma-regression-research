from __future__ import annotations

import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.base import LLMProvider, StructuredExtractionError
from app.models import (
    AnalysisStatus,
    Case,
    DatePrecision,
    Event,
    EventType,
    Evidence,
    EvidenceStatus,
    ExtractionRun,
    ExtractionStatus,
    FieldEvidenceLink,
    Paper,
    PartialReasonCode,
    SupportType,
    TemporalRecord,
)
from app.services.temporal_semantics import parse_temporal
from app.schemas.extraction import (
    CaseCandidate,
    CaseExistence,
    ExtractedField,
    FieldStatus,
    PaperMetadataCandidate,
    RegressionRelation,
    TimelineDatePrecision,
    TimelineEventCandidate,
)
from app.services.case_extractor import (
    CaseExistenceClassifier,
    CaseExtractor,
    PaperMetadataExtractor,
)
from app.services.chunking import chunk_pages, read_page_text
from app.services.evidence_verifier import (
    EvidenceVerifier,
    VerifiedReference,
    normalize_text,
)
from app.services.case_scope import scope_chunks_for_identifier
from app.services.timeline_extractor import TimelineExtractor


WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}
RELATIVE_RE = re.compile(
    r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    r"\s+(day|days|week|weeks|month|months)\s+(before|after)\b",
    re.IGNORECASE,
)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _exact_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _relative_day(relative_time: str | None) -> int | None:
    if not relative_time:
        return None
    match = RELATIVE_RE.search(relative_time)
    if not match:
        return None
    amount_text, unit, direction = match.groups()
    amount = (
        int(amount_text)
        if amount_text.isdigit()
        else WORD_NUMBERS[amount_text.casefold()]
    )
    multiplier = 1 if unit.casefold().startswith("day") else 7
    if unit.casefold().startswith("month"):
        multiplier = 30
    value = amount * multiplier
    return -value if direction.casefold() == "before" else value


class ExtractionPipeline:
    SCHEMA_VERSION = "phase2.3"
    RULE_VERSION = "phase2.3-case-scope-v1"

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.metadata_extractor = PaperMetadataExtractor(provider)
        self.classifier = CaseExistenceClassifier(provider)
        self.case_extractor = CaseExtractor(provider)
        self.timeline_extractor = TimelineExtractor(provider)

    @property
    def prompt_version(self) -> str:
        return ",".join(
            [
                f"{self.metadata_extractor.prompt.name}:"
                f"{self.metadata_extractor.prompt.version}",
                f"{self.classifier.prompt.name}:{self.classifier.prompt.version}",
                f"{self.case_extractor.prompt.name}:"
                f"{self.case_extractor.prompt.version}",
                f"{self.timeline_extractor.prompt.name}:"
                f"{self.timeline_extractor.prompt.version}",
            ]
        )

    def run(self, session: Session, paper_id: int) -> ExtractionRun:
        paper = session.get(Paper, paper_id)
        if paper is None:
            raise ValueError(f"Paper {paper_id} not found")

        run = ExtractionRun(
            paper_id=paper.id,
            run_type="case_timeline",
            model=self.provider.model,
            prompt_version=self.prompt_version,
            status=ExtractionStatus.RUNNING,
            retry_count=0,
            schema_version=self.SCHEMA_VERSION,
            rule_version=self.RULE_VERSION,
        )
        paper.analysis_status = AnalysisStatus.EXTRACTION_RUNNING
        session.add(run)
        session.commit()
        session.refresh(run)
        total_retries = 0
        result: dict[str, Any] = {}
        reason_codes: set[PartialReasonCode] = set()

        try:
            pages = read_page_text(Path(paper.extracted_text_path))
            chunks = chunk_pages(paper.id, pages)
            verifier = EvidenceVerifier(pages, chunks)
            result = {
                "verification_failures": [],
                "event_canonicalization": [],
                "schema_version": self.SCHEMA_VERSION,
                "rule_version": self.RULE_VERSION,
            }

            metadata_result = self.metadata_extractor.extract(chunks)
            total_retries += metadata_result.retry_count
            result["metadata"] = metadata_result.value.model_dump(mode="json")
            self._persist_metadata(
                session,
                paper,
                run,
                metadata_result.value,
                verifier,
                result["verification_failures"],
                reason_codes,
            )

            detection_result = self.classifier.classify(chunks)
            total_retries += detection_result.retry_count
            detection = detection_result.value
            result["case_detection"] = detection.model_dump(mode="json")
            verified_detection = self._verified_references(
                detection.evidence_refs,
                verifier,
                result["verification_failures"],
                "paper.case_existence",
            )
            for reference in verified_detection:
                evidence = self._create_evidence(
                    session,
                    paper.id,
                    None,
                    f"paper.case_existence: {detection.existence.value}",
                    reference,
                    detection.confidence,
                )
                self._link(session, run.id, "paper", paper.id, "case_existence", evidence)

            if detection.existence == CaseExistence.NO:
                if total_retries:
                    reason_codes.add(PartialReasonCode.SCHEMA_RECOVERY)
                run.status = (
                    ExtractionStatus.PARTIAL
                    if reason_codes
                    else ExtractionStatus.COMPLETED
                )
                run.retry_count = total_retries
                run.reason_codes = sorted(code.value for code in reason_codes)
                result["partial_reason_codes"] = run.reason_codes
                paper.analysis_status = (
                    AnalysisStatus.PARTIAL
                    if reason_codes
                    else AnalysisStatus.EXTRACTED
                )
                run.result_json = result
                run.finished_at = _utcnow()
                session.commit()
                session.refresh(run)
                return run
            if detection.existence == CaseExistence.YES and not verified_detection:
                reason_codes.update(
                    {
                        PartialReasonCode.UNVERIFIED_QUOTE,
                        PartialReasonCode.FIELD_WITHOUT_EVIDENCE,
                    }
                )
                raise ValueError("Positive case detection had no verifiable source quote")
            if detection.existence == CaseExistence.UNCERTAIN:
                reason_codes.add(PartialReasonCode.CASE_EXISTENCE_UNCERTAIN)
                if total_retries:
                    reason_codes.add(PartialReasonCode.SCHEMA_RECOVERY)
                run.status = ExtractionStatus.PARTIAL
                run.retry_count = total_retries
                run.reason_codes = sorted(code.value for code in reason_codes)
                result["partial_reason_codes"] = run.reason_codes
                paper.analysis_status = AnalysisStatus.PARTIAL
                run.result_json = result
                run.finished_at = _utcnow()
                session.commit()
                session.refresh(run)
                return run

            case_result = self.case_extractor.extract(chunks)
            total_retries += case_result.retry_count
            result["cases"] = case_result.value.model_dump(mode="json")["cases"]
            result["timelines"] = []

            for index, candidate in enumerate(case_result.value.cases):
                if any(
                    getattr(candidate, field_name).status == FieldStatus.UNCERTAIN
                    for field_name in (
                        "diagnosis_date",
                        "regression_start_date",
                        "first_observed_reduction",
                        "regression_confirmed_date",
                        "treatment_status",
                    )
                ):
                    reason_codes.add(PartialReasonCode.TEMPORAL_UNCERTAINTY)
                case = self._persist_case(
                    session,
                    paper,
                    run,
                    candidate,
                    index,
                    verifier,
                    result["verification_failures"],
                    reason_codes,
                )
                identifier = None
                if candidate.patient_identifier.value:
                    identifier = str(candidate.patient_identifier.value)
                timeline_result = self.timeline_extractor.extract(
                    scope_chunks_for_identifier(chunks, identifier),
                    candidate,
                )
                total_retries += timeline_result.retry_count
                result["timelines"].append(
                    {
                        "case_id": case.id,
                        "events": timeline_result.value.model_dump(mode="json")["events"],
                    }
                )
                if any(
                    event.event_type.value == "treatment"
                    and (
                        event.date_precision == TimelineDatePrecision.UNKNOWN
                        or event.relation_to_regression == RegressionRelation.UNKNOWN
                    )
                    for event in timeline_result.value.events
                ):
                    reason_codes.add(PartialReasonCode.TEMPORAL_UNCERTAINTY)
                for event_candidate in timeline_result.value.events:
                    self._persist_event(
                        session,
                        paper,
                        case,
                        run,
                        event_candidate,
                        verifier,
                        result["verification_failures"],
                        reason_codes,
                        result["event_canonicalization"],
                    )

            if result["verification_failures"]:
                reason_codes.add(PartialReasonCode.UNVERIFIED_QUOTE)
            if total_retries:
                reason_codes.add(PartialReasonCode.SCHEMA_RECOVERY)
            has_cases = bool(case_result.value.cases)
            if not has_cases:
                reason_codes.add(PartialReasonCode.FIELD_WITHOUT_EVIDENCE)
            run.status = (
                ExtractionStatus.PARTIAL
                if reason_codes
                else ExtractionStatus.COMPLETED
            )
            run.retry_count = total_retries
            run.reason_codes = sorted(code.value for code in reason_codes)
            result["partial_reason_codes"] = run.reason_codes
            paper.analysis_status = (
                AnalysisStatus.PARTIAL if run.status == ExtractionStatus.PARTIAL
                else AnalysisStatus.EXTRACTED
            )
            run.result_json = result
            run.finished_at = _utcnow()
            session.commit()
            session.refresh(run)
            return run
        except Exception as exc:
            session.rollback()
            failed_run = session.get(ExtractionRun, run.id)
            failed_paper = session.get(Paper, paper_id)
            if failed_run is not None:
                failed_run.status = ExtractionStatus.FAILED
                failed_run.finished_at = _utcnow()
                failed_run.error = str(exc)[:4000]
                failed_run.result_json = result or None
                failed_run.reason_codes = sorted(code.value for code in reason_codes)
                failed_run.retry_count = total_retries + (
                    exc.retry_count if isinstance(exc, StructuredExtractionError) else 0
                )
            if failed_paper is not None:
                failed_paper.analysis_status = AnalysisStatus.FAILED
            session.commit()
            raise

    def _persist_metadata(
        self,
        session: Session,
        paper: Paper,
        run: ExtractionRun,
        metadata: PaperMetadataCandidate,
        verifier: EvidenceVerifier,
        failures: list[dict[str, Any]],
        reason_codes: set[PartialReasonCode],
    ) -> None:
        for field_name in metadata.__class__.model_fields:
            field: ExtractedField = getattr(metadata, field_name)
            references = self._verified_references(
                field.evidence_refs,
                verifier,
                failures,
                f"paper.{field_name}",
            )
            if field.status != FieldStatus.REPORTED or not references:
                if field.status == FieldStatus.REPORTED and not references:
                    reason_codes.add(PartialReasonCode.FIELD_WITHOUT_EVIDENCE)
                continue
            value = field.value
            setattr(paper, field_name, value)
            for reference in references:
                evidence = self._create_evidence(
                    session,
                    paper.id,
                    None,
                    f"paper.{field_name}: {value}",
                    reference,
                    1.0,
                )
                self._link(session, run.id, "paper", paper.id, field_name, evidence)

    def _persist_case(
        self,
        session: Session,
        paper: Paper,
        run: ExtractionRun,
        candidate: CaseCandidate,
        index: int,
        verifier: EvidenceVerifier,
        failures: list[dict[str, Any]],
        reason_codes: set[PartialReasonCode],
    ) -> Case:
        identifier_field = candidate.patient_identifier
        identifier_refs = self._verified_references(
            identifier_field.evidence_refs,
            verifier,
            failures,
            "case.patient_identifier",
        )
        reported = (
            str(identifier_field.value)
            if identifier_field.status == FieldStatus.REPORTED and identifier_refs
            else f"paper-{paper.id}-case-{index + 1}"
        )
        identifier = f"{reported} [run {run.id}]"
        case = session.scalar(
            select(Case).where(
                Case.paper_id == paper.id,
                Case.patient_identifier == identifier,
            )
        )
        if case is None:
            case = Case(paper_id=paper.id, patient_identifier=identifier)
            session.add(case)
            session.flush()

        case.extraction_confidence = candidate.confidence
        case.extraction_run_id = run.id
        field_statuses: dict[str, Any] = {}
        scalar_fields = {
            "age": "age",
            "sex": "sex",
            "melanoma_subtype": "melanoma_subtype",
            "primary_site": "primary_site",
            "stage": "stage",
            "metastatic_sites": "metastatic_sites",
            "diagnosis_date": "diagnosis_date",
            "regression_start_date": "regression_start_date",
            "first_observed_reduction": "first_observed_reduction",
            "regression_confirmed_date": "regression_confirmed_date",
            "regression_duration": "regression_duration",
            "regression_type": "regression_type",
            "regression_extent_clinical": "regression_extent_clinical",
            "viable_tumor_at_pathology": "viable_tumor_at_pathology",
            "treatment_before_regression": "treatment_before_regression",
            "treatment_status": "treatment_status",
            "preceding_events": "preceding_event",
            "outcome": "outcome",
            "follow_up_duration": "follow_up_duration",
        }
        for column_name in set(scalar_fields.values()):
            setattr(case, column_name, [] if column_name == "metastatic_sites" else None)
        case.partial_or_complete = None
        case.primary_site_status = None

        for field_name in candidate.__class__.model_fields:
            if field_name == "confidence":
                continue
            field: ExtractedField = getattr(candidate, field_name)
            field_statuses[field_name] = {
                "status": field.status.value,
                "raw_value": field.model_dump(mode="json")["value"],
            }
            if field_name == "primary_site":
                case.primary_site_status = field.status.value
            references = self._verified_references(
                field.evidence_refs,
                verifier,
                failures,
                f"case.{field_name}",
            )
            if field.status in {
                FieldStatus.REPORTED,
                FieldStatus.REPORTED_ABSENT,
            } and not references:
                field_statuses[field_name]["status"] = FieldStatus.UNCERTAIN.value
                if field_name == "primary_site":
                    case.primary_site_status = FieldStatus.UNCERTAIN.value
                reason_codes.add(PartialReasonCode.FIELD_WITHOUT_EVIDENCE)
                continue
            if field.status == FieldStatus.NOT_REPORTED:
                continue

            should_store_value = field.status == FieldStatus.REPORTED or (
                field.status == FieldStatus.UNCERTAIN
                and field_name
                in {"regression_extent_clinical", "viable_tumor_at_pathology"}
            )
            if field_name in scalar_fields and should_store_value:
                value = field.value
                if field_name.endswith("_date"):
                    value = _exact_date(value)
                elif field_name == "preceding_events":
                    value = "; ".join(value or [])
                elif hasattr(value, "value"):
                    value = value.value
                setattr(case, scalar_fields[field_name], value)

            for reference in references:
                evidence = self._create_evidence(
                    session,
                    paper.id,
                    case.id,
                    f"case.{field_name}: {field.value}",
                    reference,
                    candidate.confidence,
                )
                self._link(session, run.id, "case", case.id, field_name, evidence)

        case.field_statuses = field_statuses
        session.flush()
        self._persist_case_temporal_records(
            session, paper, case, run, candidate, field_statuses
        )
        return case

    def _persist_case_temporal_records(
        self,
        session: Session,
        paper: Paper,
        case: Case,
        run: ExtractionRun,
        candidate: CaseCandidate,
        field_statuses: dict[str, Any],
    ) -> None:
        temporal_fields = (
            "diagnosis_date",
            "regression_start_date",
            "first_observed_reduction",
            "regression_confirmed_date",
            "regression_duration",
            "follow_up_duration",
        )
        for field_name in temporal_fields:
            raw = (field_statuses.get(field_name) or {}).get("raw_value")
            if raw is None:
                continue
            parsed = parse_temporal(str(raw))
            if parsed is None:
                continue
            if parsed.temporal_precision.value == "EXACT_DATE" and field_name.endswith(
                "_date"
            ):
                continue
            evidence = session.scalar(
                select(Evidence)
                .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
                .where(
                    FieldEvidenceLink.extraction_run_id == run.id,
                    FieldEvidenceLink.entity_type == "case",
                    FieldEvidenceLink.entity_id == case.id,
                    FieldEvidenceLink.field_name == field_name,
                )
                .order_by(Evidence.id)
            )
            session.add(
                TemporalRecord(
                    paper_id=paper.id,
                    case_id=case.id,
                    entity_type="case",
                    entity_id=case.id,
                    field_name=field_name,
                    temporal_text=parsed.temporal_text,
                    temporal_value=parsed.temporal_value,
                    temporal_unit=parsed.temporal_unit,
                    temporal_relation=parsed.temporal_relation,
                    temporal_precision=parsed.temporal_precision,
                    evidence_id=evidence.id if evidence else None,
                    created_from_run_id=run.id,
                )
            )

    def _persist_event(
        self,
        session: Session,
        paper: Paper,
        case: Case,
        run: ExtractionRun,
        candidate: TimelineEventCandidate,
        verifier: EvidenceVerifier,
        failures: list[dict[str, Any]],
        reason_codes: set[PartialReasonCode],
        canonicalization_log: list[dict[str, Any]],
    ) -> None:
        references = self._verified_references(
            candidate.evidence_refs,
            verifier,
            failures,
            "event.description",
        )
        if not references:
            reason_codes.add(PartialReasonCode.FIELD_WITHOUT_EVIDENCE)
            return
        precision_map = {
            TimelineDatePrecision.EXACT: DatePrecision.EXACT,
            TimelineDatePrecision.APPROXIMATE: DatePrecision.APPROXIMATE,
            TimelineDatePrecision.RELATIVE: DatePrecision.RELATIVE,
            TimelineDatePrecision.UNKNOWN: DatePrecision.UNKNOWN,
        }
        relative_day = _relative_day(candidate.relative_time)
        database_precision = precision_map[candidate.date_precision]
        if (
            database_precision != DatePrecision.UNKNOWN
            and _exact_date(candidate.event_date) is None
            and relative_day is None
        ):
            # PHASE 1 SQLite databases have a legacy CHECK constraint that
            # requires an exact date or numeric relative_day for every known
            # precision. Preserve textual timing and source precision separately
            # rather than inventing a numeric offset.
            database_precision = DatePrecision.UNKNOWN
        parsed_temporal = parse_temporal(
            candidate.relative_time or candidate.event_date
        )
        event = self._find_canonical_event(session, case.id, run.id, candidate)
        if event is None:
            event = Event(
                case_id=case.id,
                event_date=_exact_date(candidate.event_date),
                date_precision=database_precision,
                relative_day=relative_day,
                relative_time=candidate.relative_time,
                source_date_precision=candidate.date_precision.value,
                relation_to_regression=candidate.relation_to_regression.value,
                temporal_order_confidence=candidate.temporal_order_confidence,
                temporal_value=parsed_temporal.temporal_value if parsed_temporal else None,
                temporal_unit=parsed_temporal.temporal_unit if parsed_temporal else None,
                temporal_relation=(
                    parsed_temporal.temporal_relation if parsed_temporal else None
                ),
                temporal_precision=(
                    parsed_temporal.temporal_precision.value if parsed_temporal else None
                ),
                extraction_run_id=run.id,
                event_type=candidate.event_type,
                description=candidate.description,
            )
            session.add(event)
            session.flush()
        else:
            canonicalization_log.append(
                {
                    "event_id": event.id,
                    "event_type": candidate.event_type.value,
                    "merged_description": candidate.description,
                    "reason": "duplicate clinical observation",
                }
            )
            event.temporal_order_confidence = max(
                event.temporal_order_confidence or 0.0,
                candidate.temporal_order_confidence,
            )
        first_evidence: Evidence | None = None
        for reference in references:
            if self._event_reference_already_linked(
                session, run.id, event.id, reference
            ):
                continue
            evidence = self._create_evidence(
                session,
                paper.id,
                case.id,
                f"event.description: {candidate.description}",
                reference,
                candidate.temporal_order_confidence,
            )
            if first_evidence is None:
                first_evidence = evidence
            linked_fields = ["description", "event_type", "relation_to_regression"]
            if candidate.event_date is not None:
                linked_fields.append("event_date")
            if candidate.relative_time is not None:
                linked_fields.extend(["relative_time", "date_precision"])
            for field_name in linked_fields:
                self._link(session, run.id, "event", event.id, field_name, evidence)
        if parsed_temporal is not None and first_evidence is not None:
            existing_temporal = session.scalar(
                select(TemporalRecord).where(
                    TemporalRecord.created_from_run_id == run.id,
                    TemporalRecord.entity_type == "event",
                    TemporalRecord.entity_id == event.id,
                )
            )
            if existing_temporal is None:
                session.add(
                    TemporalRecord(
                        paper_id=paper.id,
                        case_id=case.id,
                        entity_type="event",
                        entity_id=event.id,
                        field_name="relative_time",
                        temporal_text=parsed_temporal.temporal_text,
                        temporal_value=parsed_temporal.temporal_value,
                        temporal_unit=parsed_temporal.temporal_unit,
                        temporal_relation=parsed_temporal.temporal_relation,
                        temporal_precision=parsed_temporal.temporal_precision,
                        evidence_id=first_evidence.id,
                        created_from_run_id=run.id,
                    )
                )

    @staticmethod
    def _event_terms(text: str) -> set[str]:
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "of",
            "in",
            "to",
            "was",
            "were",
            "with",
            "on",
            "at",
            "had",
            "has",
            "patient",
        }
        aliases = {
            "decreased": "decrease",
            "decreases": "decrease",
            "reduced": "decrease",
            "reduction": "decrease",
            "pulmonary": "lung",
            "months": "month",
            "weeks": "week",
            "days": "day",
            "six": "6",
        }
        terms = set()
        for token in re.findall(r"[a-z0-9.]+", normalize_text(text)):
            token = token.strip(".")
            token = aliases.get(token, token)
            if token not in stop_words and len(token) > 1:
                terms.add(token)
        return terms

    @classmethod
    def _find_canonical_event(
        cls,
        session: Session,
        case_id: int,
        run_id: int,
        candidate: TimelineEventCandidate,
    ) -> Event | None:
        existing_events = session.scalars(
            select(Event).where(
                Event.case_id == case_id,
                Event.extraction_run_id == run_id,
                Event.event_type == candidate.event_type,
            )
        )
        candidate_normalized = normalize_text(candidate.description)
        candidate_terms = cls._event_terms(candidate.description)
        candidate_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", candidate_normalized))
        for event in existing_events:
            event_normalized = normalize_text(event.description)
            if event_normalized == candidate_normalized:
                return event
            event_terms = cls._event_terms(event.description)
            union = candidate_terms | event_terms
            similarity = len(candidate_terms & event_terms) / max(len(union), 1)
            if similarity >= 0.72:
                return event
            if candidate.event_type == EventType.TUMOR_REGRESSION:
                event_numbers = set(
                    re.findall(r"\b\d+(?:\.\d+)?\b", event_normalized)
                )
                if candidate_numbers & event_numbers and similarity >= 0.35:
                    return event
        return None

    @staticmethod
    def _event_reference_already_linked(
        session: Session,
        run_id: int,
        event_id: int,
        reference: VerifiedReference,
    ) -> bool:
        evidence_rows = session.scalars(
            select(Evidence)
            .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
            .where(
                FieldEvidenceLink.extraction_run_id == run_id,
                FieldEvidenceLink.entity_type == "event",
                FieldEvidenceLink.entity_id == event_id,
            )
        ).unique()
        return any(
            evidence.page == reference.page
            and normalize_text(evidence.source_quote or "")
            == normalize_text(reference.quote)
            for evidence in evidence_rows
        )

    @staticmethod
    def _verified_references(
        references,
        verifier: EvidenceVerifier,
        failures: list[dict[str, Any]],
        field_name: str,
    ) -> list[VerifiedReference]:
        verified: list[VerifiedReference] = []
        for reference in references:
            result = verifier.verify(reference)
            if result.verified:
                verified.append(result)
            else:
                failures.append(
                    {
                        "field": field_name,
                        "page": result.page,
                        "quote": result.quote,
                        "reason": result.reason,
                        "status": EvidenceStatus.UNVERIFIED.value,
                    }
                )
        return verified

    @staticmethod
    def _create_evidence(
        session: Session,
        paper_id: int,
        case_id: int | None,
        claim: str,
        reference: VerifiedReference,
        confidence: float,
    ) -> Evidence:
        evidence = Evidence(
            paper_id=paper_id,
            case_id=case_id,
            evidence_type=reference.evidence_type,
            claim=claim,
            source_quote=reference.quote,
            raw_source_quote=reference.raw_quote or reference.quote,
            normalized_source_quote=reference.normalized_quote,
            verification_status=reference.verification_status.value,
            page=reference.page,
            section=reference.section,
            confidence=confidence,
            support_type=SupportType.NEUTRAL,
            status=EvidenceStatus.SUPPORTED,
        )
        session.add(evidence)
        session.flush()
        return evidence

    @staticmethod
    def _link(
        session: Session,
        run_id: int,
        entity_type: str,
        entity_id: int,
        field_name: str,
        evidence: Evidence,
    ) -> None:
        session.add(
            FieldEvidenceLink(
                extraction_run_id=run_id,
                entity_type=entity_type,
                entity_id=entity_id,
                field_name=field_name,
                evidence_id=evidence.id,
            )
        )
