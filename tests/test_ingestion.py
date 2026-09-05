from pathlib import Path

import pymupdf
import pytest

from app.services.paper_ingestion import ingest_pdf, resolve_paper_path
from app.services.paper_parser import PdfTextExtractionError, parse_pdf


def _make_pdf(path: Path) -> None:
    document = pymupdf.open()
    first_page = document.new_page()
    first_page.insert_text(
        (72, 72),
        "A melanoma case report\nDOI: 10.1000/test.123\nPMID: 12345678",
    )
    second_page = document.new_page()
    second_page.insert_text((72, 72), "Observed regression after follow-up.")
    document.set_metadata(
        {
            "title": "Documented melanoma regression",
            "author": "A. Researcher; B. Reviewer",
            "creationDate": "D:20200101000000",
        }
    )
    document.save(path)
    document.close()


def test_ingest_pdf_preserves_pages_and_deduplicates(db_session, tmp_path):
    pdf_path = tmp_path / "paper.pdf"
    processed_dir = tmp_path / "processed"
    _make_pdf(pdf_path)

    first = ingest_pdf(db_session, pdf_path, processed_dir)
    second = ingest_pdf(db_session, pdf_path, processed_dir)

    assert first.created is True
    assert second.created is False
    assert second.paper.id == first.paper.id
    assert first.paper.title == "Documented melanoma regression"
    assert first.paper.authors == ["A. Researcher", "B. Reviewer"]
    assert first.paper.year is None
    assert first.paper.raw_metadata["creationDate"].startswith("D:2020")
    assert first.paper.doi == "10.1000/test.123"
    assert first.paper.pmid == "12345678"
    extracted = Path(first.paper.extracted_text_path).read_text(encoding="utf-8")
    assert "=== PAGE 1 ===" in extracted
    assert "=== PAGE 2 ===" in extracted


def test_resolve_paper_path_rejects_directory_traversal(tmp_path):
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()

    try:
        resolve_paper_path(papers_dir, "../outside.pdf")
    except ValueError as exc:
        assert "inside" in str(exc)
    else:
        raise AssertionError("Directory traversal should be rejected")


def test_html_download_wrapper_renamed_as_pdf_is_rejected(tmp_path):
    fake_pdf = tmp_path / "wrapper.pdf"
    fake_pdf.write_text("<html>Preparing to download ...</html>", encoding="utf-8")

    with pytest.raises(PdfTextExtractionError, match="missing PDF signature"):
        parse_pdf(fake_pdf)
