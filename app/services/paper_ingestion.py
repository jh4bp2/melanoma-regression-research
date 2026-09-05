from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import AnalysisStatus, Paper, PaperType
from app.services.paper_parser import parse_pdf, write_page_preserving_text


@dataclass(frozen=True)
class IngestionResult:
    paper: Paper
    created: bool


def resolve_paper_path(papers_dir: Path, filename: str) -> Path:
    papers_root = papers_dir.resolve()
    candidate = (papers_root / filename).resolve()
    try:
        candidate.relative_to(papers_root)
    except ValueError as exc:
        raise ValueError("PDF path must stay inside the configured papers directory") from exc
    if candidate.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files can be ingested")
    return candidate


def ingest_pdf(
    session: Session,
    pdf_path: Path,
    processed_dir: Path,
) -> IngestionResult:
    parsed = parse_pdf(pdf_path)

    existing = session.scalar(
        select(Paper).where(Paper.content_sha256 == parsed.content_sha256)
    )
    if existing is not None:
        return IngestionResult(paper=existing, created=False)

    identifier_conditions = []
    if parsed.doi:
        identifier_conditions.append(Paper.doi == parsed.doi)
    if parsed.pmid:
        identifier_conditions.append(Paper.pmid == parsed.pmid)
    if identifier_conditions:
        existing = session.scalar(select(Paper).where(or_(*identifier_conditions)))
        if existing is not None:
            return IngestionResult(paper=existing, created=False)

    output_path = processed_dir.resolve() / f"{parsed.content_sha256}.txt"
    write_page_preserving_text(parsed, output_path)

    paper = Paper(
        title=parsed.title,
        authors=parsed.authors,
        year=parsed.year,
        doi=parsed.doi,
        pmid=parsed.pmid,
        full_text_path=str(pdf_path.resolve()),
        extracted_text_path=str(output_path),
        paper_type=PaperType.OTHER,
        analysis_status=AnalysisStatus.INGESTED,
        content_sha256=parsed.content_sha256,
        page_count=parsed.page_count,
        raw_metadata=parsed.raw_metadata,
    )
    try:
        session.add(paper)
        session.commit()
        session.refresh(paper)
    except Exception:
        session.rollback()
        output_path.unlink(missing_ok=True)
        raise

    return IngestionResult(paper=paper, created=True)


def ingest_directory(
    session: Session,
    papers_dir: Path,
    processed_dir: Path,
) -> list[IngestionResult]:
    papers_dir.mkdir(parents=True, exist_ok=True)
    return [
        ingest_pdf(session, pdf_path, processed_dir)
        for pdf_path in sorted(papers_dir.glob("*.pdf"))
    ]
