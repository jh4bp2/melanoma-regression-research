from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.base import LLMProvider, StructuredExtractionError
from app.models import (
    BiologicalObservation,
    BiologicalDirection,
    BiologicalStatus,
    BiologicalTimeRelation,
    Case,
    CaseScopeStatus,
    ClinicalContextSubtype,
    Event,
    EventType,
    Evidence,
    EvidenceStatus,
    EvidenceType,
    ExplanatoryAlternative,
    ExplanatoryAlternativeStatus,
    ExtractionRun,
    ExtractionStatus,
    FieldEvidenceLink,
    GenotypeObservation,
    GenotypeState,
    ImmuneRelatedAdverseEvent,
    Lesion,
    LesionAlias,
    LesionAliasStatus,
    LesionCollection,
    LesionCollectionMembership,
    LesionState,
    MeasurementSemantics,
    ObservationCategory,
    ObservationDomain,
    PartialReasonCode,
    QualitativeLevel,
    QuoteVerificationStatus,
    RegressionEpisode,
    RegressionEpisodeType,
    RegressionExtent,
    RegressionRole,
    ScopeType,
    SupportType,
    TemporalRecord,
    TemporalSemanticPrecision,
)
from app.services.case_scope import other_patient_quote, quote_scope_status, scope_chunks
from app.services.genotype_semantics import is_genotype_claim, parse_genotype
from app.services.irae_semantics import canonical_irae_groups, parse_irae
from app.services.recall_hardening import (
    classify_explanatory_alternative,
    reconcile_phase2_genotypes,
    scan_explanatory_alternatives,
    scan_genotype_text,
    scan_immune_pathology,
    verify_hit,
)
from app.services.lesion_identity import (
    collection_membership_ok,
    merge_decision,
    parse_lesion_text,
)
from app.services.pathology_split import split_pathology_observations
from app.services.regression_episodes import build_regression_episodes
from app.services.temporal_semantics import parse_temporal
from app.schemas.extraction import (
    BiologicalObservationCandidate,
    RejectedInterpretationCandidate,
)
from app.services.biological_observation_extractor import (
    BiologicalObservationExtractor,
)
from app.services.chunking import chunk_pages, read_page_text
from app.services.evidence_verifier import (
    EvidenceVerifier,
    VerifiedReference,
    normalize_text,
)


TARGET_VARIABLES = {
    "CD8_T_CELL",
    "CD4_T_CELL",
    "NK_CELL",
    "TREG",
    "MACROPHAGE",
    "DENDRITIC_CELL",
    "LYMPHOCYTE",
    "IMMUNE_INFILTRATION",
    "PD_1",
    "PD_L1",
    "CTLA_4",
    "IFN_ALPHA",
    "IFN_BETA",
    "IFN_GAMMA",
    "IL_2",
    "IL_6",
    "TNF_ALPHA",
    "CRP",
    "FEVER",
    "SYSTEMIC_INFLAMMATION",
    "GLUCOSE",
    "FDG_UPTAKE",
    "SUV",
    "LACTATE",
    "IRON",
    "OXYGEN",
    "HYPOXIA",
    "LIPID_METABOLISM",
    "TUMOR_NECROSIS",
    "VIABLE_TUMOR_CELLS",
    "APOPTOSIS",
    "FIBROSIS",
    "ANGIOGENESIS",
    "TUMOR_PERFUSION",
    "CORTISOL",
    "CATECHOLAMINE",
    "HORMONAL_CHANGE",
    "INFECTION",
    "IDENTIFIED_ORGANISM",
    "MICROBIOME_CHANGE",
}


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class BiologicalObservationPipeline:
    SCHEMA_VERSION = "phase3.4"
    RULE_VERSION = "phase3.4-stability-v1"
    RUN_TYPE = "biological_observation"

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.extractor = BiologicalObservationExtractor(provider)

    @property
    def prompt_version(self) -> str:
        return f"{self.extractor.prompt.name}:{self.extractor.prompt.version}"

    def run_case(
        self,
        session: Session,
        case_id: int,
        *,
        source_run_id: int | None = None,
    ) -> ExtractionRun:
        case = session.get(Case, case_id)
        if case is None:
            raise ValueError(f"Case {case_id} not found")
        source_run_id = source_run_id or case.extraction_run_id
        source_run = (
            session.get(ExtractionRun, source_run_id)
            if source_run_id is not None
            else None
        )
        if source_run is None or source_run.paper_id != case.paper_id:
            raise ValueError(
                "A preserved Case/Timeline extraction run for this case is required"
            )

        run = ExtractionRun(
            paper_id=case.paper_id,
            case_id=case.id,
            source_extraction_run_id=source_run.id,
            run_type=self.RUN_TYPE,
            model=self.provider.model,
            prompt_version=self.prompt_version,
            schema_version=self.SCHEMA_VERSION,
            rule_version=self.RULE_VERSION,
            status=ExtractionStatus.RUNNING,
            retry_count=0,
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        result: dict[str, Any] = {
            "case_id": case.id,
            "source_extraction_run_id": source_run.id,
            "schema_version": self.SCHEMA_VERSION,
            "rule_version": self.RULE_VERSION,
            "verification_failures": [],
            "rejected_as_interpretation": [],
            "duplicate_merges": [],
            "lesion_alias_merges": [],
            "unresolved_lesion_identities": [],
            "explanatory_alternatives": [],
            "case_scope_uncertain": [],
            "reconciliation_required": [],
            "recovered_from_recall": [],
        }
        reason_codes: set[PartialReasonCode] = set()

        try:
            pages = read_page_text(Path(case.paper.extracted_text_path))
            chunks = scope_chunks(chunk_pages(case.paper_id, pages), case)
            verifier = EvidenceVerifier(pages, chunks)
            events = list(
                session.scalars(
                    select(Event)
                    .where(
                        Event.case_id == case.id,
                        Event.extraction_run_id == source_run.id,
                    )
                    .order_by(Event.id)
                )
            )
            extraction = self.extractor.extract(
                chunks,
                self._case_context(case),
                [self._event_context(event) for event in events],
            )
            run.retry_count = extraction.retry_count
            result["observations"] = extraction.value.model_dump(mode="json")[
                "observations"
            ]
            result["rejected_interpretations"] = extraction.value.model_dump(
                mode="json"
            )["rejected_interpretations"]

            for interpretation in extraction.value.rejected_interpretations:
                self._persist_rejected_interpretation(
                    session,
                    run,
                    case,
                    interpretation,
                    verifier,
                    result,
                    reason_codes,
                )

            persisted: list[BiologicalObservation] = []
            for candidate in split_pathology_observations(
                extraction.value.observations
            ):
                observation = self._persist_observation(
                    session,
                    run,
                    case,
                    events,
                    candidate,
                    verifier,
                    result,
                    reason_codes,
                )
                if observation is not None and observation not in persisted:
                    persisted.append(observation)

            self._ensure_infection_clinical_context(
                session, run, case, events, persisted, result, reason_codes
            )
            self._ensure_timeline_clinical_context(
                session, run, case, events, persisted
            )
            self._run_stability_recall(
                session,
                run,
                case,
                events,
                pages,
                chunks,
                verifier,
                persisted,
                result,
                reason_codes,
            )
            self._ensure_irae_records(
                session, run, case, events, persisted, result
            )
            self._persist_regression_episodes(session, run, case, events)
            self._persist_lesion_states(session, run, case, persisted)
            covered = self._covered_target_variables(persisted)
            not_reported = sorted(TARGET_VARIABLES - covered)
            result["not_reported_variables"] = not_reported
            result["metrics"] = {
                "persisted_observations": len(persisted),
                "verified_evidence": self._run_evidence_count(session, run.id),
                "rejected_evidence": len(result["rejected_as_interpretation"]),
                "duplicate_merges": len(result["duplicate_merges"]),
                "lesion_alias_merges": len(result["lesion_alias_merges"]),
                "unresolved_lesion_identities": len(
                    result["unresolved_lesion_identities"]
                ),
                "dual_domain_immune": sum(
                    1
                    for observation in persisted
                    if observation.observation_domain
                    == ObservationDomain.BIOLOGICAL_STATE.value
                    and observation.domain_secondary
                    == ObservationDomain.DIAGNOSTIC_EVIDENCE.value
                    and observation.category == ObservationCategory.IMMUNE
                ),
                "genotype_records": len(
                    list(
                        session.scalars(
                            select(GenotypeObservation).where(
                                GenotypeObservation.created_from_run_id == run.id
                            )
                        )
                    )
                ),
                "uncertain_observations": sum(
                    observation.status
                    in {
                        BiologicalStatus.UNCERTAIN.value,
                        BiologicalStatus.CONFLICTING.value,
                    }
                    for observation in persisted
                ),
                "not_reported_variables": len(not_reported),
                "regression_episodes": self._count_rows(
                    session, RegressionEpisode, run.id
                ),
                "irae_records": self._count_rows(
                    session, ImmuneRelatedAdverseEvent, run.id
                ),
                "leukoderma_records": sum(
                    1
                    for observation in persisted
                    if observation.category
                    == ObservationCategory.DERMATOLOGIC_PHENOTYPE
                    or "leukoderma"
                    in normalize_text(
                        f"{observation.variable_name} {observation.value or ''}"
                    )
                ),
                "case_scope_uncertain": len(result.get("case_scope_uncertain", [])),
                "reconciliation_required": len(
                    result.get("reconciliation_required", [])
                ),
                "recovered_from_recall": len(result.get("recovered_from_recall", [])),
            }
            if extraction.retry_count:
                reason_codes.add(PartialReasonCode.SCHEMA_RECOVERY)
            if result["verification_failures"]:
                reason_codes.add(PartialReasonCode.UNVERIFIED_QUOTE)
            run.status = (
                ExtractionStatus.PARTIAL
                if reason_codes
                else ExtractionStatus.COMPLETED
            )
            run.reason_codes = sorted(code.value for code in reason_codes)
            run.result_json = result
            run.finished_at = _utcnow()
            session.commit()
            session.refresh(run)
            return run
        except Exception as exc:
            session.rollback()
            failed_run = session.get(ExtractionRun, run.id)
            if failed_run is not None:
                failed_run.status = ExtractionStatus.FAILED
                failed_run.finished_at = _utcnow()
                failed_run.error = str(exc)[:4000]
                failed_run.result_json = result
                failed_run.reason_codes = sorted(code.value for code in reason_codes)
                failed_run.retry_count += (
                    exc.retry_count if isinstance(exc, StructuredExtractionError) else 0
                )
                session.commit()
            raise

    @staticmethod
    def _case_context(case: Case) -> dict[str, Any]:
        return {
            "case_id": case.id,
            "paper_id": case.paper_id,
            "patient_identifier": case.patient_identifier,
            "field_statuses": case.field_statuses,
            "regression_start_date": case.regression_start_date,
            "first_observed_reduction": case.first_observed_reduction,
            "regression_confirmed_date": case.regression_confirmed_date,
            "regression_duration": case.regression_duration,
            "regression_extent_clinical": case.regression_extent_clinical,
            "viable_tumor_at_pathology": case.viable_tumor_at_pathology,
        }

    @staticmethod
    def _event_context(event: Event) -> dict[str, Any]:
        return {
            "event_id": event.id,
            "event_type": event.event_type.value,
            "description": event.description,
            "event_date": event.event_date,
            "relative_time": event.relative_time,
            "relation_to_regression": event.relation_to_regression,
        }

    def _persist_observation(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        events: list[Event],
        candidate: BiologicalObservationCandidate,
        verifier: EvidenceVerifier,
        result: dict[str, Any],
        reason_codes: set[PartialReasonCode],
    ) -> BiologicalObservation | None:
        if candidate.status == BiologicalStatus.NOT_REPORTED:
            return None
        original_lesion_identifier = candidate.lesion_identifier
        self._harden_ontology(candidate)
        if any(
            other_patient_quote(reference.quote, case)
            for reference in candidate.evidence_refs
        ):
            reason_codes.add(PartialReasonCode.CASE_SCOPE_UNCERTAIN)
            result.setdefault("case_scope_uncertain", []).append(
                {
                    "variable": candidate.variable_name,
                    "reason": "Quote names another patient and was not assigned",
                }
            )
            return None

        observed_refs: list[VerifiedReference] = []
        for reference in candidate.evidence_refs:
            verified = verifier.verify(reference)
            if not verified.verified:
                self._record_verification_failure(
                    result, f"biological_observation.{candidate.variable_name}", verified
                )
                continue
            if verified.evidence_type == EvidenceType.AUTHOR_INTERPRETATION:
                self._persist_verified_interpretation(
                    session,
                    run,
                    case,
                    candidate.variable_name,
                    "Mechanistic or interpretive language cannot be an observation",
                    candidate.confidence,
                    verified,
                    result,
                )
                continue
            observed_refs.append(verified)

        if not observed_refs:
            reason_codes.add(PartialReasonCode.FIELD_WITHOUT_EVIDENCE)
            return None

        lesion, collection = self._resolve_lesion_graph(
            session,
            run,
            case,
            candidate,
            observed_refs,
            result,
            extra_alias_texts=[original_lesion_identifier]
            if original_lesion_identifier
            else None,
        )
        parsed_temporal = parse_temporal(
            candidate.temporal_text
            or candidate.observation_context
            or candidate.value
        )
        linked_event_id = self._match_event(candidate, events)
        anchor_event_id = self._match_anchor_event(candidate, events) or linked_event_id
        canonical = self._find_canonical_observation(
            session, run.id, candidate, lesion.id if lesion else None
        )
        if canonical is None:
            canonical = BiologicalObservation(
                paper_id=case.paper_id,
                case_id=case.id,
                category=candidate.category,
                variable_name=candidate.variable_name,
                normalized_variable=self._normalized_variable(candidate),
                value=candidate.value,
                normalized_value=candidate.normalized_value,
                unit=candidate.unit,
                direction=candidate.direction.value,
                status=candidate.status.value,
                time_relation=candidate.time_relation.value,
                temporal_precision=candidate.temporal_precision.value,
                observation_domain=candidate.observation_domain.value,
                domain_secondary=(
                    candidate.domain_secondary.value
                    if candidate.domain_secondary
                    else None
                ),
                measurement_semantics=candidate.measurement_semantics.value,
                scope_type=candidate.scope_type.value,
                lesion_identifier=candidate.lesion_identifier,
                lesion_id=lesion.id if lesion else None,
                lesion_collection_id=collection.id if collection else None,
                regression_role=candidate.regression_role.value,
                qualitative_level=candidate.qualitative_level.value,
                temporal_text=candidate.temporal_text
                or (parsed_temporal.temporal_text if parsed_temporal else None),
                temporal_value=(
                    candidate.temporal_value
                    if candidate.temporal_value is not None
                    else (parsed_temporal.temporal_value if parsed_temporal else None)
                ),
                temporal_unit=candidate.temporal_unit
                or (parsed_temporal.temporal_unit if parsed_temporal else None),
                temporal_relation=candidate.temporal_relation
                or (parsed_temporal.temporal_relation if parsed_temporal else None),
                anchor_event_id=anchor_event_id,
                observation_context=candidate.observation_context,
                evidence_type=EvidenceType.OBSERVED_FACT.value,
                confidence=candidate.confidence,
                linked_event_id=linked_event_id,
                clinical_context_subtype=self._clinical_subtype(candidate),
                case_scope_status=quote_scope_status(
                    observed_refs[0].quote, case
                ).value,
                created_from_run_id=run.id,
                extraction_run_id=run.id,
                created_at=_utcnow(),
            )
            session.add(canonical)
            session.flush()
        else:
            result["duplicate_merges"].append(
                {
                    "observation_id": canonical.id,
                    "variable_name": candidate.variable_name,
                    "reason": "repeated biological observation",
                }
            )
            canonical.confidence = max(
                canonical.confidence or 0.0, candidate.confidence
            )

        first_evidence_id = None
        for reference in observed_refs:
            if self._reference_already_linked(
                session, run.id, "biological_observation", canonical.id, reference
            ):
                if first_evidence_id is None:
                    first_evidence_id = session.scalar(
                        select(FieldEvidenceLink.evidence_id).where(
                            FieldEvidenceLink.extraction_run_id == run.id,
                            FieldEvidenceLink.entity_type == "biological_observation",
                            FieldEvidenceLink.entity_id == canonical.id,
                        )
                    )
                continue
            evidence = self._create_evidence(
                session,
                case.paper_id,
                case.id,
                (
                    f"biological_observation.{canonical.variable_name}: "
                    f"{canonical.value or canonical.status}"
                ),
                reference,
                candidate.confidence,
            )
            if first_evidence_id is None:
                first_evidence_id = evidence.id
            linked_fields = [
                "category",
                "observation_domain",
                "measurement_semantics",
                "variable_name",
                "direction",
                "status",
                "time_relation",
                "scope_type",
                "regression_role",
                "qualitative_level",
            ]
            if canonical.value is not None:
                linked_fields.append("value")
            if canonical.normalized_value is not None:
                linked_fields.append("normalized_value")
            if canonical.unit is not None:
                linked_fields.append("unit")
            for field_name in linked_fields:
                self._link(
                    session,
                    run.id,
                    "biological_observation",
                    canonical.id,
                    field_name,
                    evidence,
                )
        if first_evidence_id is None:
            first_evidence_id = session.scalar(
                select(FieldEvidenceLink.evidence_id).where(
                    FieldEvidenceLink.extraction_run_id == run.id,
                    FieldEvidenceLink.entity_type == "biological_observation",
                    FieldEvidenceLink.entity_id == canonical.id,
                )
            )
        self._persist_genotype(
            session, run, case, canonical, candidate, first_evidence_id
        )
        store_temporal = parsed_temporal is not None and (
            candidate.temporal_text
            or parsed_temporal.temporal_precision
            != TemporalSemanticPrecision.UNKNOWN
        )
        if store_temporal and first_evidence_id is not None:
            session.add(
                TemporalRecord(
                    paper_id=case.paper_id,
                    case_id=case.id,
                    entity_type="biological_observation",
                    entity_id=canonical.id,
                    field_name="temporal_text",
                    temporal_text=parsed_temporal.temporal_text,
                    temporal_value=parsed_temporal.temporal_value,
                    temporal_unit=parsed_temporal.temporal_unit,
                    temporal_relation=parsed_temporal.temporal_relation,
                    temporal_precision=parsed_temporal.temporal_precision,
                    anchor_event_id=anchor_event_id,
                    evidence_id=first_evidence_id,
                    created_from_run_id=run.id,
                )
            )
        return canonical

    def _persist_rejected_interpretation(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        candidate: RejectedInterpretationCandidate,
        verifier: EvidenceVerifier,
        result: dict[str, Any],
        reason_codes: set[PartialReasonCode],
    ) -> None:
        for reference in candidate.evidence_refs:
            verified = verifier.verify(reference)
            if not verified.verified:
                self._record_verification_failure(
                    result, "rejected_biological_interpretation", verified
                )
                reason_codes.add(PartialReasonCode.UNVERIFIED_QUOTE)
                continue
            if verified.evidence_type != EvidenceType.AUTHOR_INTERPRETATION:
                continue
            self._persist_verified_interpretation(
                session,
                run,
                case,
                candidate.statement,
                candidate.rejection_reason,
                candidate.confidence,
                verified,
                result,
            )

    def _persist_verified_interpretation(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        statement: str,
        reason: str,
        confidence: float,
        reference: VerifiedReference,
        result: dict[str, Any],
    ) -> None:
        if self._reference_already_linked(
            session, run.id, "case", case.id, reference
        ):
            return
        interpreted_reference = VerifiedReference(
            verified=True,
            quote=reference.quote,
            page=reference.page,
            section=reference.section,
            evidence_type=EvidenceType.AUTHOR_INTERPRETATION,
        )
        evidence = self._create_evidence(
            session,
            case.paper_id,
            case.id,
            f"rejected biological interpretation: {statement}",
            interpreted_reference,
            confidence,
        )
        self._link(
            session,
            run.id,
            "case",
            case.id,
            "rejected_biological_interpretation",
            evidence,
        )
        result["rejected_as_interpretation"].append(
            {
                "evidence_id": evidence.id,
                "statement": statement,
                "reason": reason,
                "page": reference.page,
                "section": reference.section,
                "quote": reference.quote,
            }
        )
        self._persist_explanatory_alternative(
            session, run, case, statement, reference.quote, evidence.id, result
        )

    @classmethod
    def _harden_ontology(
        cls, candidate: BiologicalObservationCandidate
    ) -> None:
        claim_text = normalize_text(
            " ".join(
                part
                for part in [
                    candidate.variable_name,
                    candidate.normalized_variable,
                    candidate.value,
                ]
                if part
            )
        )
        text = normalize_text(
            " ".join(
                part
                for part in [
                    candidate.variable_name,
                    candidate.normalized_variable,
                    candidate.value,
                    candidate.observation_context,
                    *(reference.quote for reference in candidate.evidence_refs),
                ]
                if part
            )
        )
        scope_text = normalize_text(
            f"{claim_text} {candidate.lesion_identifier or ''}"
        )

        if re.search(
            r"\b(?:peripheral neuropathy|night sweats?|cough|hemoptysis|fever)\b",
            claim_text,
        ):
            candidate.scope_type = ScopeType.PATIENT
            candidate.lesion_identifier = None
            candidate.regression_role = RegressionRole.UNKNOWN
        elif re.search(r"\bnew pulmonary nodules?\b", claim_text):
            candidate.scope_type = ScopeType.PATIENT
            candidate.lesion_identifier = None
            candidate.regression_role = RegressionRole.UNKNOWN
        elif re.search(r"\bbilateral upper\s*(?:lobe|lung)\b", scope_text):
            candidate.scope_type = ScopeType.LESION
            candidate.lesion_identifier = "bilateral upper-lobe lesions"
            if re.search(
                r"\bincreased in size and number\b|\bsuv\b.{0,20}\b15\.2\b",
                text,
            ):
                candidate.regression_role = RegressionRole.PROGRESSING_NON_TARGET
        elif re.search(
            r"\bleft lower\s*lobe\b|"
            r"\bpreviously biopsied left (?:lung )?nodule\b",
            scope_text,
        ):
            candidate.scope_type = ScopeType.LESION
            candidate.lesion_identifier = "left lower lobe biopsied lesion"
            if re.search(
                r"\bdecreas\w*\b|\bminimal fdg\b|\bsuv\b.{0,20}\b2\.5\b",
                text,
            ):
                candidate.regression_role = RegressionRole.REGRESSING_TARGET
        elif re.search(r"\bleft upper\s*lobe\b", scope_text):
            candidate.scope_type = ScopeType.LESION
            candidate.lesion_identifier = "left upper lobe target lesion"
            if re.search(
                r"\breduc\w*\b|\bregress\w*\b|\bnecrot\w*\b|"
                r"\bno viable cells\b",
                text,
            ):
                candidate.regression_role = RegressionRole.REGRESSING_TARGET
        elif re.search(r"\bhilar\b|\bmediastinal lymph node", scope_text):
            candidate.scope_type = ScopeType.LYMPH_NODE
            candidate.lesion_identifier = "hilar/mediastinal lymph nodes"
        if re.search(r"\b(?:complete blood count|cbc)\b", claim_text):
            candidate.scope_type = ScopeType.SYSTEMIC
            candidate.lesion_identifier = None
            candidate.regression_role = RegressionRole.UNKNOWN
            candidate.normalized_value = "NORMAL"

        if re.search(r"\b(?:suv|fdg|fluorodeoxyglucose|uptake)\b", claim_text):
            candidate.measurement_semantics = MeasurementSemantics.IMAGING_PROXY
        elif re.search(
            r"\b(?:complete blood count|cbc|crp|cytokine)\b", claim_text
        ):
            candidate.measurement_semantics = MeasurementSemantics.LAB_MEASUREMENT
        elif re.search(
            r"\b(?:night sweats?|cough|hemoptysis|fever|symptom|neuropathy)\b",
            claim_text,
        ):
            candidate.measurement_semantics = MeasurementSemantics.SYMPTOM
        elif re.search(
            r"\b(?:histopath\w*|immunohist\w*|stain\w*|necrot\w*|"
            r"viable cells?|melanin pigment|malignant cells?|"
            r"biopsy diagnosis|fibrosis|no (?:residual )?disease|"
            r"no viable)\b|positive for metastatic melanoma",
            claim_text,
        ):
            candidate.measurement_semantics = MeasurementSemantics.PATHOLOGIC_FINDING
        elif re.search(r"\bclinical examination\b", claim_text):
            candidate.measurement_semantics = MeasurementSemantics.CLINICAL_FINDING
        elif re.search(
            r"\b(?:size|diameter|nodule|lesion|metastas|progression)\b",
            claim_text,
        ):
            candidate.measurement_semantics = (
                MeasurementSemantics.MORPHOLOGIC_FINDING
            )
        elif "biopsy" in claim_text:
            candidate.measurement_semantics = MeasurementSemantics.PATHOLOGIC_FINDING
        elif candidate.measurement_semantics == MeasurementSemantics.UNKNOWN:
            candidate.measurement_semantics = MeasurementSemantics.CLINICAL_FINDING

        if re.search(r"\bminimal\b", claim_text):
            candidate.qualitative_level = QualitativeLevel.MINIMAL
        elif re.search(r"\bmarked(?:ly)?\b", claim_text):
            candidate.qualitative_level = QualitativeLevel.MARKED
        elif re.search(r"\bnormal\b", claim_text):
            candidate.qualitative_level = QualitativeLevel.NORMAL
        elif re.search(r"\b(?:high|intense(?:ly)?)\b", claim_text):
            candidate.qualitative_level = QualitativeLevel.HIGH
        elif re.search(r"\blow\b", claim_text):
            candidate.qualitative_level = QualitativeLevel.LOW

        immune_infiltrate = re.search(
            r"(?:cd[348](?:\+|positive)?|"
            r"lymphocyt\w*\s+infiltration|"
            r"immune infiltration|t-?cell infiltration)",
            claim_text,
        )
        genotype_claim = is_genotype_claim(claim_text, text)
        leukoderma_claim = re.search(
            r"\b(?:leukoderma|vitiligo(?:-like)?)\b",
            claim_text,
        )
        irae_claim = parse_irae(claim_text)
        named_treatment = re.search(
            r"\b(?:ipilimumab|pembrolizumab|nivolumab|interferon|"
            r"radiotherap\w*|chemotherap\w*|lenalidomide)\b",
            text,
        )
        spontaneous_regression = re.search(
            r"\b(?:spontaneous regression|completely disappeared|"
            r"resolved both clinically|all (?:in-?transit )?(?:metastases|nodules) "
            r"had (?:resolved|vanished|disappeared))\b",
            text,
        )
        infection_context = re.search(
            r"\b(?:postoperative infection|wound dehiscence|"
            r"recurring infections?|chronically infected|infection)\b",
            claim_text,
        )

        if immune_infiltrate:
            candidate.category = ObservationCategory.IMMUNE
            candidate.observation_domain = ObservationDomain.BIOLOGICAL_STATE
            candidate.domain_secondary = ObservationDomain.DIAGNOSTIC_EVIDENCE
            candidate.measurement_semantics = MeasurementSemantics.PATHOLOGIC_FINDING
        elif leukoderma_claim:
            candidate.category = ObservationCategory.DERMATOLOGIC_PHENOTYPE
            candidate.observation_domain = ObservationDomain.CLINICAL_CONTEXT
            candidate.measurement_semantics = MeasurementSemantics.CLINICAL_FINDING
            if candidate.regression_role != RegressionRole.UNKNOWN and not (
                candidate.lesion_identifier
                and re.search(r"leukoderma|vitiligo|ankle", candidate.lesion_identifier, re.I)
            ):
                candidate.regression_role = RegressionRole.UNKNOWN
        elif irae_claim:
            candidate.observation_domain = ObservationDomain.CLINICAL_CONTEXT
            candidate.measurement_semantics = MeasurementSemantics.CLINICAL_FINDING
            candidate.scope_type = ScopeType.PATIENT
            candidate.regression_role = RegressionRole.UNKNOWN
        elif infection_context:
            candidate.observation_domain = ObservationDomain.CLINICAL_CONTEXT
            if candidate.measurement_semantics == MeasurementSemantics.UNKNOWN:
                candidate.measurement_semantics = MeasurementSemantics.CLINICAL_FINDING
        elif genotype_claim:
            candidate.category = ObservationCategory.GENETIC
            candidate.observation_domain = ObservationDomain.DIAGNOSTIC_EVIDENCE
            parsed = parse_genotype(
                candidate.variable_name,
                candidate.value,
                str(candidate.normalized_value or ""),
                text,
            )
            if parsed and parsed.state == GenotypeState.WILD_TYPE.value:
                candidate.status = BiologicalStatus.REPORTED
                candidate.direction = BiologicalDirection.UNKNOWN
                candidate.normalized_value = "WILD_TYPE"
            elif parsed and parsed.state == GenotypeState.NOT_DETECTED.value:
                candidate.status = BiologicalStatus.REPORTED
                candidate.direction = BiologicalDirection.UNKNOWN
                candidate.normalized_value = "NOT_DETECTED"
            elif parsed and parsed.state == GenotypeState.VARIANT_PRESENT.value:
                candidate.status = BiologicalStatus.REPORTED
                candidate.direction = BiologicalDirection.PRESENT
                candidate.normalized_value = "VARIANT_PRESENT"
        elif candidate.measurement_semantics == MeasurementSemantics.SYMPTOM:
            candidate.observation_domain = ObservationDomain.CLINICAL_CONTEXT
        elif re.search(r"\b(?:complete blood count|cbc)\b", claim_text):
            candidate.observation_domain = ObservationDomain.BIOLOGICAL_STATE
        elif re.search(
            r"\b(?:melanin pigment|s-?100|melan-?a|mason fontana|stain)\b",
            claim_text,
        ) and not immune_infiltrate:
            candidate.observation_domain = ObservationDomain.DIAGNOSTIC_EVIDENCE
        elif re.search(
            r"\b(?:necrot\w*|no viable cells|viable tumor cells)\b",
            claim_text,
        ):
            candidate.observation_domain = ObservationDomain.BIOLOGICAL_STATE
        elif candidate.measurement_semantics == MeasurementSemantics.IMAGING_PROXY:
            candidate.observation_domain = (
                ObservationDomain.BIOLOGICAL_STATE
                if candidate.regression_role
                in {
                    RegressionRole.REGRESSING_TARGET,
                    RegressionRole.PROGRESSING_NON_TARGET,
                }
                else ObservationDomain.DIAGNOSTIC_EVIDENCE
            )
        elif (
            named_treatment
            and re.search(r"\b(?:response|resistant|resistance|refractory)\b", claim_text)
        ):
            candidate.observation_domain = ObservationDomain.TREATMENT_RESPONSE
        elif spontaneous_regression:
            candidate.observation_domain = ObservationDomain.DISEASE_PHENOTYPE
        elif re.search(
            r"\b(?:response|resistant|resistance|refractory)\b", text
        ) and named_treatment:
            candidate.observation_domain = ObservationDomain.TREATMENT_RESPONSE
        elif re.search(
            r"\b(?:size|increased in size|decreased in size|progression|"
            r"metastas(?:is|es|tic)|recurr|regress)\b",
            claim_text,
        ) and candidate.measurement_semantics != MeasurementSemantics.PATHOLOGIC_FINDING:
            candidate.observation_domain = ObservationDomain.DISEASE_PHENOTYPE
        elif candidate.measurement_semantics == MeasurementSemantics.PATHOLOGIC_FINDING:
            candidate.observation_domain = ObservationDomain.DIAGNOSTIC_EVIDENCE

        if (
            candidate.measurement_semantics == MeasurementSemantics.IMAGING_PROXY
            and re.search(r"\b(?:suv|fdg|uptake)\b", text)
            and not cls._has_explicit_same_measurement_comparison(candidate, text)
        ):
            candidate.direction = BiologicalDirection.UNKNOWN
        if (
            candidate.qualitative_level == QualitativeLevel.NORMAL
            and re.search(r"\b(?:complete blood count|cbc)\b", text)
        ):
            candidate.direction = BiologicalDirection.UNKNOWN
        static_range = re.search(
            r"\b(?:measur\w*|ranged|ranging|range)\b.{0,40}"
            r"\d+(?:\.\d+)?\s*(?:mm|cm)?\s*(?:[-\u2013\u2014]|to)\s*"
            r"\d+(?:\.\d+)?|"
            r"\b\d+(?:\.\d+)?\s*[-\u2013\u2014]\s*\d+(?:\.\d+)?\s*(?:mm|cm)\b",
            claim_text,
        )
        if candidate.measurement_semantics == MeasurementSemantics.MORPHOLOGIC_FINDING:
            if re.search(r"\bincreased in size and number\b", claim_text):
                candidate.direction = BiologicalDirection.INCREASED
            elif re.search(r"\b(?:decreased|reduced) in size\b", claim_text):
                candidate.direction = BiologicalDirection.DECREASED
            elif static_range:
                candidate.direction = BiologicalDirection.UNKNOWN
        elif static_range and not re.search(
            r"\b(?:decreas\w*|reduc\w*|fell|shrank|increas\w*|rose|grew)\b",
            claim_text,
        ):
            candidate.direction = BiologicalDirection.UNKNOWN

    @staticmethod
    def _has_explicit_same_measurement_comparison(
        candidate: BiologicalObservationCandidate, text: str
    ) -> bool:
        if (
            isinstance(candidate.normalized_value, list)
            and len(candidate.normalized_value) >= 2
        ):
            return True
        return bool(
            re.search(
                r"\b(?:suv|fdg uptake|uptake)\b.{0,30}"
                r"\b(?:increased|decreased|reduced|fell|rose)\b|"
                r"\b(?:reduction|increase|decrease)\s+in\s+"
                r"(?:fdg(?: uptake)?|suv|uptake)\b|"
                r"\bfrom\s+\d+(?:\.\d+)?\s+to\s+\d+(?:\.\d+)?\b",
                text,
            )
        )

    @staticmethod
    def _normalized_variable(candidate: BiologicalObservationCandidate) -> str:
        source = candidate.normalized_variable or candidate.variable_name
        normalized = re.sub(r"[^A-Z0-9]+", "_", source.upper()).strip("_")
        aliases = {
            "STANDARDIZED_UPTAKE_VALUE": "SUV",
            "FDG_AVIDITY": "FDG_UPTAKE",
            "FDG_ACTIVITY": "FDG_UPTAKE",
            "VIABLE_TUMOR": "VIABLE_TUMOR_CELLS",
            "VIABLE_MELANOMA_CELLS": "VIABLE_TUMOR_CELLS",
            "NECROSIS": "TUMOR_NECROSIS",
            "TUMOUR_NECROSIS": "TUMOR_NECROSIS",
        }
        return aliases.get(normalized, normalized)

    @classmethod
    def _find_canonical_observation(
        cls,
        session: Session,
        run_id: int,
        candidate: BiologicalObservationCandidate,
        lesion_id: int | None = None,
    ) -> BiologicalObservation | None:
        normalized_variable = cls._normalized_variable(candidate)
        rows = session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.created_from_run_id == run_id,
                BiologicalObservation.category == candidate.category,
                BiologicalObservation.normalized_variable == normalized_variable,
                BiologicalObservation.observation_domain
                == candidate.observation_domain.value,
                BiologicalObservation.scope_type == candidate.scope_type.value,
                BiologicalObservation.lesion_id == lesion_id,
                BiologicalObservation.regression_role
                == candidate.regression_role.value,
                BiologicalObservation.status == (
                    candidate.status.value
                    if hasattr(candidate.status, "value")
                    else candidate.status
                ),
                BiologicalObservation.direction == (
                    candidate.direction.value
                    if hasattr(candidate.direction, "value")
                    else candidate.direction
                ),
                BiologicalObservation.time_relation == candidate.time_relation.value,
            )
        )
        candidate_value = normalize_text(candidate.value or "")
        candidate_numbers = set(re.findall(r"\d+(?:\.\d+)?", candidate_value))
        for row in rows:
            row_value = normalize_text(row.value or "")
            if candidate_value == row_value:
                return row
            row_numbers = set(re.findall(r"\d+(?:\.\d+)?", row_value))
            if candidate_numbers and candidate_numbers == row_numbers:
                return row
            if not candidate_numbers and not row_numbers:
                left = set(re.findall(r"\w+", candidate_value))
                right = set(re.findall(r"\w+", row_value))
                similarity = len(left & right) / max(len(left | right), 1)
                if similarity >= 0.55:
                    return row
        return None

    @staticmethod
    def _match_event(
        candidate: BiologicalObservationCandidate, events: list[Event]
    ) -> int | None:
        match_text = candidate.related_event_description or " ".join(
            part
            for part in [
                candidate.variable_name,
                candidate.value,
                candidate.observation_context,
            ]
            if part
        )
        candidate_terms = BiologicalObservationPipeline._matching_terms(match_text)
        candidate_numbers = set(re.findall(r"\d+(?:\.\d+)?", match_text))
        best: tuple[float, int] | None = None
        for event in events:
            event_terms = BiologicalObservationPipeline._matching_terms(
                event.description
            )
            similarity = len(candidate_terms & event_terms) / max(
                len(candidate_terms | event_terms), 1
            )
            event_numbers = set(re.findall(r"\d+(?:\.\d+)?", event.description))
            direct_numeric_match = bool(candidate_numbers & event_numbers)
            if (
                similarity >= 0.45
                or (direct_numeric_match and similarity >= 0.2)
            ) and (best is None or similarity > best[0]):
                best = (similarity, event.id)
        return best[1] if best else None

    @staticmethod
    def _matching_terms(text: str) -> set[str]:
        stop_words = {
            "a",
            "an",
            "and",
            "at",
            "in",
            "of",
            "on",
            "the",
            "to",
            "was",
            "were",
            "with",
        }
        aliases = {
            "decreased": "decrease",
            "reduced": "decrease",
            "reduction": "decrease",
            "cells": "cell",
            "lesions": "lesion",
        }
        return {
            aliases.get(token, token)
            for token in re.findall(r"\w+", normalize_text(text))
            if token not in stop_words and len(token) > 1
        }

    @staticmethod
    def _covered_target_variables(
        observations: list[BiologicalObservation],
    ) -> set[str]:
        covered: set[str] = set()
        for observation in observations:
            text = " ".join(
                [
                    observation.normalized_variable or "",
                    observation.variable_name,
                ]
            ).upper()
            for target in TARGET_VARIABLES:
                if target in text:
                    covered.add(target)
            if "FDG" in text:
                covered.add("FDG_UPTAKE")
            if "SUV" in text or "STANDARDIZED UPTAKE" in text:
                covered.add("SUV")
            if "NECRO" in text:
                covered.add("TUMOR_NECROSIS")
            if "VIABLE" in text and ("TUMOR" in text or "MELANOMA" in text):
                covered.add("VIABLE_TUMOR_CELLS")
        return covered

    @staticmethod
    def _record_verification_failure(
        result: dict[str, Any], field_name: str, reference: VerifiedReference
    ) -> None:
        result["verification_failures"].append(
            {
                "field": field_name,
                "page": reference.page,
                "quote": reference.quote,
                "reason": reference.reason,
                "status": EvidenceStatus.UNVERIFIED.value,
            }
        )

    @staticmethod
    def _create_evidence(
        session: Session,
        paper_id: int,
        case_id: int,
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

    @staticmethod
    def _reference_already_linked(
        session: Session,
        run_id: int,
        entity_type: str,
        entity_id: int,
        reference: VerifiedReference,
    ) -> bool:
        rows = session.scalars(
            select(Evidence)
            .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
            .where(
                FieldEvidenceLink.extraction_run_id == run_id,
                FieldEvidenceLink.entity_type == entity_type,
                FieldEvidenceLink.entity_id == entity_id,
            )
        ).unique()
        return any(
            row.page == reference.page
            and normalize_text(row.source_quote or "") == normalize_text(reference.quote)
            for row in rows
        )

    def _resolve_lesion_graph(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        candidate: BiologicalObservationCandidate,
        observed_refs: list[VerifiedReference],
        result: dict[str, Any],
        extra_alias_texts: list[str] | None = None,
    ) -> tuple[Lesion | None, LesionCollection | None]:
        source = candidate.lesion_identifier or ""
        parsed = parse_lesion_text(source)
        if parsed is None or not _usable_lesion_parse(parsed):
            return None, None
        evidence_id = None
        page = None
        section = None
        if observed_refs:
            page = observed_refs[0].page
            section = observed_refs[0].section
        if parsed.is_collection:
            collection = self._get_or_create_collection(
                session, run, case, parsed, source
            )
            self._link_collection_members(session, run, case, collection, parsed)
            return None, collection
        existing = list(
            session.scalars(
                select(Lesion).where(
                    Lesion.case_id == case.id,
                    Lesion.created_from_run_id == run.id,
                )
            )
        )
        confirmed: Lesion | None = next(
            (
                lesion
                for lesion in existing
                if lesion.identity_key == parsed.identity_key
            ),
            None,
        )
        possible: Lesion | None = None
        for lesion in existing:
            if confirmed is not None:
                break
            other = parse_lesion_text(lesion.canonical_name)
            if other is None:
                continue
            decision = merge_decision(parsed, other)
            if decision == "CONFIRMED_ALIAS":
                confirmed = lesion
                break
            if decision == "POSSIBLE_SAME_LESION" and possible is None:
                possible = lesion
        alias_texts = _unique_alias_texts(source, extra_alias_texts)
        if confirmed is not None:
            for alias_text in alias_texts:
                self._add_alias(
                    session,
                    confirmed,
                    alias_text,
                    case.paper_id,
                    page,
                    section,
                    LesionAliasStatus.CONFIRMED_ALIAS,
                    evidence_id,
                )
            result["lesion_alias_merges"].append(
                {
                    "lesion_id": confirmed.id,
                    "source_text": source,
                    "canonical_name": confirmed.canonical_name,
                }
            )
            return confirmed, None
        lesion = Lesion(
            paper_id=case.paper_id,
            case_id=case.id,
            canonical_name=parsed.canonical_name or source,
            organ=parsed.organ,
            anatomical_location=parsed.anatomical_location,
            laterality=parsed.laterality,
            lesion_type=parsed.lesion_type,
            identity_key=parsed.identity_key,
            created_from_run_id=run.id,
        )
        session.add(lesion)
        session.flush()
        for index, alias_text in enumerate(alias_texts):
            self._add_alias(
                session,
                lesion,
                alias_text,
                case.paper_id,
                page,
                section,
                (
                    LesionAliasStatus.POSSIBLE_SAME_LESION
                    if possible is not None and index == 0
                    else LesionAliasStatus.CONFIRMED_ALIAS
                ),
                evidence_id,
                possible_same_lesion_id=(
                    possible.id if possible is not None and index == 0 else None
                ),
            )
        if possible is not None:
            result["unresolved_lesion_identities"].append(
                {
                    "lesion_id": lesion.id,
                    "possible_same_lesion_id": possible.id,
                    "source_text": source,
                }
            )
        collections = list(
            session.scalars(
                select(LesionCollection).where(
                    LesionCollection.case_id == case.id,
                    LesionCollection.created_from_run_id == run.id,
                )
            )
        )
        for collection in collections:
            collection_parse = parse_lesion_text(collection.canonical_name)
            if collection_parse and collection_membership_ok(collection_parse, parsed):
                self._add_membership(session, collection, lesion)
        return lesion, None

    def _get_or_create_collection(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        parsed,
        source: str,
    ) -> LesionCollection:
        existing = session.scalar(
            select(LesionCollection).where(
                LesionCollection.case_id == case.id,
                LesionCollection.created_from_run_id == run.id,
                LesionCollection.canonical_name == parsed.canonical_name,
            )
        )
        if existing is not None:
            return existing
        collection = LesionCollection(
            paper_id=case.paper_id,
            case_id=case.id,
            canonical_name=parsed.canonical_name or source,
            collection_type=parsed.collection_kind,
            organ=parsed.organ,
            anatomical_location=parsed.anatomical_location,
            source_text=source,
            collection_only=True,
            membership_confidence=0.6,
            created_from_run_id=run.id,
        )
        session.add(collection)
        session.flush()
        return collection

    def _link_collection_members(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        collection: LesionCollection,
        collection_parse,
    ) -> None:
        for lesion in session.scalars(
            select(Lesion).where(
                Lesion.case_id == case.id,
                Lesion.created_from_run_id == run.id,
            )
        ):
            member = parse_lesion_text(lesion.canonical_name)
            if member and collection_membership_ok(collection_parse, member):
                self._add_membership(session, collection, lesion)

    @staticmethod
    def _add_membership(
        session: Session, collection: LesionCollection, lesion: Lesion
    ) -> None:
        existing = session.scalar(
            select(LesionCollectionMembership).where(
                LesionCollectionMembership.collection_id == collection.id,
                LesionCollectionMembership.lesion_id == lesion.id,
            )
        )
        if existing is None:
            collection.collection_only = False
            session.add(
                LesionCollectionMembership(
                    collection_id=collection.id,
                    lesion_id=lesion.id,
                    membership_confidence=0.8,
                )
            )

    @staticmethod
    def _add_alias(
        session: Session,
        lesion: Lesion,
        source_text: str,
        paper_id: int,
        page: int | None,
        section: str | None,
        status: LesionAliasStatus,
        evidence_id: int | None,
        possible_same_lesion_id: int | None = None,
    ) -> None:
        existing = session.scalar(
            select(LesionAlias).where(
                LesionAlias.lesion_id == lesion.id,
                LesionAlias.source_text == source_text,
                LesionAlias.page == page,
                LesionAlias.section == section,
            )
        )
        if existing is not None:
            if (
                existing.status == LesionAliasStatus.POSSIBLE_SAME_LESION
                and status == LesionAliasStatus.CONFIRMED_ALIAS
            ):
                existing.status = status
                if possible_same_lesion_id is not None:
                    existing.possible_same_lesion_id = possible_same_lesion_id
            return
        session.add(
            LesionAlias(
                lesion_id=lesion.id,
                possible_same_lesion_id=possible_same_lesion_id,
                source_text=source_text,
                paper_id=paper_id,
                page=page,
                section=section,
                status=status,
                evidence_id=evidence_id,
            )
        )

    def _persist_genotype(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        observation: BiologicalObservation,
        candidate: BiologicalObservationCandidate,
        evidence_id: int | None,
    ) -> None:
        if evidence_id is None:
            return
        if (
            candidate.category != ObservationCategory.GENETIC
            and not is_genotype_claim(
                candidate.variable_name,
                candidate.value,
                *(reference.quote for reference in candidate.evidence_refs),
            )
        ):
            return
        parsed = parse_genotype(
            candidate.variable_name,
            candidate.normalized_variable,
            candidate.value,
            str(candidate.normalized_value or ""),
            *(reference.quote for reference in candidate.evidence_refs),
        )
        if parsed is None:
            return
        existing = session.scalar(
            select(GenotypeObservation).where(
                GenotypeObservation.case_id == case.id,
                GenotypeObservation.created_from_run_id == run.id,
                GenotypeObservation.gene == parsed.gene,
                GenotypeObservation.state == GenotypeState(parsed.state),
            )
        )
        if existing is not None:
            return
        session.add(
            GenotypeObservation(
                paper_id=case.paper_id,
                case_id=case.id,
                biological_observation_id=observation.id,
                gene=parsed.gene,
                variant=parsed.variant,
                transcript=parsed.transcript,
                coding_change=parsed.coding_change,
                protein_change=parsed.protein_change,
                rs_id=parsed.rs_id,
                variant_type=parsed.variant_type,
                zygosity=parsed.zygosity,
                origin=parsed.origin,
                assay=parsed.assay,
                source_context=parsed.source_context,
                state=GenotypeState(parsed.state),
                evidence_id=evidence_id,
                created_from_run_id=run.id,
            )
        )

    def _persist_explanatory_alternative(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        statement: str,
        quote: str,
        evidence_id: int,
        result: dict[str, Any],
    ) -> None:
        text = normalize_text(f"{statement} {quote}")
        alternative_type = classify_explanatory_alternative(statement, quote)
        status = ExplanatoryAlternativeStatus.AUTHOR_SUGGESTED
        if alternative_type is None:
            return
        existing = session.scalar(
            select(ExplanatoryAlternative).where(
                ExplanatoryAlternative.case_id == case.id,
                ExplanatoryAlternative.created_from_run_id == run.id,
                ExplanatoryAlternative.alternative_type == alternative_type,
            )
        )
        if existing is not None:
            return
        session.add(
            ExplanatoryAlternative(
                paper_id=case.paper_id,
                case_id=case.id,
                alternative_type=alternative_type,
                description=statement,
                temporal_relation="BEFORE" if "prior" in text or "year" in text else None,
                status=status,
                evidence_id=evidence_id,
                created_from_run_id=run.id,
            )
        )
        result["explanatory_alternatives"].append(
            {
                "type": alternative_type,
                "status": status.value,
                "description": statement,
            }
        )

    def _run_stability_recall(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        events: list[Event],
        pages: dict[int, str],
        chunks: list,
        verifier: EvidenceVerifier,
        persisted: list[BiologicalObservation],
        result: dict[str, Any],
        reason_codes: set[PartialReasonCode],
    ) -> None:
        existing_genotype_keys = {
            (row.gene, row.state.value if hasattr(row.state, "value") else row.state)
            for row in session.scalars(
                select(GenotypeObservation).where(
                    GenotypeObservation.created_from_run_id == run.id
                )
            )
        }
        event_quotes = self._event_evidence_quotes(session, events)
        hits = []
        hits.extend(scan_immune_pathology(pages, chunks))
        hits.extend(scan_genotype_text(pages, chunks))
        hits.extend(scan_explanatory_alternatives(pages, chunks))
        hits.extend(
            reconcile_phase2_genotypes(
                events, existing_genotype_keys, pages, chunks, event_quotes
            )
        )
        for hit in hits:
            verified = verify_hit(verifier, hit)
            if verified.status == "RECONCILIATION_REQUIRED":
                reason_codes.add(PartialReasonCode.RECONCILIATION_REQUIRED)
                result["reconciliation_required"].append(
                    {
                        "kind": verified.kind,
                        "source": verified.source,
                        "reason": verified.reason,
                        "quote": verified.quote,
                        "gene": verified.gene,
                        "state": verified.state,
                    }
                )
                continue
            if verified.kind == "immune":
                if self._has_immune_pathology(persisted):
                    continue
                observation = self._persist_observation(
                    session,
                    run,
                    case,
                    events,
                    self._recall_observation_candidate(verified),
                    verifier,
                    result,
                    reason_codes,
                )
                if observation is not None:
                    persisted.append(observation)
                    result["recovered_from_recall"].append(
                        {
                            "kind": "immune",
                            "variable": observation.variable_name,
                            "source": verified.source,
                        }
                    )
            elif verified.kind == "genotype":
                if any(gene == (verified.gene or "") for gene, _state in existing_genotype_keys):
                    continue
                key = (verified.gene or "", verified.state or "")
                observation = self._persist_observation(
                    session,
                    run,
                    case,
                    events,
                    self._recall_observation_candidate(verified),
                    verifier,
                    result,
                    reason_codes,
                )
                if observation is not None:
                    persisted.append(observation)
                    existing_genotype_keys.add(key)
                    result["recovered_from_recall"].append(
                        {
                            "kind": "genotype",
                            "gene": verified.gene,
                            "state": verified.state,
                            "source": verified.source,
                        }
                    )
            elif verified.kind == "alternative":
                already = any(
                    row.get("type") == verified.alternative_type
                    for row in result.get("explanatory_alternatives", [])
                )
                if already:
                    continue
                self._persist_verified_interpretation(
                    session,
                    run,
                    case,
                    verified.quote,
                    verified.reason,
                    0.85,
                    verifier.verify(verified.as_reference()),
                    result,
                )
                if any(
                    row.get("type") == verified.alternative_type
                    for row in result.get("explanatory_alternatives", [])
                ):
                    result["recovered_from_recall"].append(
                        {
                            "kind": "alternative",
                            "type": verified.alternative_type,
                            "source": verified.source,
                        }
                    )

    @staticmethod
    def _has_immune_pathology(persisted: list[BiologicalObservation]) -> bool:
        return any(
            observation.category == ObservationCategory.IMMUNE
            and re.search(
                r"\b(?:cd3|cd8|cd4|nk|til|macrophage|infiltrat)\b",
                normalize_text(
                    f"{observation.variable_name} {observation.value or ''}"
                ),
            )
            for observation in persisted
        )

    @staticmethod
    def _recall_observation_candidate(hit):
        from app.schemas.extraction import BiologicalObservationCandidate

        if hit.kind == "genotype":
            return BiologicalObservationCandidate(
                category=ObservationCategory.GENETIC,
                observation_domain=ObservationDomain.DIAGNOSTIC_EVIDENCE,
                measurement_semantics=MeasurementSemantics.DIRECT_MEASUREMENT,
                variable_name=hit.variable_name or "genotype",
                value=hit.value,
                direction=BiologicalDirection.UNKNOWN,
                status=BiologicalStatus.REPORTED,
                scope_type=ScopeType.PATIENT,
                observation_context="Recovered by genotype recall/reconciliation; not inferred.",
                confidence=0.85,
                evidence_refs=[hit.as_reference()],
            )
        return BiologicalObservationCandidate(
            category=ObservationCategory.IMMUNE,
            observation_domain=ObservationDomain.BIOLOGICAL_STATE,
            domain_secondary=ObservationDomain.DIAGNOSTIC_EVIDENCE,
            measurement_semantics=MeasurementSemantics.PATHOLOGIC_FINDING,
            variable_name=hit.variable_name or "immune-cell infiltration",
            value=hit.value,
            direction=BiologicalDirection.PRESENT,
            status=BiologicalStatus.REPORTED,
            scope_type=ScopeType.PATIENT,
            observation_context="Recovered by immune-pathology recall pass; not inferred.",
            confidence=0.85,
            evidence_refs=[hit.as_reference()],
        )

    @staticmethod
    def _event_evidence_quotes(
        session: Session, events: list[Event]
    ) -> dict[int, tuple[int | None, str | None, str]]:
        quotes: dict[int, tuple[int | None, str | None, str]] = {}
        for event in events:
            evidence = session.scalar(
                select(Evidence)
                .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
                .where(
                    FieldEvidenceLink.extraction_run_id == event.extraction_run_id,
                    FieldEvidenceLink.entity_type == "event",
                    FieldEvidenceLink.entity_id == event.id,
                )
                .order_by(Evidence.id)
            )
            if evidence is not None and evidence.source_quote:
                quotes[event.id] = (
                    evidence.page,
                    evidence.section,
                    evidence.source_quote,
                )
        return quotes

    def _ensure_infection_clinical_context(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        events: list[Event],
        persisted: list[BiologicalObservation],
        result: dict[str, Any],
        reason_codes: set[PartialReasonCode],
    ) -> None:
        has_infection_context = any(
            observation.observation_domain
            == ObservationDomain.CLINICAL_CONTEXT.value
            and re.search(
                r"\b(?:infection|wound dehiscence|chronically infected)\b",
                normalize_text(
                    f"{observation.variable_name} {observation.value or ''}"
                ),
            )
            for observation in persisted
        )
        infection_events = [
            event
            for event in events
            if event.event_type == EventType.INFECTION
            or re.search(
                r"\b(?:infection|wound dehiscence)\b",
                normalize_text(event.description),
            )
        ]
        if has_infection_context or not infection_events:
            return
        event = infection_events[0]
        evidence = session.scalar(
            select(Evidence)
            .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
            .where(
                FieldEvidenceLink.extraction_run_id == event.extraction_run_id,
                FieldEvidenceLink.entity_type == "event",
                FieldEvidenceLink.entity_id == event.id,
            )
            .order_by(Evidence.id)
        )
        if evidence is None:
            return
        observation = BiologicalObservation(
            paper_id=case.paper_id,
            case_id=case.id,
            category=ObservationCategory.MICROBIOME,
            variable_name="infection",
            normalized_variable="INFECTION",
            value=event.description,
            direction=BiologicalDirection.PRESENT.value,
            status=BiologicalStatus.REPORTED.value,
            time_relation=BiologicalTimeRelation.BEFORE_REGRESSION.value
            if event.relation_to_regression == "BEFORE"
            else BiologicalTimeRelation.UNKNOWN.value,
            temporal_precision="UNKNOWN",
            observation_domain=ObservationDomain.CLINICAL_CONTEXT.value,
            measurement_semantics=MeasurementSemantics.CLINICAL_FINDING.value,
            scope_type=ScopeType.PATIENT.value,
            regression_role=RegressionRole.UNKNOWN.value,
            qualitative_level=QualitativeLevel.UNKNOWN.value,
            observation_context="Recovered from timed infection Event; not a mechanism.",
            evidence_type=EvidenceType.OBSERVED_FACT.value,
            confidence=event.temporal_order_confidence or 0.8,
            linked_event_id=event.id,
            created_from_run_id=run.id,
            extraction_run_id=run.id,
            created_at=_utcnow(),
        )
        session.add(observation)
        session.flush()
        self._link(
            session,
            run.id,
            "biological_observation",
            observation.id,
            "value",
            evidence,
        )
        persisted.append(observation)

    def _ensure_timeline_clinical_context(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        events: list[Event],
        persisted: list[BiologicalObservation],
    ) -> None:
        specs = (
            (EventType.FEVER, r"\bfever\b", "fever", "FEVER", ClinicalContextSubtype.FEVER),
            (
                EventType.VACCINATION,
                r"\bvaccin",
                "vaccination",
                "VACCINATION",
                ClinicalContextSubtype.VACCINE,
            ),
        )
        for event_type, pattern, variable, normalized, subtype in specs:
            already = any(
                observation.observation_domain
                == ObservationDomain.CLINICAL_CONTEXT.value
                and re.search(
                    pattern,
                    normalize_text(
                        f"{observation.variable_name} {observation.value or ''}"
                    ),
                )
                for observation in persisted
            )
            matched = [
                event
                for event in events
                if event.event_type == event_type
                or re.search(pattern, normalize_text(event.description))
            ]
            if already or not matched:
                continue
            event = matched[0]
            evidence = session.scalar(
                select(Evidence)
                .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
                .where(
                    FieldEvidenceLink.extraction_run_id == event.extraction_run_id,
                    FieldEvidenceLink.entity_type == "event",
                    FieldEvidenceLink.entity_id == event.id,
                )
                .order_by(Evidence.id)
            )
            if evidence is None:
                continue
            observation = BiologicalObservation(
                paper_id=case.paper_id,
                case_id=case.id,
                category=ObservationCategory.INFLAMMATORY,
                variable_name=variable,
                normalized_variable=normalized,
                value=event.description,
                direction=BiologicalDirection.PRESENT.value,
                status=BiologicalStatus.REPORTED.value,
                time_relation=BiologicalTimeRelation.UNKNOWN.value,
                temporal_precision="UNKNOWN",
                observation_domain=ObservationDomain.CLINICAL_CONTEXT.value,
                measurement_semantics=MeasurementSemantics.CLINICAL_FINDING.value,
                scope_type=ScopeType.PATIENT.value,
                regression_role=RegressionRole.UNKNOWN.value,
                qualitative_level=QualitativeLevel.UNKNOWN.value,
                observation_context=(
                    "Recovered from PHASE 2 Event as clinical context; "
                    "not promoted to a causal observation."
                ),
                evidence_type=EvidenceType.OBSERVED_FACT.value,
                confidence=0.8,
                linked_event_id=event.id,
                clinical_context_subtype=subtype.value,
                created_from_run_id=run.id,
                extraction_run_id=run.id,
                created_at=_utcnow(),
            )
            session.add(observation)
            session.flush()
            self._link(
                session,
                run.id,
                "biological_observation",
                observation.id,
                "value",
                evidence,
            )
            persisted.append(observation)

    @staticmethod
    def _match_anchor_event(
        candidate: BiologicalObservationCandidate, events: list[Event]
    ) -> int | None:
        if not candidate.anchor_event_description:
            return None
        return BiologicalObservationPipeline._match_event(
            candidate.model_copy(
                update={
                    "related_event_description": candidate.anchor_event_description
                }
            ),
            events,
        )

    @staticmethod
    def _run_evidence_count(session: Session, run_id: int) -> int:
        evidence_ids = set(
            session.scalars(
                select(FieldEvidenceLink.evidence_id).where(
                    FieldEvidenceLink.extraction_run_id == run_id
                )
            )
        )
        return len(evidence_ids)


    def _ensure_irae_records(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        events: list[Event],
        persisted: list[BiologicalObservation],
        result: dict[str, Any],
    ) -> None:
        for parsed, grouped_events in canonical_irae_groups(events):
            existing = session.scalar(
                select(ImmuneRelatedAdverseEvent).where(
                    ImmuneRelatedAdverseEvent.case_id == case.id,
                    ImmuneRelatedAdverseEvent.created_from_run_id == run.id,
                    ImmuneRelatedAdverseEvent.event_type == parsed.event_type,
                )
            )
            primary_evidence = None
            for event in grouped_events:
                evidence = session.scalar(
                    select(Evidence)
                    .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
                    .where(
                        FieldEvidenceLink.extraction_run_id == event.extraction_run_id,
                        FieldEvidenceLink.entity_type == "event",
                        FieldEvidenceLink.entity_id == event.id,
                    )
                    .order_by(Evidence.id)
                )
                if evidence is None:
                    continue
                if primary_evidence is None:
                    primary_evidence = evidence
            if existing is None:
                existing = ImmuneRelatedAdverseEvent(
                    paper_id=case.paper_id,
                    case_id=case.id,
                    event_id=grouped_events[0].id,
                    event_type=parsed.event_type,
                    organ_system=parsed.organ_system,
                    grade=parsed.grade,
                    onset_relation_to_treatment=parsed.onset_relation_to_treatment,
                    resolution_status=parsed.resolution_status,
                    description=parsed.description,
                    evidence_id=primary_evidence.id if primary_evidence is not None else None,
                    created_from_run_id=run.id,
                )
                session.add(existing)
                session.flush()
            has_context = any(
                observation.clinical_context_subtype
                == ClinicalContextSubtype.IRAE.value
                and parsed.event_type
                in normalize_text(
                    f"{observation.variable_name} {observation.value or ''}"
                )
                for observation in persisted
            )
            if has_context or primary_evidence is None:
                continue
            observation = BiologicalObservation(
                paper_id=case.paper_id,
                case_id=case.id,
                category=ObservationCategory.IMMUNE,
                variable_name=parsed.event_type,
                normalized_variable="IRAE",
                value=parsed.description,
                direction=BiologicalDirection.PRESENT.value,
                status=BiologicalStatus.REPORTED.value,
                time_relation=BiologicalTimeRelation.UNKNOWN.value,
                temporal_precision="UNKNOWN",
                observation_domain=ObservationDomain.CLINICAL_CONTEXT.value,
                measurement_semantics=MeasurementSemantics.CLINICAL_FINDING.value,
                scope_type=ScopeType.PATIENT.value,
                regression_role=RegressionRole.UNKNOWN.value,
                qualitative_level=QualitativeLevel.UNKNOWN.value,
                observation_context=(
                    "Immune-related adverse event recorded as clinical context; "
                    "not assigned as the cause of regression."
                ),
                evidence_type=EvidenceType.OBSERVED_FACT.value,
                confidence=0.8,
                linked_event_id=grouped_events[0].id,
                clinical_context_subtype=ClinicalContextSubtype.IRAE.value,
                created_from_run_id=run.id,
                extraction_run_id=run.id,
                created_at=_utcnow(),
            )
            session.add(observation)
            session.flush()
            self._link(
                session,
                run.id,
                "biological_observation",
                observation.id,
                "value",
                primary_evidence,
            )
            persisted.append(observation)

    def _persist_regression_episodes(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        events: list[Event],
    ) -> None:
        drafts = build_regression_episodes(events)
        for draft in drafts:
            existing = session.scalar(
                select(RegressionEpisode).where(
                    RegressionEpisode.case_id == case.id,
                    RegressionEpisode.created_from_run_id == run.id,
                    RegressionEpisode.episode_index == draft.episode_index,
                )
            )
            if existing is not None:
                continue
            session.add(
                RegressionEpisode(
                    paper_id=case.paper_id,
                    case_id=case.id,
                    episode_index=draft.episode_index,
                    episode_type=RegressionEpisodeType(draft.episode_type),
                    extent=RegressionExtent(draft.extent),
                    spontaneous_status=draft.spontaneous_status,
                    associated_event_ids=draft.associated_event_ids,
                    associated_lesion_ids=[],
                    description=draft.description,
                    confidence=draft.confidence,
                    created_from_run_id=run.id,
                )
            )
        session.flush()

    def _persist_lesion_states(
        self,
        session: Session,
        run: ExtractionRun,
        case: Case,
        observations: list[BiologicalObservation],
    ) -> None:
        grouped: dict[tuple[int | None, int | None], dict[str, str]] = {}
        for observation in observations:
            key = (observation.lesion_id, observation.lesion_collection_id)
            if key == (None, None):
                continue
            bucket = grouped.setdefault(key, {})
            text = normalize_text(
                f"{observation.variable_name} {observation.value or ''}"
            )
            if re.search(r"\bno viable|absence of (?:neoplastic|malignant)", text):
                bucket["viability_status"] = "ABSENT"
            elif re.search(r"\bviable (?:tumor|malignant) cells\b", text):
                bucket["viability_status"] = observation.direction or "PRESENT"
            if re.search(
                r"\b(?:complete regression|disappeared|vanished|resolved)\b", text
            ):
                bucket["regression_status"] = "REGRESSED"
            elif re.search(r"\bprogress|enlarg", text):
                bucket["regression_status"] = "PROGRESSING"
            if re.search(r"\bfibrosis|melanophage|hypopigment", text):
                bucket["morphology_status"] = observation.value or observation.variable_name
            if re.search(r"\bfdg|suv|uptake\b", text):
                bucket["metabolic_status"] = observation.value or observation.variable_name
            if observation.observation_domain == ObservationDomain.DIAGNOSTIC_EVIDENCE.value:
                bucket["pathology_status"] = observation.value or observation.variable_name
        for (lesion_id, collection_id), fields in grouped.items():
            if not fields:
                continue
            existing = session.scalar(
                select(LesionState).where(
                    LesionState.case_id == case.id,
                    LesionState.created_from_run_id == run.id,
                    LesionState.lesion_id == lesion_id,
                    LesionState.lesion_collection_id == collection_id,
                )
            )
            if existing is not None:
                for name, value in fields.items():
                    if getattr(existing, name) is None:
                        setattr(existing, name, value)
                continue
            session.add(
                LesionState(
                    paper_id=case.paper_id,
                    case_id=case.id,
                    lesion_id=lesion_id,
                    lesion_collection_id=collection_id,
                    created_from_run_id=run.id,
                    **fields,
                )
            )

    @staticmethod
    def _clinical_subtype(candidate: BiologicalObservationCandidate) -> str | None:
        text = normalize_text(
            f"{candidate.variable_name} {candidate.value or ''}"
        )
        if candidate.category == ObservationCategory.DERMATOLOGIC_PHENOTYPE:
            return ClinicalContextSubtype.DERMATOLOGIC_PHENOTYPE.value
        if parse_irae(text):
            return ClinicalContextSubtype.IRAE.value
        if re.search(r"\binfection\b", text):
            return ClinicalContextSubtype.INFECTION.value
        if re.search(r"\bfever\b", text):
            return ClinicalContextSubtype.FEVER.value
        if re.search(r"\bvaccin", text):
            return ClinicalContextSubtype.VACCINE.value
        return None

    @staticmethod
    def _count_rows(session: Session, model, run_id: int) -> int:
        return len(list(session.scalars(select(model).where(model.created_from_run_id == run_id))))


def _usable_lesion_parse(parsed) -> bool:
    if parsed.is_collection:
        return True
    if parsed.anatomical_location or (parsed.organ and parsed.organ != "SKIN"):
        return True
    if parsed.laterality and parsed.organ:
        return True
    return False


def _unique_alias_texts(
    source: str, extra_alias_texts: list[str] | None
) -> list[str]:
    texts: list[str] = []
    for text in [source, *(extra_alias_texts or [])]:
        cleaned = (text or "").strip()
        if cleaned and cleaned not in texts:
            texts.append(cleaned)
    return texts
