from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.llm.base import StructuredExtractionError
from app.llm.provider import LLMConfigurationError, create_provider
from app.models import (
    BiologicalObservation,
    Case,
    Event,
    Evidence,
    ExplanatoryAlternative,
    ExtractionRun,
    FieldEvidenceLink,
    GenotypeObservation,
    Lesion,
    LesionCollection,
    Paper,
    TemporalRecord,
)
from app.schemas.records import (
    BiologicalObservationDetailRead,
    BiologicalObservationRead,
    CaseDetailRead,
    CaseCreate,
    CaseRead,
    EventCreate,
    EventRead,
    EvidenceCreate,
    EvidenceRead,
    ExplanatoryAlternativeRead,
    ExtractionRunRead,
    FieldEvidenceRead,
    GenotypeObservationRead,
    IngestRequest,
    LesionCollectionRead,
    LesionRead,
    PaperRead,
    TemporalRecordRead,
    TimelineEventDetailRead,
)
from app.services.extraction_pipeline import ExtractionPipeline
from app.services.biological_observation_pipeline import (
    BiologicalObservationPipeline,
)
from app.services.paper_ingestion import ingest_pdf, resolve_paper_path
from app.services.paper_parser import PdfTextExtractionError


router = APIRouter()


def _commit_or_conflict(session: Session, record):
    try:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The record conflicts with an existing record or integrity rule",
        ) from exc


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/papers", response_model=list[PaperRead])
def list_papers(session: Session = Depends(get_db)) -> list[Paper]:
    return list(session.scalars(select(Paper).order_by(Paper.id.desc())))


@router.get("/papers/{paper_id}", response_model=PaperRead)
def get_paper(paper_id: int, session: Session = Depends(get_db)) -> Paper:
    paper = session.get(Paper, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.post("/papers/{paper_id}/extract", response_model=ExtractionRunRead)
def extract_paper(
    paper_id: int,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ExtractionRun:
    if session.get(Paper, paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    try:
        provider = create_provider(settings)
        return ExtractionPipeline(provider).run(session, paper_id)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except StructuredExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/papers/{paper_id}/extraction-status",
    response_model=ExtractionRunRead | None,
)
def extraction_status(
    paper_id: int, session: Session = Depends(get_db)
) -> ExtractionRun | None:
    if session.get(Paper, paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return session.scalar(
        select(ExtractionRun)
        .where(
            ExtractionRun.paper_id == paper_id,
            (
                ExtractionRun.run_type.is_(None)
                | (ExtractionRun.run_type == "case_timeline")
            ),
        )
        .order_by(ExtractionRun.id.desc())
        .limit(1)
    )


@router.post("/papers/ingest", response_model=PaperRead)
def ingest_paper(
    payload: IngestRequest,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Paper:
    try:
        pdf_path = resolve_paper_path(settings.papers_dir, payload.filename)
        return ingest_pdf(session, pdf_path, settings.processed_dir).paper
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, PdfTextExtractionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/cases", response_model=list[CaseRead])
def list_cases(session: Session = Depends(get_db)) -> list[Case]:
    return list(session.scalars(select(Case).order_by(Case.id.desc())))


def _field_evidence(
    session: Session, entity_type: str, entity_id: int
) -> list[FieldEvidenceRead]:
    rows = session.execute(
        select(FieldEvidenceLink.field_name, Evidence)
        .join(Evidence, Evidence.id == FieldEvidenceLink.evidence_id)
        .where(
            FieldEvidenceLink.entity_type == entity_type,
            FieldEvidenceLink.entity_id == entity_id,
        )
        .order_by(FieldEvidenceLink.field_name, Evidence.id)
    )
    return [
        FieldEvidenceRead(
            field_name=field_name,
            evidence=EvidenceRead.model_validate(evidence),
        )
        for field_name, evidence in rows
    ]


@router.get("/papers/{paper_id}/cases", response_model=list[CaseDetailRead])
def list_paper_cases(
    paper_id: int, session: Session = Depends(get_db)
) -> list[CaseDetailRead]:
    if session.get(Paper, paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    cases = session.scalars(
        select(Case).where(Case.paper_id == paper_id).order_by(Case.id)
    )
    return [
        CaseDetailRead(
            case=CaseRead.model_validate(case),
            evidence=_field_evidence(session, "case", case.id),
        )
        for case in cases
    ]


@router.get("/cases/{case_id}", response_model=CaseDetailRead)
def get_case(case_id: int, session: Session = Depends(get_db)) -> CaseDetailRead:
    case = session.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseDetailRead(
        case=CaseRead.model_validate(case),
        evidence=_field_evidence(session, "case", case.id),
    )


@router.post("/cases", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, session: Session = Depends(get_db)) -> Case:
    if session.get(Paper, payload.paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return _commit_or_conflict(session, Case(**payload.model_dump()))


@router.get("/cases/{case_id}/events", response_model=list[EventRead])
def list_events(case_id: int, session: Session = Depends(get_db)) -> list[Event]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    statement = (
        select(Event)
        .where(Event.case_id == case_id)
        .order_by(Event.relative_day.asc().nulls_last(), Event.event_date.asc().nulls_last())
    )
    return list(session.scalars(statement))


@router.get(
    "/cases/{case_id}/timeline", response_model=list[TimelineEventDetailRead]
)
def get_timeline(
    case_id: int, session: Session = Depends(get_db)
) -> list[TimelineEventDetailRead]:
    events = list_events(case_id, session)
    return [
        TimelineEventDetailRead(
            event=EventRead.model_validate(event),
            evidence=_field_evidence(session, "event", event.id),
        )
        for event in events
    ]


def _latest_biological_run_id(session: Session, case_id: int) -> int | None:
    return session.scalar(
        select(ExtractionRun.id)
        .where(
            ExtractionRun.case_id == case_id,
            ExtractionRun.run_type == BiologicalObservationPipeline.RUN_TYPE,
        )
        .order_by(ExtractionRun.id.desc())
        .limit(1)
    )


def _biological_observation_details(
    session: Session, case_id: int
) -> list[BiologicalObservationDetailRead]:
    run_id = _latest_biological_run_id(session, case_id)
    if run_id is None:
        return []
    observations = session.scalars(
        select(BiologicalObservation)
        .where(
            BiologicalObservation.case_id == case_id,
            BiologicalObservation.created_from_run_id == run_id,
        )
        .order_by(
            BiologicalObservation.category,
            BiologicalObservation.normalized_variable,
            BiologicalObservation.id,
        )
    )
    return [
        BiologicalObservationDetailRead(
            observation=BiologicalObservationRead.model_validate(observation),
            evidence=_field_evidence(
                session, "biological_observation", observation.id
            ),
        )
        for observation in observations
    ]


@router.post(
    "/cases/{case_id}/extract-biological-observations",
    response_model=ExtractionRunRead,
)
def extract_biological_observations(
    case_id: int,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ExtractionRun:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    try:
        provider = create_provider(settings)
        return BiologicalObservationPipeline(provider).run_case(session, case_id)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except StructuredExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/cases/{case_id}/biological-observations",
    response_model=list[BiologicalObservationDetailRead],
)
def get_case_biological_observations(
    case_id: int, session: Session = Depends(get_db)
) -> list[BiologicalObservationDetailRead]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _biological_observation_details(session, case_id)


@router.get(
    "/papers/{paper_id}/biological-observations",
    response_model=list[BiologicalObservationDetailRead],
)
def get_paper_biological_observations(
    paper_id: int, session: Session = Depends(get_db)
) -> list[BiologicalObservationDetailRead]:
    if session.get(Paper, paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    cases = session.scalars(
        select(Case).where(Case.paper_id == paper_id).order_by(Case.id)
    )
    return [
        detail
        for case in cases
        for detail in _biological_observation_details(session, case.id)
    ]


@router.get("/cases/{case_id}/lesions", response_model=list[LesionRead])
def get_case_lesions(
    case_id: int, session: Session = Depends(get_db)
) -> list[Lesion]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(
        session.scalars(
            select(Lesion).where(Lesion.case_id == case_id).order_by(Lesion.id)
        ).unique()
    )


@router.get(
    "/cases/{case_id}/lesion-collections",
    response_model=list[LesionCollectionRead],
)
def get_case_lesion_collections(
    case_id: int, session: Session = Depends(get_db)
) -> list[LesionCollection]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(
        session.scalars(
            select(LesionCollection)
            .where(LesionCollection.case_id == case_id)
            .order_by(LesionCollection.id)
        )
    )


@router.get(
    "/cases/{case_id}/temporal-records", response_model=list[TemporalRecordRead]
)
def get_case_temporal_records(
    case_id: int, session: Session = Depends(get_db)
) -> list[TemporalRecord]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(
        session.scalars(
            select(TemporalRecord)
            .where(TemporalRecord.case_id == case_id)
            .order_by(TemporalRecord.id)
        )
    )


@router.get(
    "/cases/{case_id}/genotype-observations",
    response_model=list[GenotypeObservationRead],
)
def get_case_genotype_observations(
    case_id: int, session: Session = Depends(get_db)
) -> list[GenotypeObservation]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(
        session.scalars(
            select(GenotypeObservation)
            .where(GenotypeObservation.case_id == case_id)
            .order_by(GenotypeObservation.id)
        )
    )


@router.get(
    "/cases/{case_id}/explanatory-alternatives",
    response_model=list[ExplanatoryAlternativeRead],
)
def get_case_explanatory_alternatives(
    case_id: int, session: Session = Depends(get_db)
) -> list[ExplanatoryAlternative]:
    if session.get(Case, case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return list(
        session.scalars(
            select(ExplanatoryAlternative)
            .where(ExplanatoryAlternative.case_id == case_id)
            .order_by(ExplanatoryAlternative.id)
        )
    )


@router.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, session: Session = Depends(get_db)) -> Event:
    if session.get(Case, payload.case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _commit_or_conflict(session, Event(**payload.model_dump()))


@router.get("/evidence", response_model=list[EvidenceRead])
def list_evidence(session: Session = Depends(get_db)) -> list[Evidence]:
    return list(session.scalars(select(Evidence).order_by(Evidence.id.desc())))


@router.post(
    "/evidence", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED
)
def create_evidence(
    payload: EvidenceCreate, session: Session = Depends(get_db)
) -> Evidence:
    if session.get(Paper, payload.paper_id) is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    if payload.case_id is not None:
        case = session.get(Case, payload.case_id)
        if case is None:
            raise HTTPException(status_code=404, detail="Case not found")
        if case.paper_id != payload.paper_id:
            raise HTTPException(
                status_code=422, detail="Evidence paper_id must match the case paper_id"
            )
    return _commit_or_conflict(session, Evidence(**payload.model_dump()))
