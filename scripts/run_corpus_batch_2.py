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
from app.services.paper_parser import PdfTextExtractionError, parse_pdf


PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PAPERS_MANIFEST = PAPERS_DIR / "manifest.json"
PREFIX = "batch2-"

BATCH_CANDIDATES = [
    {
        "candidate_id": "batch2-haight-1984",
        "title": "Spontaneous Regression of Metastatic Visceral Malignant Melanoma",
        "doi": None,
        "pmid": "21278950",
        "pmcid": "PMC2153525",
        "year": 1984,
        "journal": "Canadian Family Physician",
        "filename": "haight_1984_pmc2153525.pdf",
        "selection_reason": (
            "Batch 2: pulmonary metastatic melanoma regression with long time-course"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC2153525.1/PMC2153525.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2153525/pdf/",
            "https://europepmc.org/articles/PMC2153525?pdf=render",
            "https://www.cfp.ca/content/cfp/30/6/1391.full.pdf",
            "https://www.cfp.ca/content/30/6/1391.full.pdf",
        ],
        "access_note": "PMC / Europe PMC / CFP publisher PDF",
    },
    {
        "candidate_id": "batch2-mikhail-1986",
        "title": "Spontaneous regression of metastatic malignant melanoma",
        "doi": "10.1111/j.1524-4725.1986.tb01939.x",
        "pmid": "3700829",
        "pmcid": None,
        "year": 1986,
        "journal": "The Journal of Dermatologic Surgery and Oncology",
        "filename": "mikhail_1986.pdf",
        "selection_reason": (
            "Batch 2: primary recurrence plus parotid/cervical/pulmonary metastases"
        ),
        "source_urls": [
            "https://europepmc.org/articles/PMC0?pdf=render",
            "https://deepblue.lib.umich.edu/bitstream/handle/2027.42/74434/j.1524-4725.1986.tb01939.x.pdf",
            "http://hdl.handle.net/2027.42/74434",
        ],
        "access_note": (
            "Not in PMC; Europe PMC hasPDF=N; Unpaywall oa_status=closed, "
            "has_repository_copy=false; OpenAlex is_oa=false; Deep Blue "
            "handle 2027.42/74434 is a restricted/non-OA deposit"
        ),
    },
    {
        "candidate_id": "batch2-kessler-1984",
        "title": "Spontaneous regression of primary malignant melanoma with metastases",
        "doi": "10.1097/00006534-198409000-00019",
        "pmid": "6473562",
        "pmcid": None,
        "year": 1984,
        "journal": "Plastic and Reconstructive Surgery",
        "filename": "kessler_1984.pdf",
        "selection_reason": (
            "Batch 2: presumed primary regression with metastatic disease"
        ),
        "source_urls": [],
        "access_note": (
            "Not in PMC; Europe PMC hasPDF=N; Unpaywall oa_status=closed, "
            "has_repository_copy=false; OpenAlex is_oa=false; LWW/PRS closed"
        ),
    },
    {
        "candidate_id": "batch2-macdougal-1976",
        "title": (
            "Spontaneous regression of the primary lesion of a metastatic "
            "malignant melanoma"
        ),
        "doi": "10.1097/00006534-197603000-00013",
        "pmid": "1257341",
        "pmcid": None,
        "year": 1976,
        "journal": "Plastic and Reconstructive Surgery",
        "filename": "macdougal_1976.pdf",
        "selection_reason": (
            "Batch 2: occult/regressed primary with metastatic melanoma"
        ),
        "source_urls": [],
        "access_note": (
            "Not in PMC; Europe PMC hasPDF=N; Unpaywall oa_status=closed, "
            "has_repository_copy=false; OpenAlex is_oa=false; LWW/PRS closed. "
            "Europe PMC OpenAlex 'Free' DOI link is the publisher landing page, "
            "not an OA PDF"
        ),
    },
    {
        "candidate_id": "batch2-grafton-1994",
        "title": "Regressing malignant melanoma",
        "doi": None,
        "pmid": "7844465",
        "pmcid": None,
        "year": 1994,
        "journal": "The Journal of the Louisiana State Medical Society",
        "filename": "grafton_1994.pdf",
        "selection_reason": (
            "Batch 2: two partial-regression cases and diagnostic limitation"
        ),
        "source_urls": [],
        "access_note": (
            "No DOI; not in PMC; Europe PMC hasPDF=N; OpenAlex is_oa=false, "
            "any_repository_has_fulltext=false; J La State Med Soc closed"
        ),
    },
]


def _access_source(url: str, pmcid: str | None) -> str:
    if "pmc-oa-opendata.s3.amazonaws.com" in url:
        return f"NIH NLM NCBI PMC Article Datasets on AWS ({pmcid}.1)"
    if "ncbi.nlm.nih.gov/pmc" in url:
        return f"NCBI PMC OA PDF ({pmcid})"
    if "europepmc.org" in url:
        return f"Europe PMC full-text PDF ({pmcid})"
    if "cfp.ca" in url:
        return "Canadian Family Physician publisher open-access PDF"
    if "deepblue.lib.umich.edu" in url or "hdl.handle.net" in url:
        return "University of Michigan Deep Blue institutional repository"
    return "Legal open-access PDF"


def _download(urls: list[str], dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not urls:
        raise RuntimeError("No legal PDF URLs to attempt")
    errors: list[str] = []
    with httpx.Client(follow_redirects=True, timeout=180.0) as client:
        for url in urls:
            if "PMC0" in url:
                errors.append(f"{url}: placeholder skipped")
                continue
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
        "notes": "Corpus Expansion Batch 2 candidate.",
        "role": "batch_2",
        "batch": 2,
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
    replaced = False
    for index, row in enumerate(payload["papers"]):
        ids = row.get("candidate_identifiers") or {}
        if (target["pmid"] and ids.get("pmid") == target["pmid"]) or (
            target["pmcid"] and ids.get("pmcid") == target["pmcid"]
        ):
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
            print(
                f"=== acquire {target['candidate_id']} "
                f"{target.get('pmcid') or target['pmid']} ===",
                flush=True,
            )
            try:
                source_url = _download(target["source_urls"], dest)
                sha256, size, pages = _verify_pdf(dest)
                parse_pdf(dest)
            except Exception as exc:
                print(f"FULLTEXT_UNAVAILABLE {target['candidate_id']}: {exc}", flush=True)
                pipeline.mark_fulltext_unavailable(
                    target["candidate_id"],
                    note=target["access_note"],
                )
                payload = load_manifest(store)
                row = find_duplicate(payload, candidate_id=target["candidate_id"])
                if row:
                    row["notes"] = target["access_note"]
                    row["access_source"] = target["access_note"]
                    save_manifest(store, payload)
                _update_papers_manifest(
                    target,
                    {
                        "title": target["title"],
                        "filename": None,
                        "source_url": (
                            f"https://pubmed.ncbi.nlm.nih.gov/{target['pmid']}/"
                        ),
                        "access_source": target["access_note"],
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

            paper = pipeline.ingest_manual_pdf(
                session, target["candidate_id"], dest, PROCESSED_DIR
            )
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
                    "source_version": (
                        f"{target['pmcid']}.1" if target["pmcid"] else None
                    ),
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
            print(
                f"=== PHASE 2 extract paper={paper_id} ({target['candidate_id']}) ===",
                flush=True,
            )
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
        if str(row.get("candidate_id", "")).startswith(PREFIX)
    ]
    observation_count = 0
    quote_counts: Counter[str] = Counter()
    case_ids: list[int] = []
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
            quote_counts[item.verification_status or "UNKNOWN"] += 1
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
        "# Corpus batch 2",
        "",
        "Infrastructure version: phase4a.1",
        "Frozen ontology: PHASE 2.3 / PHASE 3.4 / biological_observation_extraction:v5",
        "Schema/rule/prompt were not modified.",
        "",
        f"- candidates attempted: {len(attempted)}",
        f"- full text success: {stats['success']}",
        f"- full text failure/unavailable: {stats['failure']}",
        "",
        "## Full text",
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
            "## Extraction counts (Batch 2 papers with full text)",
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
    lines.extend(["", "## Measurement status (Batch 2 case-matrix cells)", ""])
    if stats["measurement_status"]:
        for key, value in sorted(stats["measurement_status"].items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none (no extracted Batch 2 case rows)")
    lines.extend(
        [
            "",
            "## Quote verification (Batch 2 linked evidence)",
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
        if str(point.get("candidate_id", "")).startswith(PREFIX)
        or str(point.get("batch")) == "2"
    ]
    if points:
        for point in points:
            status = point.get("repeat_status")
            prefix = f"[{status}] " if status else ""
            lines.append(f"- {prefix}{point.get('candidate_id')}: {point.get('note')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Repeated Batch 1 pressure-point watch", ""])
    watch = payload.get("batch2_repeat_watch") or []
    if watch:
        for item in watch:
            lines.append(f"- {item['item']}: {item['status']} — {item['note']}")
    else:
        lines.append("- not applicable (no Batch 2 full text extracted)")
    lines.extend(["", "## Possible duplicate reports", ""])
    dups = payload.get("possible_duplicate_reports") or []
    batch_dups = [item for item in dups if str(item.get("candidate_id", "")).startswith(PREFIX)]
    if batch_dups:
        for item in batch_dups:
            lines.append(f"- POSSIBLE_DUPLICATE_REPORT {item}")
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
    out = PROCESSED_DIR / "audit" / "corpus_batch_2.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def record_batch_pressure_points(store: CorpusStore, session) -> None:
    payload = load_manifest(store)
    existing = {
        (point.get("candidate_id"), point.get("note"))
        for point in payload.get("pressure_points") or []
    }

    def add(candidate_id: str, note: str, repeat_status: str | None = None) -> None:
        if (candidate_id, note) in existing:
            return
        record_pressure_point(payload, candidate_id=candidate_id, note=note)
        payload["pressure_points"][-1]["batch"] = 2
        if repeat_status:
            payload["pressure_points"][-1]["repeat_status"] = repeat_status
        existing.add((candidate_id, note))

    row = find_duplicate(payload, candidate_id="batch2-haight-1984")
    if row and row.get("paper_id"):
        cases, _phase2, phase3 = seed_cases_and_runs(session, row["paper_id"])
        observations = list(
            session.scalars(
                select(BiologicalObservation).where(
                    BiologicalObservation.case_id.in_([case.id for case in cases] or [-1]),
                    BiologicalObservation.created_from_run_id.in_(
                        [run.id for run in phase3] or [-1]
                    ),
                )
            )
        )
        collections = list(
            session.scalars(
                select(LesionCollection).where(
                    LesionCollection.case_id.in_([case.id for case in cases] or [-1]),
                    LesionCollection.created_from_run_id.in_(
                        [run.id for run in phase3] or [-1]
                    ),
                )
            )
        )
        _cases, lesions, episodes, _states = load_seed_entities(
            session, [case.id for case in cases], [run.id for run in phase3]
        )
        pulmonary_obs = [
            obs
            for obs in observations
            if "pulmon" in (obs.variable_name or "").lower()
            or "pulmon" in str(obs.normalized_variable or "").lower()
        ]
        lung_lesions = [
            lesion
            for lesion in lesions
            if "lung" in (lesion.organ or "").lower()
            or "pulmon" in (lesion.canonical_name or "").lower()
        ]
        if pulmonary_obs and not collections and not lung_lesions:
            add(
                "batch2-haight-1984",
                "Multiple pulmonary nodules have neither a Lesion row nor a "
                "LesionCollection. Some nodules disappeared on serial films "
                "while others appeared later; the frozen model cannot group "
                "that imaging-only mixed course.",
                "WORSENED",
            )
        if any(
            "histological_documentation_of_pulmonary" in str(obs.normalized_variable or "").lower()
            for obs in observations
        ):
            add(
                "batch2-haight-1984",
                "The paper states there was no histological documentation of "
                "the pulmonary nodules, but that clause was stored as "
                "DIAGNOSTIC_EVIDENCE HISTOLOGICAL_DOCUMENTATION_OF_PULMONARY_NODULES "
                "with an empty value instead of REPORTED_ABSENT.",
                "NEW",
            )
        if len(episodes) <= 1 and pulmonary_obs:
            add(
                "batch2-haight-1984",
                "Case-level RegressionEpisode still cannot separately encode "
                "neck recurrence versus later mixed pulmonary-nodule regression "
                "and new nodules.",
                "REPEATED",
            )
    payload["possible_duplicate_reports"] = [
        item
        for item in (payload.get("possible_duplicate_reports") or [])
        if not str(item.get("candidate_id", "")).startswith(PREFIX)
    ]
    payload["batch2_repeat_watch"] = payload.get("batch2_repeat_watch") or []
    save_manifest(store, payload)


def classify_repeat_watch(store: CorpusStore, session) -> None:
    payload = load_manifest(store)
    row = find_duplicate(payload, candidate_id="batch2-haight-1984")
    watch = []

    def add(item: str, status: str, note: str) -> None:
        watch.append({"item": item, "status": status, "note": note})

    if not row or not row.get("paper_id"):
        add(
            "LesionCollection missing",
            "NOT_OBSERVABLE",
            "No Batch 2 full text extracted for this watch item except Haight pending.",
        )
        payload["batch2_repeat_watch"] = watch
        save_manifest(store, payload)
        return

    cases, _phase2, phase3 = seed_cases_and_runs(session, row["paper_id"])
    observations = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.case_id.in_([case.id for case in cases] or [-1]),
                BiologicalObservation.created_from_run_id.in_(
                    [run.id for run in phase3] or [-1]
                ),
            )
        )
    )
    collections = list(
        session.scalars(
            select(LesionCollection).where(
                LesionCollection.case_id.in_([case.id for case in cases] or [-1]),
                LesionCollection.created_from_run_id.in_(
                    [run.id for run in phase3] or [-1]
                ),
            )
        )
    )
    _cases, lesions, _episodes, _states = load_seed_entities(
        session, [case.id for case in cases], [run.id for run in phase3]
    )
    pulmonary_obs = [
        obs
        for obs in observations
        if "pulmon" in (obs.variable_name or "").lower()
        or "pulmon" in str(obs.normalized_variable or "").lower()
    ]
    lung_lesions = [
        lesion
        for lesion in lesions
        if "lung" in (lesion.organ or "").lower()
        or "pulmon" in (lesion.canonical_name or "").lower()
    ]
    if collections:
        add(
            "LesionCollection missing",
            "RESOLVED_BY_EXISTING_MODEL",
            "Haight pulmonary nodules received a LesionCollection row.",
        )
    elif pulmonary_obs and not lung_lesions:
        add(
            "LesionCollection missing",
            "WORSENED",
            "Haight pulmonary nodules have no collection and no lesion rows, "
            "only unscoped observations.",
        )
    elif lung_lesions:
        add(
            "LesionCollection missing",
            "REPEATED",
            "Haight pulmonary findings have lesion rows but no collection.",
        )
    else:
        add(
            "LesionCollection missing",
            "NEW",
            "Haight did not surface a pulmonary collection or multiple-nodule lesion group.",
        )

    add(
        "host predisposition expression",
        "RESOLVED_BY_EXISTING_MODEL",
        "Haight has no XP/host-genotype claim; the Batch 1 host-slot gap did not recur.",
    )
    dermo = [
        obs
        for obs in observations
        if "dermoscop" in (obs.variable_name or "").lower()
        or "dermoscop" in (obs.normalized_variable or "").lower()
    ]
    add(
        "dermoscopic/pathology domain ambiguity",
        "RESOLVED_BY_EXISTING_MODEL" if not dermo else "REPEATED",
        "Haight has no dermoscopic findings."
        if not dermo
        else "Dermoscopic wording appeared without a dedicated domain.",
    )
    add(
        "retrospective vs directly observed regression",
        "RESOLVED_BY_EXISTING_MODEL",
        "Haight pulmonary change is serial chest-film observation, not a "
        "retrospective occult-primary diagnosis. The Batch 1 occult/retrospective "
        "gap did not recur.",
    )
    add(
        "primary regression + metastatic persistence/progression coexistence",
        "REPEATED",
        "Haight has neck recurrence then later mixed pulmonary-nodule regression "
        "and new nodules; one case-level episode remains.",
    )
    add(
        "old scanned PDF article-boundary contamination",
        "RESOLVED_BY_EXISTING_MODEL",
        "Haight PDF is the target article plus its French summary. No adjacent "
        "unrelated article was ingested, and Nathanson review cases were not "
        "created as patients.",
    )
    payload["batch2_repeat_watch"] = watch
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
    parser = argparse.ArgumentParser(description="Corpus Expansion Batch 2")
    parser.add_argument("--acquire-only", action="store_true")
    parser.add_argument("--extract-only", action="store_true")
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
        classify_repeat_watch(store, session)
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
            "Abstracts were not used as Evidence.",
            "Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.",
        ],
        test_result="pending",
    )


if __name__ == "__main__":
    main()
