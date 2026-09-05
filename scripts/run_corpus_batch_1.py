from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pymupdf
from sqlalchemy import select

from app.corpus.indexes import load_seed_entities
from app.corpus.manifest import (
    add_or_update_paper,
    find_duplicate,
    load_manifest,
    record_pressure_point,
    save_manifest,
    transition_paper,
)
from app.corpus.pipeline import CorpusPipeline
from app.corpus.runs import seed_cases_and_runs
from app.corpus.states import PaperIntakeState, QualityStatus
from app.corpus.store import CorpusStore
from app.core.config import PROJECT_ROOT, get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.llm.provider import create_provider
from app.models import (
    BiologicalObservation,
    Case,
    Evidence,
    FieldEvidenceLink,
    LesionCollection,
    Paper,
    QuoteVerificationStatus,
)
from app.services.biological_observation_pipeline import BiologicalObservationPipeline
from app.services.extraction_pipeline import ExtractionPipeline
from app.services.paper_ingestion import ingest_pdf
from app.services.paper_parser import PdfTextExtractionError, parse_pdf


PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PAPERS_MANIFEST = PAPERS_DIR / "manifest.json"

BATCH_CANDIDATES = [
    {
        "candidate_id": "batch1-lynch-1978",
        "title": (
            "Spontaneous regression of metastatic malignant melanoma "
            "in 2 sibs with xeroderma pigmentosum"
        ),
        "doi": "10.1136/jmg.15.5.357",
        "pmid": "739525",
        "pmcid": "PMC1013731",
        "year": 1978,
        "journal": "Journal of Medical Genetics",
        "filename": "lynch_1978_pmc1013731.pdf",
        "selection_reason": (
            "Batch 1: two XP siblings with metastatic melanoma regression"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC1013731.1/PMC1013731.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1013731/pdf/",
            "https://europepmc.org/articles/PMC1013731?pdf=render",
            "https://jmg.bmj.com/content/jmedgenet/15/5/357.full.pdf",
        ],
    },
    {
        "candidate_id": "batch1-levison-1955",
        "title": "Spontaneous Regression of a Malignant Melanoma",
        "doi": "10.1136/bmj.1.4911.458",
        "pmid": "13230519",
        "pmcid": "PMC2061225",
        "year": 1955,
        "journal": "British Medical Journal",
        "filename": "levison_1955_pmc2061225.pdf",
        "selection_reason": "Batch 1: historical BMJ melanoma regression case",
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC2061225.1/PMC2061225.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2061225/pdf/",
            "https://europepmc.org/articles/PMC2061225?pdf=render",
        ],
    },
    {
        "candidate_id": "batch1-khosravi-2016",
        "title": (
            "Metastatic melanoma with spontaneous complete regression "
            "of a thick primary lesion"
        ),
        "doi": "10.1016/j.jdcr.2016.09.011",
        "pmid": "27981212",
        "pmcid": "PMC5144746",
        "year": 2016,
        "journal": "JAAD Case Reports",
        "filename": "khosravi_2016_pmc5144746.pdf",
        "selection_reason": (
            "Batch 1: thick primary complete regression with metastatic disease"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC5144746.1/PMC5144746.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5144746/pdf/",
            "https://europepmc.org/articles/PMC5144746?pdf=render",
            "https://www.jaadcasereports.org/article/S2352-5126(16)30111-4/pdf",
        ],
    },
    {
        "candidate_id": "batch1-paolino-2020",
        "title": (
            "Spontaneous Regression of Primary Melanoma and Multiple "
            "Melanocytic Nevi in a Patient With Metastatic Melanoma"
        ),
        "doi": "10.5826/dpc.1003a52",
        "pmid": "32685272",
        "pmcid": "PMC7346594",
        "year": 2020,
        "journal": "Dermatology Practical & Conceptual",
        "filename": "paolino_2020_pmc7346594.pdf",
        "selection_reason": (
            "Batch 1: primary melanoma, multiple nevi, and metastatic scopes"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC7346594.1/PMC7346594.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7346594/pdf/",
            "https://europepmc.org/articles/PMC7346594?pdf=render",
            (
                "https://dpcj.org/index.php/dpc/article/download/"
                "dermatol-pract-concept-articleid-dp1003a52/dp1003a52-pdf"
            ),
        ],
    },
    {
        "candidate_id": "batch1-nwabudike-2022",
        "title": (
            "Clinical, Dermoscopic and Microscopic Features of a "
            '"Collision Tumour" Ultimately Confirmed as a Regressing Melanoma '
            "- Lessons Learnt from a Chance Diagnosis"
        ),
        "doi": "10.2147/CCID.S361793",
        "pmid": "35860608",
        "pmcid": "PMC9289571",
        "year": 2022,
        "journal": "Clinical, Cosmetic and Investigational Dermatology",
        "filename": "nwabudike_2022_pmc9289571.pdf",
        "selection_reason": (
            "Batch 1: dermoscopic, microscopic, and diagnostic-scope case"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC9289571.1/PMC9289571.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9289571/pdf/",
            "https://europepmc.org/articles/PMC9289571?pdf=render",
            "https://www.dovepress.com/getfile.php?fileID=82126",
        ],
    },
]


def _access_source(url: str, pmcid: str) -> str:
    if "pmc-oa-opendata.s3.amazonaws.com" in url:
        return f"NIH NLM NCBI PMC Article Datasets on AWS ({pmcid}.1)"
    if "ncbi.nlm.nih.gov/pmc" in url:
        return f"NCBI PMC OA PDF ({pmcid})"
    if "europepmc.org" in url:
        return f"Europe PMC full-text PDF ({pmcid})"
    if "jmg.bmj.com" in url or "jaadcasereports.org" in url:
        return "Publisher open-access PDF"
    if "dpcj.org" in url or "dovepress.com" in url:
        return "Publisher open-access PDF"
    return "Legal open-access PDF"


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
                errors.append(
                    f"{url}: not a PDF ({response.headers.get('content-type')})"
                )
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


def _blank_row(target: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": target["candidate_id"],
        "title": target["title"],
        "doi": target["doi"],
        "pmid": target["pmid"],
        "pmcid": target["pmcid"],
        "year": target["year"],
        "journal": target["journal"],
        "selection_reason": target["selection_reason"],
        "source_url": None,
        "access_source": None,
        "fulltext_status": PaperIntakeState.CANDIDATE.value,
        "ingestion_status": PaperIntakeState.CANDIDATE.value,
        "extraction_status": PaperIntakeState.CANDIDATE.value,
        "paper_id": None,
        "sha256": None,
        "page_count": None,
        "bytes": None,
        "download_date": None,
        "case_count": 0,
        "lesion_count": 0,
        "episode_count": 0,
        "quality_status": QualityStatus.PENDING.value,
        "notes": "Corpus Expansion Batch 1 candidate.",
        "role": "batch_1",
        "batch": 1,
    }


def _advance(row: dict[str, Any], field: str, nxt: PaperIntakeState) -> None:
    current = PaperIntakeState(row[field])
    if current == nxt:
        return
    if current == PaperIntakeState.CANDIDATE and nxt in {
        PaperIntakeState.INGESTED,
        PaperIntakeState.EXTRACTED,
        PaperIntakeState.AUDITED,
    }:
        transition_paper(row, field, PaperIntakeState.FULLTEXT_FOUND)
        current = PaperIntakeState.FULLTEXT_FOUND
    if current == PaperIntakeState.FULLTEXT_FOUND and nxt in {
        PaperIntakeState.EXTRACTED,
        PaperIntakeState.AUDITED,
    }:
        transition_paper(row, field, PaperIntakeState.INGESTED)
        current = PaperIntakeState.INGESTED
    if current == PaperIntakeState.INGESTED and nxt == PaperIntakeState.AUDITED:
        transition_paper(row, field, PaperIntakeState.EXTRACTED)
        current = PaperIntakeState.EXTRACTED
    transition_paper(row, field, nxt)


def _update_papers_manifest(target: dict[str, Any], record: dict[str, Any]) -> None:
    payload = json.loads(PAPERS_MANIFEST.read_text(encoding="utf-8"))
    pmcid = target["pmcid"]
    replaced = False
    for index, row in enumerate(payload["papers"]):
        ids = row.get("candidate_identifiers") or {}
        if ids.get("pmcid") == pmcid or ids.get("pmid") == target["pmid"]:
            payload["papers"][index] = record
            replaced = True
            break
    if not replaced:
        payload["papers"].append(record)
    PAPERS_MANIFEST.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _patch_paper_metadata(session, paper: Paper, target: dict[str, Any], source_url: str) -> None:
    paper.title = target["title"]
    paper.doi = target["doi"]
    paper.pmid = target["pmid"]
    paper.year = target["year"]
    paper.journal = target["journal"]
    paper.source_url = source_url
    session.commit()


def register_candidates(store: CorpusStore) -> None:
    payload = load_manifest(store)
    for target in BATCH_CANDIDATES:
        existing = find_duplicate(payload, candidate_id=target["candidate_id"])
        if existing:
            continue
        add_or_update_paper(payload, _blank_row(target))
    save_manifest(store, payload)


def acquire_and_ingest(store: CorpusStore) -> list[str]:
    pipeline = CorpusPipeline(store)
    payload = load_manifest(store)
    attempted = [target["candidate_id"] for target in BATCH_CANDIDATES]
    with SessionLocal() as session:
        for target in BATCH_CANDIDATES:
            row = find_duplicate(payload, candidate_id=target["candidate_id"])
            assert row is not None
            dest = PAPERS_DIR / target["filename"]
            print(f"=== acquire {target['candidate_id']} {target['pmcid']} ===", flush=True)
            try:
                source_url = _download(target["source_urls"], dest)
                sha256, size, pages = _verify_pdf(dest)
                parse_pdf(dest)
            except Exception as exc:
                print(f"FULLTEXT_UNAVAILABLE {target['candidate_id']}: {exc}", flush=True)
                pipeline.mark_fulltext_unavailable(
                    target["candidate_id"],
                    note=f"Legal full text not ingestible: {exc}",
                )
                payload = load_manifest(store)
                row = find_duplicate(payload, candidate_id=target["candidate_id"])
                _update_papers_manifest(
                    target,
                    {
                        "title": target["title"],
                        "filename": None,
                        "source_url": target["source_urls"][-1],
                        "access_source": "Checked PMC OA / Europe PMC / publisher",
                        "source_size_bytes": None,
                        "local_sha256": None,
                        "page_count": None,
                        "download_date": None,
                        "access_checked_on": date.today().isoformat(),
                        "status": "FULLTEXT_UNAVAILABLE",
                        "candidate_identifiers": {
                            "doi": target["doi"],
                            "pmid": target["pmid"],
                            "pmcid": target["pmcid"],
                        },
                    },
                )
                continue

            row["source_url"] = source_url
            row["access_source"] = _access_source(source_url, target["pmcid"])
            row["sha256"] = sha256
            row["page_count"] = pages
            row["bytes"] = size
            row["download_date"] = date.today().isoformat()
            _advance(row, "fulltext_status", PaperIntakeState.FULLTEXT_FOUND)
            _advance(row, "ingestion_status", PaperIntakeState.FULLTEXT_FOUND)
            _advance(row, "extraction_status", PaperIntakeState.FULLTEXT_FOUND)
            save_manifest(store, payload)

            paper = pipeline.ingest_manual_pdf(session, target["candidate_id"], dest, PROCESSED_DIR)
            _patch_paper_metadata(session, paper, target, source_url)
            payload = load_manifest(store)
            row = find_duplicate(payload, candidate_id=target["candidate_id"])
            assert row is not None
            row["paper_id"] = paper.id
            row["title"] = target["title"]
            row["doi"] = target["doi"]
            row["pmid"] = target["pmid"]
            row["year"] = target["year"]
            row["journal"] = target["journal"]
            _advance(row, "extraction_status", PaperIntakeState.INGESTED)
            save_manifest(store, payload)
            _update_papers_manifest(
                target,
                {
                    "title": target["title"],
                    "filename": target["filename"],
                    "source_url": source_url,
                    "access_source": row["access_source"],
                    "source_version": f"{target['pmcid']}.1",
                    "source_size_bytes": size,
                    "local_sha256": sha256,
                    "page_count": pages,
                    "download_date": date.today().isoformat(),
                    "ingestion_paper_id": paper.id,
                    "status": "INGESTED",
                    "candidate_identifiers": {
                        "doi": target["doi"],
                        "pmid": target["pmid"],
                        "pmcid": target["pmcid"],
                    },
                },
            )
            print(
                f"paper_id={paper.id} pages={pages} bytes={size} sha={sha256[:12]}...",
                flush=True,
            )
    return attempted


def extract_ingested(store: CorpusStore) -> None:
    settings = get_settings()
    print(
        f"versions phase2={ExtractionPipeline.SCHEMA_VERSION}/"
        f"{ExtractionPipeline.RULE_VERSION} "
        f"phase3={BiologicalObservationPipeline.SCHEMA_VERSION}/"
        f"{BiologicalObservationPipeline.RULE_VERSION} "
        f"timeout={settings.llm_timeout_seconds}",
        flush=True,
    )
    provider = create_provider(settings)
    case_pipeline = ExtractionPipeline(provider)
    bio_pipeline = BiologicalObservationPipeline(provider)
    payload = load_manifest(store)
    with SessionLocal() as session:
        for target in BATCH_CANDIDATES:
            row = find_duplicate(payload, candidate_id=target["candidate_id"])
            if row is None or row.get("paper_id") is None:
                continue
            if row["extraction_status"] in {
                PaperIntakeState.EXTRACTED.value,
                PaperIntakeState.AUDITED.value,
                PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
                PaperIntakeState.EXCLUDED.value,
            }:
                continue
            paper_id = row["paper_id"]
            print(f"=== PHASE 2 extract paper={paper_id} ({target['candidate_id']}) ===", flush=True)
            case_run = case_pipeline.run(session, paper_id)
            cases = list(
                session.scalars(
                    select(Case)
                    .where(
                        Case.paper_id == paper_id,
                        Case.extraction_run_id == case_run.id,
                    )
                    .order_by(Case.id)
                )
            )
            print(
                f"paper={paper_id} case_run={case_run.id} "
                f"status={case_run.status.value} cases={[c.id for c in cases]}",
                flush=True,
            )
            for case in cases:
                print(
                    f"=== PHASE 3.4 extract case={case.id} paper={paper_id} ===",
                    flush=True,
                )
                bio_run = bio_pipeline.run_case(
                    session, case.id, source_run_id=case_run.id
                )
                metrics = (bio_run.result_json or {}).get("metrics", {})
                print(
                    f"case={case.id} bio_run={bio_run.id} "
                    f"status={bio_run.status.value} "
                    f"observations={metrics.get('persisted_observations', 0)} "
                    f"episodes={metrics.get('regression_episodes', 0)} "
                    f"genotypes={metrics.get('genotype_records', 0)}",
                    flush=True,
                )
            _advance(row, "extraction_status", PaperIntakeState.EXTRACTED)
            save_manifest(store, payload)


def collect_batch_stats(session, store: CorpusStore) -> dict[str, Any]:
    payload = load_manifest(store)
    batch_rows = [
        row
        for row in payload["papers"]
        if row.get("candidate_id", "").startswith("batch1-")
    ]
    paper_ids = [row["paper_id"] for row in batch_rows if row.get("paper_id")]
    observation_count = 0
    quote_counts: Counter[str] = Counter()
    case_ids: list[int] = []
    run_ids: list[int] = []
    per_paper: list[dict[str, Any]] = []
    for row in batch_rows:
        paper_id = row.get("paper_id")
        if paper_id is None:
            per_paper.append(
                {
                    "candidate_id": row["candidate_id"],
                    "paper_id": None,
                    "fulltext": row["fulltext_status"],
                    "cases": 0,
                    "lesions": 0,
                    "collections": 0,
                    "episodes": 0,
                    "observations": 0,
                }
            )
            continue
        cases, phase2, phase3 = seed_cases_and_runs(session, paper_id)
        phase3_ids = [run.id for run in phase3]
        case_ids.extend(case.id for case in cases)
        run_ids.extend(phase3_ids)
        _cases, lesions, episodes, _states = load_seed_entities(
            session, [case.id for case in cases], phase3_ids
        )
        collections = list(
            session.scalars(
                select(LesionCollection).where(
                    LesionCollection.case_id.in_([case.id for case in cases] or [-1]),
                    LesionCollection.created_from_run_id.in_(phase3_ids or [-1]),
                )
            )
        )
        observations = list(
            session.scalars(
                select(BiologicalObservation).where(
                    BiologicalObservation.case_id.in_([case.id for case in cases] or [-1]),
                    BiologicalObservation.created_from_run_id.in_(phase3_ids or [-1]),
                )
            )
        )
        observation_count += len(observations)
        links = list(
            session.scalars(
                select(FieldEvidenceLink).where(
                    FieldEvidenceLink.extraction_run_id.in_(
                        [*(phase3_ids), *([phase2.id] if phase2 else [])] or [-1]
                    )
                )
            )
        )
        evidence = list(
            session.scalars(
                select(Evidence).where(
                    Evidence.id.in_({link.evidence_id for link in links} or [-1])
                )
            )
        )
        for item in evidence:
            status = item.verification_status or "UNKNOWN"
            quote_counts[status] += 1
        per_paper.append(
            {
                "candidate_id": row["candidate_id"],
                "paper_id": paper_id,
                "fulltext": row["fulltext_status"],
                "cases": len(cases),
                "lesions": len(lesions),
                "collections": len(collections),
                "episodes": len(episodes),
                "observations": len(observations),
                "patient_ids": [case.patient_identifier for case in cases],
            }
        )
    matrix = store.read_json("observation_matrix.json", {"case_rows": []})
    status_counts: Counter[str] = Counter()
    for matrix_row in matrix.get("case_rows", []):
        if matrix_row.get("row_type") != "case":
            continue
        if matrix_row.get("case_id") not in case_ids:
            continue
        for cell in (matrix_row.get("cells") or {}).values():
            status_counts[cell.get("measurement_status") or "UNKNOWN"] += 1
    return {
        "per_paper": per_paper,
        "cases": sum(item["cases"] for item in per_paper),
        "lesions": sum(item["lesions"] for item in per_paper),
        "collections": sum(item["collections"] for item in per_paper),
        "episodes": sum(item["episodes"] for item in per_paper),
        "observations": observation_count,
        "quote_counts": dict(quote_counts),
        "measurement_status": dict(status_counts),
        "success": sum(1 for item in per_paper if item["paper_id"]),
        "failure": sum(1 for item in per_paper if item["paper_id"] is None),
    }


def write_audit(
    store: CorpusStore,
    attempted: list[str],
    stats: dict[str, Any],
    extra_notes: list[str],
    test_result: str,
) -> Path:
    payload = load_manifest(store)
    by_id = {row["candidate_id"]: row for row in payload["papers"]}
    lines = [
        "# Corpus batch 1",
        "",
        "Infrastructure version: phase4a.1",
        "Frozen ontology: PHASE 2.3 / PHASE 3.4 / biological_observation_extraction:v5",
        "Schema/rule/prompt were not modified.",
        "",
        "## Full text",
        "",
        f"- success: {stats['success']}",
        f"- failure/unavailable: {stats['failure']}",
        "",
    ]
    for item in stats["per_paper"]:
        row = by_id.get(item["candidate_id"], {})
        lines.append(
            f"- `{item['candidate_id']}` paper_id={item['paper_id']} "
            f"fulltext={item['fulltext']} access={row.get('access_source')} "
            f"bytes={row.get('bytes')} sha256={row.get('sha256')} "
            f"pages={row.get('page_count')} downloaded={row.get('download_date')}"
        )
    lines.extend(
        [
            "",
            "## Extraction counts (Batch 1 papers only)",
            "",
            f"- Case: {stats['cases']}",
            f"- lesion: {stats['lesions']}",
            f"- collection: {stats['collections']}",
            f"- regression episode: {stats['episodes']}",
            f"- observation: {stats['observations']}",
            "",
            "### Per paper",
            "",
        ]
    )
    for item in stats["per_paper"]:
        lines.append(
            f"- `{item['candidate_id']}` paper_id={item['paper_id']} "
            f"cases={item['cases']} lesions={item['lesions']} "
            f"collections={item['collections']} episodes={item['episodes']} "
            f"observations={item['observations']} "
            f"patients={item.get('patient_ids')}"
        )
    lines.extend(
        [
            "",
            "## Measurement status (Batch 1 case-matrix cells)",
            "",
        ]
    )
    if stats["measurement_status"]:
        for key, value in sorted(stats["measurement_status"].items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Quote verification (Batch 1 linked evidence)",
            "",
            f"- VERIFIED_EXACT: {stats['quote_counts'].get(QuoteVerificationStatus.VERIFIED_EXACT.value, 0)}",
            f"- VERIFIED_NORMALIZED: {stats['quote_counts'].get(QuoteVerificationStatus.VERIFIED_NORMALIZED.value, 0)}",
            f"- UNVERIFIED: {stats['quote_counts'].get(QuoteVerificationStatus.UNVERIFIED.value, 0)}",
            "",
            "## Ontology pressure points",
            "",
        ]
    )
    points = [
        point
        for point in (payload.get("pressure_points") or [])
        if str(point.get("candidate_id", "")).startswith("batch1-")
    ]
    if points:
        for point in points:
            lines.append(f"- {point.get('candidate_id')}: {point.get('note')}")
    else:
        lines.append("- none")
    excluded = [
        f"{cid}: {by_id[cid].get('exclusion_reason')}"
        for cid in attempted
        if by_id.get(cid, {}).get("extraction_status") == PaperIntakeState.EXCLUDED.value
    ]
    lines.extend(["", "## Excluded papers", ""])
    if excluded:
        for item in excluded:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Tests", "", f"- {test_result}", ""])
    if extra_notes:
        lines.extend(["## Notes", ""])
        for note in extra_notes:
            lines.append(f"- {note}")
        lines.append("")
    out = PROCESSED_DIR / "audit" / "corpus_batch_1.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def record_batch_pressure_points(store: CorpusStore, session) -> None:
    payload = load_manifest(store)
    existing = {
        (point.get("candidate_id"), point.get("note"))
        for point in payload.get("pressure_points") or []
    }

    def add(candidate_id: str, note: str) -> None:
        if (candidate_id, note) in existing:
            return
        record_pressure_point(payload, candidate_id=candidate_id, note=note)
        existing.add((candidate_id, note))

    add(
        "batch1-lynch-1978",
        "Frozen ontology has no dedicated host/genetic clinical-context type. "
        "Xeroderma pigmentosum was stored as CLINICAL_CONTEXT on one sibling, "
        "BIOLOGICAL_STATE on the other, and as genotype gene=XDP. "
        "Inflammatory infiltrate was kept as an observed Biological State only "
        "where the paper described cells.",
    )
    add(
        "batch1-levison-1955",
        "The legal PMC PDF includes adjacent BMJ articles on the same pages. "
        "Sparse 1955 dates have no richer UNKNOWN-date slot than missing values. "
        "Pulmonary findings used a 'collection' lesion_identifier without a "
        "LesionCollection row. Unmentioned findings must remain NOT_REPORTED.",
    )
    add(
        "batch1-khosravi-2016",
        "Frozen RegressionEpisode is case-level and cannot separately encode "
        "primary complete regression coexisting with later metastatic progression. "
        "Those facts were stored as separate observations/events and were not "
        "collapsed into a single contradictory episode.",
    )
    add(
        "batch1-paolino-2020",
        "Multiple melanocytic nevi have no LesionCollection row; remaining nevi "
        "were one DIAGNOSTIC_EVIDENCE observation. Dermoscopic regression was "
        "stored as DISEASE_PHENOTYPE/DERMATOLOGIC_PHENOTYPE because there is no "
        "dermoscopic observation domain.",
    )
    add(
        "batch1-nwabudike-2022",
        "No dermoscopic observation domain; collision-tumour impression versus "
        "histopathologic melanoma share one lesion. The first PHASE 2 attempt "
        "failed because REPORTED_ABSENT is valid only for primary_site. "
        "Lymphocytic infiltrate was stored as both DIAGNOSTIC_EVIDENCE and "
        "BIOLOGICAL_STATE.",
    )
    _ = session
    save_manifest(store, payload)


def mark_audited(store: CorpusStore) -> None:
    payload = load_manifest(store)
    for target in BATCH_CANDIDATES:
        row = find_duplicate(payload, candidate_id=target["candidate_id"])
        if row is None:
            continue
        if row["extraction_status"] == PaperIntakeState.EXTRACTED.value:
            _advance(row, "extraction_status", PaperIntakeState.AUDITED)
            row["quality_status"] = QualityStatus.REVIEW.value
    save_manifest(store, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corpus Expansion Batch 1")
    parser.add_argument(
        "--acquire-only",
        action="store_true",
        help="Register, download, and ingest only",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Extract already ingested Batch 1 papers",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    store = CorpusStore()
    register_candidates(store)
    attempted = [target["candidate_id"] for target in BATCH_CANDIDATES]
    if not args.extract_only:
        attempted = acquire_and_ingest(store)
    if args.acquire_only:
        print("acquire-only complete", flush=True)
        return
    extract_ingested(store)
    pipeline = CorpusPipeline(store)
    with SessionLocal() as session:
        summary = pipeline.rebuild_indexes_and_matrix(session)
        record_batch_pressure_points(store, session)
        mark_audited(store)
        stats = collect_batch_stats(session, store)
    print(f"index rebuild: {summary}", flush=True)
    print(f"batch stats: {stats}", flush=True)
    write_audit(
        store,
        attempted,
        stats,
        extra_notes=[
            "Frozen PHASE 2.3 / 3.4 ontology was not modified.",
            "Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.",
        ],
        test_result="pending",
    )


if __name__ == "__main__":
    main()
