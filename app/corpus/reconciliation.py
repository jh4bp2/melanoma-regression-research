from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.corpus.collection_recovery import CollectionCandidate, recover_collections
from app.corpus.episode_canonical import (
    CanonicalEpisode,
    canonicalize_episodes,
    should_split_collapsed_case,
)
from app.corpus.lesion_naming import improved_lesion_name, is_weak_lesion_name
from app.corpus.polarity import (
    PolarityDecision,
    check_claim_against_quote,
    deterministic_persistence_claim,
    is_literature_statement,
)
from app.corpus.runs import seed_cases_and_runs
from app.corpus.versions import (
    CORPUS_INFRA_VERSION,
    CORPUS_RULE_VERSION,
    RECONCILIATION_RUN_TYPE,
)
from app.models import (
    BiologicalObservation,
    CollectionMembershipStatus,
    Evidence,
    Event,
    EvidenceType,
    ExtractionRun,
    ExtractionStatus,
    FieldEvidenceLink,
    Lesion,
    LesionAlias,
    LesionAliasStatus,
    LesionCollection,
    LesionCollectionMembership,
    ObservationCategory,
    QuoteVerificationStatus,
    RegressionEpisode,
    RegressionEpisodeType,
    RegressionExtent,
)


def reconcile_paper(session: Session, paper_id: int) -> dict[str, Any]:
    cases, phase2, phase3 = seed_cases_and_runs(session, paper_id)
    summary = {
        "paper_id": paper_id,
        "cases": [],
        "collections_created": 0,
        "collection_only": 0,
        "linked_members": 0,
        "episodes_before": 0,
        "episodes_after": 0,
        "merged_episodes": 0,
        "split_episodes": 0,
        "fact_inversions": 0,
        "rejected_claims": 0,
        "name_improvements": 0,
        "unresolved_collection_candidates": 0,
    }
    if not cases or not phase3:
        return summary
    for case in cases:
        case_phase3 = [run for run in phase3 if run.case_id == case.id]
        if not case_phase3:
            continue
        result = reconcile_case(session, case, phase2, case_phase3[0])
        summary["cases"].append(result)
        for key in (
            "collections_created",
            "collection_only",
            "linked_members",
            "episodes_before",
            "episodes_after",
            "merged_episodes",
            "split_episodes",
            "fact_inversions",
            "rejected_claims",
            "name_improvements",
            "unresolved_collection_candidates",
        ):
            summary[key] += result.get(key, 0)
    return summary


def reconcile_case(
    session: Session,
    case,
    phase2: ExtractionRun | None,
    phase3: ExtractionRun,
) -> dict[str, Any]:
    observations = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.case_id == case.id,
                BiologicalObservation.created_from_run_id == phase3.id,
            )
        )
    )
    lesions = list(
        session.scalars(
            select(Lesion).where(
                Lesion.case_id == case.id,
                Lesion.created_from_run_id == phase3.id,
            )
        )
    )
    episodes = list(
        session.scalars(
            select(RegressionEpisode).where(
                RegressionEpisode.case_id == case.id,
                RegressionEpisode.created_from_run_id == phase3.id,
            )
        )
    )
    events = []
    if phase2:
        events = list(
            session.scalars(
                select(Event).where(
                    Event.case_id == case.id,
                    Event.extraction_run_id == phase2.id,
                )
            )
        )
    quotes = _observation_quotes(session, observations, phase3.id)
    inversions = _scan_inversions(observations, quotes)
    texts = _patient_fact_texts(observations, events, quotes)
    collections = recover_collections(texts, lesions)
    lesion_organs = {lesion.id: lesion.organ or "UNK" for lesion in lesions}
    canonical = canonicalize_episodes(episodes, lesion_organs=lesion_organs)
    organ_mentions = _regressing_organs(observations, events, collections, lesions)
    split_scopes = should_split_collapsed_case(episodes, organ_mentions)
    if split_scopes and len(canonical) == 1:
        canonical = _split_canonical(canonical[0], split_scopes, collections, lesions)
    name_fixes = _name_fixes(lesions, observations, events)

    run = ExtractionRun(
        paper_id=case.paper_id,
        case_id=case.id,
        source_extraction_run_id=phase3.id,
        run_type=RECONCILIATION_RUN_TYPE,
        model="deterministic-reconciliation",
        prompt_version="none",
        status=ExtractionStatus.COMPLETED,
        schema_version=CORPUS_INFRA_VERSION,
        rule_version=CORPUS_RULE_VERSION,
        finished_at=datetime.now(timezone.utc),
        result_json={},
        reason_codes=[],
    )
    session.add(run)
    session.flush()

    persisted_collections = _persist_collections(session, run, case, collections)
    persisted_episodes = _persist_episodes(session, run, case, canonical, persisted_collections)
    _persist_name_fixes(session, run, case, name_fixes)
    corrected = _persist_inversion_corrections(session, run, case, inversions)

    metrics = {
        "case_id": case.id,
        "collections_created": len(persisted_collections),
        "collection_only": sum(
            1
            for item in collections
            if item.membership_status == CollectionMembershipStatus.COLLECTION_ONLY
        ),
        "linked_members": sum(len(item.member_lesion_ids) for item in collections),
        "episodes_before": len(episodes),
        "episodes_after": len(persisted_episodes),
        "merged_episodes": sum(1 for item in canonical if item.action == "MERGED"),
        "split_episodes": sum(1 for item in canonical if item.action == "SPLIT"),
        "fact_inversions": len(inversions),
        "rejected_claims": len(inversions),
        "name_improvements": len(name_fixes),
        "unresolved_collection_candidates": 0,
        "corrections": corrected,
        "inversions": [
            {
                "observation_id": item["observation_id"],
                "decision": item["decision"],
                "reason": item["reason"],
            }
            for item in inversions
        ],
    }
    run.result_json = metrics
    session.commit()
    return metrics


def _observation_quotes(
    session: Session,
    observations: list[BiologicalObservation],
    run_id: int,
) -> dict[int, str]:
    if not observations:
        return {}
    links = list(
        session.scalars(
            select(FieldEvidenceLink).where(
                FieldEvidenceLink.extraction_run_id == run_id,
                FieldEvidenceLink.entity_type == "biological_observation",
                FieldEvidenceLink.entity_id.in_([obs.id for obs in observations]),
            )
        )
    )
    evidence = {
        item.id: item
        for item in session.scalars(
            select(Evidence).where(
                Evidence.id.in_({link.evidence_id for link in links} or [-1])
            )
        )
    }
    quotes: dict[int, str] = {}
    for link in links:
        item = evidence.get(link.evidence_id)
        if item is None:
            continue
        text = item.raw_source_quote or item.normalized_source_quote or ""
        if item.verification_status == QuoteVerificationStatus.UNVERIFIED.value:
            continue
        quotes.setdefault(link.entity_id, text)
    return quotes


def _patient_fact_texts(
    observations: list[BiologicalObservation],
    events: list[Event],
    quotes: dict[int, str],
) -> list[tuple[str, str | None, int | None]]:
    rows: list[tuple[str, str | None, int | None]] = []
    for obs in observations:
        if obs.evidence_type == EvidenceType.AUTHOR_INTERPRETATION.value:
            continue
        text = " ".join(
            part
            for part in (
                obs.variable_name,
                obs.value,
                obs.lesion_identifier,
                quotes.get(obs.id),
            )
            if part
        )
        if is_literature_statement(text):
            continue
        rows.append((text, quotes.get(obs.id), obs.id))
    for event in events:
        if is_literature_statement(event.description):
            continue
        rows.append((event.description, event.description, None))
    return rows


def _scan_inversions(
    observations: list[BiologicalObservation],
    quotes: dict[int, str],
) -> list[dict[str, Any]]:
    found = []
    for obs in observations:
        quote = quotes.get(obs.id)
        claim = " ".join(part for part in (obs.variable_name, obs.value) if part)
        result = check_claim_against_quote(quote, claim, subject=obs.variable_name)
        if result.decision == PolarityDecision.FACT_INVERSION:
            found.append(
                {
                    "observation_id": obs.id,
                    "decision": result.decision.value,
                    "reason": result.reason,
                    "quote": quote,
                    "claim": claim,
                    "subject": result.subject or obs.variable_name,
                }
            )
    return found


def _name_fixes(
    lesions: list[Lesion],
    observations: list[BiologicalObservation],
    events: list[Event],
) -> list[tuple[Lesion, str]]:
    evidence = [
        *(f"{obs.variable_name} {obs.value or ''} {obs.lesion_identifier or ''}" for obs in observations),
        *(event.description for event in events),
    ]
    fixes = []
    for lesion in lesions:
        if not is_weak_lesion_name(lesion.canonical_name):
            continue
        forbidden = [
            other.canonical_name
            for other in lesions
            if other.id != lesion.id and other.canonical_name
        ]
        improved = improved_lesion_name(
            lesion.canonical_name, evidence, forbidden_names=forbidden
        )
        if improved:
            fixes.append((lesion, improved))
    return fixes


def _persist_collections(
    session: Session,
    run: ExtractionRun,
    case,
    collections: list[CollectionCandidate],
) -> list[LesionCollection]:
    persisted = []
    for candidate in collections:
        collection = LesionCollection(
            paper_id=case.paper_id,
            case_id=case.id,
            canonical_name=candidate.normalized_label,
            collection_type=candidate.collection_type,
            organ=candidate.organ,
            anatomical_location=candidate.region,
            source_text=candidate.source_label,
            laterality=candidate.laterality,
            normalized_label=candidate.normalized_label,
            member_count_reported=candidate.reported_count,
            count_semantics=candidate.count_semantics.value,
            membership_status=candidate.membership_status.value,
            membership_confidence=candidate.confidence,
            collection_only=(
                candidate.membership_status == CollectionMembershipStatus.COLLECTION_ONLY
            ),
            created_from_run_id=run.id,
        )
        session.add(collection)
        session.flush()
        for lesion_id in candidate.member_lesion_ids:
            session.add(
                LesionCollectionMembership(
                    collection_id=collection.id,
                    lesion_id=lesion_id,
                    membership_confidence=0.7,
                )
            )
        persisted.append(collection)
    session.flush()
    return persisted


def _persist_episodes(
    session: Session,
    run: ExtractionRun,
    case,
    canonical: list[CanonicalEpisode],
    collections: list[LesionCollection],
) -> list[RegressionEpisode]:
    persisted = []
    collection_by_organ = {item.organ: item.id for item in collections if item.organ}
    for index, draft in enumerate(canonical, start=1):
        collection_ids = list(draft.associated_collection_ids)
        organ = draft.anatomic_scope
        mapped = {
            "LUNG": "LUNG",
            "LYMPH_NODE": "LYMPH_NODE",
            "NEVI": "SKIN",
            "SKIN_PRIMARY": None,
            "BRAIN": "BRAIN",
        }.get(organ)
        if mapped and mapped in collection_by_organ:
            collection_id = collection_by_organ[mapped]
            if collection_id not in collection_ids:
                collection_ids.append(collection_id)
        episode = RegressionEpisode(
            paper_id=case.paper_id,
            case_id=case.id,
            episode_index=index,
            episode_type=RegressionEpisodeType(draft.episode_type),
            extent=RegressionExtent(draft.extent),
            spontaneous_status=draft.spontaneous_status,
            associated_lesion_ids=draft.associated_lesion_ids,
            associated_event_ids=draft.associated_event_ids,
            associated_collection_ids=collection_ids,
            anatomic_scope=draft.anatomic_scope,
            milestones=draft.milestones,
            source_episode_ids=draft.source_episode_ids,
            extent_transition=draft.extent_transition,
            is_canonical=True,
            description=draft.description,
            confidence=draft.confidence,
            created_from_run_id=run.id,
        )
        session.add(episode)
        persisted.append(episode)
    session.flush()
    return persisted


def _persist_name_fixes(session: Session, run: ExtractionRun, case, fixes) -> None:
    for lesion, improved in fixes:
        lesion.reconciled_canonical_name = improved
        session.add(
            LesionAlias(
                lesion_id=lesion.id,
                source_text=lesion.canonical_name,
                paper_id=case.paper_id,
                status=LesionAliasStatus.CONFIRMED_ALIAS,
            )
        )


def _persist_inversion_corrections(
    session: Session,
    run: ExtractionRun,
    case,
    inversions: list[dict[str, Any]],
) -> int:
    created = 0
    for item in inversions:
        correction = deterministic_persistence_claim(item.get("quote"), item.get("subject"))
        if not correction:
            continue
        session.add(
            BiologicalObservation(
                paper_id=case.paper_id,
                case_id=case.id,
                category=ObservationCategory.OTHER,
                variable_name=item.get("subject") or "persistence",
                value=correction,
                status="REPORTED",
                observation_domain="DISEASE_PHENOTYPE",
                measurement_semantics="CLINICAL_FINDING",
                evidence_type=EvidenceType.OBSERVED_FACT.value,
                confidence=0.7,
                created_from_run_id=run.id,
            )
        )
        created += 1
    session.flush()
    return created


def _regressing_organs(
    observations,
    events,
    collections,
    lesions,
) -> list[str]:
    from app.corpus.polarity import DirectionPolarity, polarity_of

    organ_hits: set[str] = set()
    blobs = [
        *(f"{obs.variable_name} {obs.value or ''} {obs.lesion_identifier or ''}" for obs in observations),
        *(event.description for event in events),
    ]
    for blob in blobs:
        polarity = polarity_of(blob)
        if polarity not in {
            DirectionPolarity.DISAPPEARANCE,
            DirectionPolarity.DECREASE,
        }:
            continue
        text = blob.lower()
        if any(token in text for token in ("lung", "pulmon", "nodule")):
            organ_hits.add("LUNG")
        if any(token in text for token in ("lymph", "node", "neck", "inguinal")):
            organ_hits.add("LYMPH_NODE")
        if any(token in text for token in ("nevi", "nevus", "naev")):
            organ_hits.add("NEVI")
        if any(token in text for token in ("primary", "sole", "cheek", "ankle")):
            organ_hits.add("SKIN_PRIMARY")
        if "brain" in text or "cerebral" in text:
            organ_hits.add("BRAIN")
    return [item for item in ("LUNG", "LYMPH_NODE", "SKIN_PRIMARY", "NEVI", "BRAIN") if item in organ_hits]


def _split_canonical(
    draft: CanonicalEpisode,
    scopes: list[str],
    collections: list[CollectionCandidate],
    lesions: list[Lesion],
) -> list[CanonicalEpisode]:
    rows = []
    for scope in scopes:
        collection_ids = []
        lesion_ids = [
            lesion.id
            for lesion in lesions
            if (lesion.organ or "")
            == {
                "LUNG": "LUNG",
                "LYMPH_NODE": "LYMPH_NODE",
                "NEVI": "SKIN",
                "SKIN_PRIMARY": "SKIN",
                "BRAIN": "BRAIN",
            }.get(scope, "")
        ]
        rows.append(
            CanonicalEpisode(
                case_id=draft.case_id,
                episode_type=draft.episode_type,
                extent=draft.extent,
                anatomic_scope=scope,
                description=f"{draft.description} [scoped:{scope}]",
                associated_lesion_ids=lesion_ids,
                associated_collection_ids=[],
                associated_event_ids=draft.associated_event_ids,
                source_episode_ids=draft.source_episode_ids,
                milestones=draft.milestones,
                extent_transition=draft.extent_transition,
                spontaneous_status=draft.spontaneous_status,
                action="SPLIT",
            )
        )
    return rows or [draft]
