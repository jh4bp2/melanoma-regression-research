from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
PMID_RE = re.compile(r"\bPMID\s*:?\s*(\d{6,9})\b", re.IGNORECASE)


class PdfTextExtractionError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedPaper:
    title: str | None
    authors: list[str]
    year: int | None
    doi: str | None
    pmid: str | None
    page_count: int
    content_sha256: str
    raw_metadata: dict[str, str]
    pages: list[str]


def _clean_metadata_value(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _parse_authors(raw_authors: str) -> list[str]:
    if not raw_authors:
        return []
    separator = ";" if ";" in raw_authors else ","
    return [author.strip() for author in raw_authors.split(separator) if author.strip()]


def parse_pdf(pdf_path: Path) -> ParsedPaper:
    pdf_path = pdf_path.resolve()
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    content = pdf_path.read_bytes()
    if not content.startswith(b"%PDF-"):
        raise PdfTextExtractionError(
            f"{pdf_path.name} is not a PDF file (missing PDF signature)"
        )
    content_sha256 = hashlib.sha256(content).hexdigest()

    try:
        with pymupdf.open(pdf_path) as document:
            metadata = {
                key: _clean_metadata_value(value)
                for key, value in (document.metadata or {}).items()
            }
            pages = [page.get_text("text").strip() for page in document]
    except (pymupdf.FileDataError, RuntimeError) as exc:
        raise PdfTextExtractionError(f"Cannot parse PDF: {pdf_path.name}") from exc

    if not pages or not any(page for page in pages):
        raise PdfTextExtractionError(
            f"No extractable text in {pdf_path.name}; OCR is not supported in Phase 1"
        )

    searchable_text = "\n".join(pages[:3])
    doi_match = DOI_RE.search(searchable_text)
    pmid_match = PMID_RE.search(searchable_text)

    return ParsedPaper(
        title=metadata.get("title") or None,
        authors=_parse_authors(metadata.get("author", "")),
        # PDF creationDate is not publication year. Keep it in raw_metadata only.
        year=None,
        doi=doi_match.group().rstrip(".,;)") if doi_match else None,
        pmid=pmid_match.group(1) if pmid_match else None,
        page_count=len(pages),
        content_sha256=content_sha256,
        raw_metadata=metadata,
        pages=pages,
    )


def write_page_preserving_text(parsed: ParsedPaper, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_pages = [
        f"=== PAGE {page_number} ===\n{text}"
        for page_number, text in enumerate(parsed.pages, start=1)
    ]
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text("\n\n".join(rendered_pages) + "\n", encoding="utf-8")
    temporary_path.replace(output_path)
