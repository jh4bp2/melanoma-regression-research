from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import httpx
import pymupdf

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.paper_ingestion import ingest_pdf
from app.services.paper_parser import PdfTextExtractionError


PAPERS_DIR = Path("data/papers")
PROCESSED_DIR = Path("data/processed")
MANIFEST_PATH = PAPERS_DIR / "manifest.json"

TARGETS = [
    {
        "label": "A",
        "filename": "oswalt_2022_pmc9172893.pdf",
        "title": (
            "Identification of a Germline Pyrin Variant in a Metastatic "
            "Melanoma Patient With Multiple Spontaneous Regressions and "
            "Immune-related Adverse Events"
        ),
        "doi": "10.1097/CJI.0000000000000425",
        "pmid": "35621992",
        "pmcid": "PMC9172893",
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC9172893.1/PMC9172893.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9172893/pdf/nihms-1807636.pdf",
            "https://europepmc.org/articles/PMC9172893?pdf=render",
        ],
        "access_source": "NIH NLM NCBI PMC Article Datasets on AWS (PMC9172893.1)",
        "source_version": "PMC9172893.1",
    },
    {
        "label": "B",
        "filename": "spring_2017_pmc5729012.pdf",
        "title": (
            "Complete spontaneous regression of a metastatic acral melanoma "
            "with associated leukoderma"
        ),
        "doi": "10.1016/j.jdcr.2017.07.001",
        "pmid": "29264383",
        "pmcid": "PMC5729012",
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC5729012.1/PMC5729012.1.pdf",
            "https://www.jaadcasereports.org/article/S2352-5126(17)30161-3/pdf",
            "https://europepmc.org/articles/PMC5729012?pdf=render",
        ],
        "access_source": "NIH NLM NCBI PMC Article Datasets on AWS (PMC5729012.1)",
        "source_version": "PMC5729012.1",
    },
    {
        "label": "C",
        "filename": "wang_2025_pmc12520872.pdf",
        "title": (
            "Case Report: Shadows of disappearance: the enigma of completely "
            "regressed cutaneous melanoma revealed by lymph node metastasis"
        ),
        "doi": "10.3389/fonc.2025.1671450",
        "pmid": "41103958",
        "pmcid": "PMC12520872",
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC12520872.1/PMC12520872.1.pdf",
            "https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2025.1671450/pdf",
            "https://europepmc.org/articles/PMC12520872?pdf=render",
        ],
        "access_source": "NIH NLM NCBI PMC Article Datasets on AWS (PMC12520872.1)",
        "source_version": "PMC12520872.1",
    },
]


def _download(urls: list[str], dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with httpx.Client(follow_redirects=True, timeout=180.0) as client:
        for url in urls:
            try:
                response = client.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (compatible; CancerRegressionResearch/1.0; "
                            "legal open-access retrieval)"
                        ),
                        "Accept": "application/pdf,*/*",
                    },
                )
                response.raise_for_status()
                if response.content.startswith(b"%PDF-"):
                    dest.write_bytes(response.content)
                    return url
                errors.append(f"{url}: not a PDF ({response.headers.get('content-type')})")
            except Exception as exc:
                errors.append(f"{url}: {exc}")
    raise RuntimeError("No legal PDF retrieved:\n" + "\n".join(errors))


def _verify_pdf(path: Path) -> tuple[str, int, int]:
    content = path.read_bytes()
    if not content.startswith(b"%PDF-"):
        raise PdfTextExtractionError(f"{path.name} is not a PDF file")
    sha256 = hashlib.sha256(content).hexdigest()
    with pymupdf.open(path) as document:
        page_count = document.page_count
        if page_count < 1:
            raise PdfTextExtractionError(f"{path.name} has no pages")
    return sha256, len(content), page_count


def main() -> None:
    init_db()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    existing = {
        (row.get("candidate_identifiers") or {}).get("pmcid")
        for row in manifest["papers"]
    }
    results = []
    with SessionLocal() as session:
        for target in TARGETS:
            dest = PAPERS_DIR / target["filename"]
            print(f"=== download {target['label']} {target['pmcid']} ===", flush=True)
            source_url = _download(target["source_urls"], dest)
            sha256, size, pages = _verify_pdf(dest)
            ingested = ingest_pdf(session, dest, PROCESSED_DIR)
            record = {
                "title": target["title"],
                "filename": target["filename"],
                "source_url": source_url,
                "access_source": target["access_source"],
                "source_version": target.get("source_version"),
                "source_size_bytes": size,
                "local_sha256": sha256,
                "page_count": pages,
                "download_date": date.today().isoformat(),
                "ingestion_paper_id": ingested.paper.id,
                "status": "INGESTED",
                "candidate_identifiers": {
                    "doi": target["doi"],
                    "pmid": target["pmid"],
                    "pmcid": target["pmcid"],
                },
            }
            if target["pmcid"] in existing:
                for index, row in enumerate(manifest["papers"]):
                    if (row.get("candidate_identifiers") or {}).get("pmcid") == target[
                        "pmcid"
                    ]:
                        manifest["papers"][index] = record
                        break
            else:
                manifest["papers"].append(record)
            print(
                f"paper_id={ingested.paper.id} created={ingested.created} "
                f"pages={pages} sha256={sha256[:12]}...",
                flush=True,
            )
            results.append((target["label"], ingested.paper.id, pages, sha256, size))
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("=== acquired ===", flush=True)
    for label, paper_id, pages, sha256, size in results:
        print(
            f"{label} paper_id={paper_id} pages={pages} bytes={size} sha={sha256}",
            flush=True,
        )


if __name__ == "__main__":
    main()
