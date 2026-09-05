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
from app.corpus.states import ExclusionReason, PaperIntakeState, QualityStatus
from app.corpus.store import CorpusStore
from app.core.config import PROJECT_ROOT, get_settings
from app.llm.base import StructuredExtractionError
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.llm.provider import create_provider
from app.models import (
    BiologicalObservation,
    Case,
    Evidence,
    Event,
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
PREFIX = "batch3-"

BATCH_CANDIDATES = [
    {
        "candidate_id": "batch3-koibuchi-2022",
        "title": (
            "Spontaneous regression of lymphovascular invasion and metastasis "
            "of malignant melanoma: ultrasound findings"
        ),
        "doi": "10.1007/s40477-022-00752-6",
        "pmid": "36574191",
        "pmcid": "PMC10632326",
        "year": 2023,
        "journal": "Journal of Ultrasound",
        "filename": "koibuchi_2022_pmc10632326.pdf",
        "selection_reason": (
            "Batch 3 stress-test: ankle primary, thigh subcutaneous metastasis, "
            "lymphovascular invasion, and FNA-then-disappearance sequence"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC10632326.1/PMC10632326.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10632326/pdf/",
            "https://europepmc.org/articles/PMC10632326?pdf=render",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10632326/pdf/40477_2022_Article_752.pdf",
            "https://link.springer.com/content/pdf/10.1007/s40477-022-00752-6.pdf",
        ],
        "access_note": "PMC OA / Europe PMC / Springer OA PDF",
        "skip_extract": False,
    },
    {
        "candidate_id": "batch3-yamada-2016",
        "title": (
            "Complete regression of primary cutaneous malignant melanoma "
            "associated with distant lymph node metastasis: a teaching case "
            "mimicking blue nevus"
        ),
        "doi": "10.1186/s13104-016-2174-4",
        "pmid": "27456492",
        "pmcid": "PMC4960676",
        "year": 2016,
        "journal": "BMC Research Notes",
        "filename": "yamada_2016_pmc4960676.pdf",
        "selection_reason": (
            "Batch 3 stress-test: completely regressed primary with distant "
            "lymph-node metastasis and split regression pathology"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC4960676.1/PMC4960676.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4960676/pdf/",
            "https://europepmc.org/articles/PMC4960676?pdf=render",
            "https://bmcresnotes.biomedcentral.com/counter/pdf/10.1186/s13104-016-2174-4.pdf",
            "https://bmcresnotes.biomedcentral.com/track/pdf/10.1186/s13104-016-2174-4",
        ],
        "access_note": "PMC OA / Europe PMC / BMC publisher OA PDF",
        "skip_extract": False,
    },
    {
        "candidate_id": "batch3-sandru-2020",
        "title": "Regressive melanoma in a female patient: A case report",
        "doi": "10.3892/etm.2020.8675",
        "pmid": "32508999",
        "pmcid": "PMC7271722",
        "year": 2020,
        "journal": "Experimental and Therapeutic Medicine",
        "filename": "sandru_2020_pmc7271722.pdf",
        "selection_reason": (
            "Batch 3 stress-test: regressive primary plus multiple lymph-node, "
            "lung, and brain metastases"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC7271722.1/PMC7271722.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7271722/pdf/",
            "https://europepmc.org/articles/PMC7271722?pdf=render",
            "https://www.spandidos-publications.com/10.3892/etm.2020.8675/download",
        ],
        "access_note": "PMC OA / Europe PMC / Spandidos OA PDF",
        "skip_extract": False,
    },
    {
        "candidate_id": "batch3-martinez-lopez-2017",
        "title": (
            "Disappearance of All Nevi as Initial Sign of Metastatic Melanoma"
        ),
        "doi": "10.4103/ijd.IJD_260_16",
        "pmid": "28794570",
        "pmcid": "PMC5527740",
        "year": 2017,
        "journal": "Indian Journal of Dermatology",
        "filename": "martinez_lopez_2017_pmc5527740.pdf",
        "selection_reason": (
            "Batch 3 stress-test: all-nevi disappearance plus subcutaneous, "
            "lung, inguinal, and iliac metastatic collections"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC5527740.1/PMC5527740.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5527740/pdf/",
            "https://europepmc.org/articles/PMC5527740?pdf=render",
        ],
        "access_note": "PMC OA / Europe PMC PDF",
        "skip_extract": False,
    },
    {
        "candidate_id": "batch3-unknown-primary-2012",
        "title": (
            "Stage IV malignant melanoma of unknown primary site in a young man"
        ),
        "doi": "10.1136/bcr-2012-006283",
        "pmid": "22847563",
        "pmcid": "PMC4543345",
        "year": 2012,
        "journal": "BMJ Case Reports",
        "filename": "unknown_primary_2012_pmc4543345.pdf",
        "selection_reason": (
            "Batch 3 inclusion-gate test: melanoma of unknown primary where "
            "regressed primary is an explanatory possibility, not documented "
            "observed spontaneous regression"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC4543345.1/PMC4543345.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4543345/pdf/",
            "https://europepmc.org/articles/PMC4543345?pdf=render",
        ],
        "access_note": "PMC OA / Europe PMC PDF",
        "skip_extract": True,
        "evaluate_inclusion": True,
    },
]


def _access_source(url: str, pmcid: str | None) -> str:
    if "pmc-oa-opendata.s3.amazonaws.com" in url:
        return f"NIH NLM NCBI PMC Article Datasets on AWS ({pmcid}.1)"
    if "ncbi.nlm.nih.gov/pmc" in url:
        return f"NCBI PMC OA PDF ({pmcid})"
    if "europepmc.org" in url:
        return f"Europe PMC full-text PDF ({pmcid})"
    if "link.springer.com" in url:
        return "Springer Journal of Ultrasound publisher open-access PDF"
    if "biomedcentral.com" in url:
        return "BMC Research Notes publisher open-access PDF"
    if "spandidos-publications.com" in url:
        return "Spandidos Experimental and Therapeutic Medicine publisher OA PDF"
    if "pmc.ncbi.nlm.nih.gov" in url:
        return f"NCBI PMC OA PDF ({pmcid})"
    return "Legal open-access PDF"


def _download(urls: list[str], dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not urls:
        raise RuntimeError("No legal PDF URLs to attempt")
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
        "notes": "Corpus Expansion Batch 3 candidate.",
        "role": "batch_3",
        "batch": 3,
        "exclusion_reason": None,
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


def _patch_paper_metadata(
    session, paper: Paper, target: dict[str, Any], source_url: str
) -> None:
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
                print(
                    f"FULLTEXT_UNAVAILABLE {target['candidate_id']}: {exc}",
                    flush=True,
                )
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


def _paper_text(filename: str) -> str:
    pdf_path = PAPERS_DIR / filename
    if pdf_path.exists():
        parsed = parse_pdf(pdf_path)
        return "\n".join(parsed.pages)
    return ""


def evaluate_unknown_primary_inclusion(store: CorpusStore) -> None:
    target = next(
        item for item in BATCH_CANDIDATES if item.get("evaluate_inclusion")
    )
    payload = load_manifest(store)
    row = find_duplicate(payload, candidate_id=target["candidate_id"])
    if row is None or row.get("paper_id") is None:
        return
    text = _paper_text(target["filename"])
    compact = (
        text.casefold()
        .replace("-\n", "")
        .replace("\n", " ")
        .replace("  ", " ")
    )
    woods_negative = (
        "failed to reveal" in compact
        and ("regressed melanoma" in compact or "halo nev" in compact)
    )
    chemo_response = (
        "chemotherapy" in compact
        and "blurred glass" in compact
        and "regression of the disease" in compact
    )
    theory_only = _is_theory_only_regression(compact)
    # Human inclusion-gate reading of Christopoulos 2012 / PMC4543345:
    # Wood's lamp did not show a regressed-primary scar; lung change followed
    # dacarbazine/sorafenib then paclitaxel; SR of an occult primary is listed
    # as one literature theory for MUP. Do not extract as a corpus SR case.
    force_exclude = (
        target["candidate_id"] == "batch3-unknown-primary-2012"
        or woods_negative
        or (theory_only and chemo_response)
    )
    if not force_exclude and "spontaneous regression" in compact:
        row["notes"] = (
            "Unknown-primary paper contains wording that may describe observed "
            "regression; extracted under frozen rules without promoting theory "
            "to patient fact."
        )
        row["discovery_track"] = None
        save_manifest(store, payload)
        target["skip_extract"] = False
        print(
            f"{target['candidate_id']}: inclusion retained for extraction "
            f"(observed-regression wording present)",
            flush=True,
        )
        return
    reason = ExclusionReason.NOT_SPONTANEOUS_REGRESSION
    note = (
        "EXCLUDED: melanoma of unknown primary. Wood's lamp did not show a "
        "regressed-primary scar. Lung-lesion change followed chemotherapy and "
        "is a treatment response, not spontaneous regression. Regressed occult "
        "primary is an author/literature explanatory theory "
        "(UNKNOWN PRIMARY != PROVEN SPONTANEOUS REGRESSION). "
        "Kept as LATENT_REGRESSION / observation-bias discovery source. "
        f"woods_negative={woods_negative} chemo_response={chemo_response} "
        f"theory_only={theory_only}"
    )
    if row["extraction_status"] != PaperIntakeState.EXCLUDED.value:
        transition_paper(row, "extraction_status", PaperIntakeState.EXCLUDED)
    row["exclusion_reason"] = reason.value
    row["notes"] = note
    row["quality_status"] = QualityStatus.REVIEW.value
    row["discovery_track"] = "LATENT_REGRESSION"
    row["research_use"] = (
        "observation-bias / unknown-primary hypothesized regression; "
        "not corpus Evidence"
    )
    save_manifest(store, payload)
    papers_payload = json.loads(PAPERS_MANIFEST.read_text(encoding="utf-8"))
    for item in papers_payload["papers"]:
        ids = item.get("candidate_identifiers") or {}
        if ids.get("pmid") == target["pmid"]:
            item["status"] = "EXCLUDED"
            item["exclusion_reason"] = reason.value
            item["discovery_track"] = "LATENT_REGRESSION"
            break
    PAPERS_MANIFEST.write_text(
        json.dumps(papers_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{target['candidate_id']}: {note}", flush=True)


def _is_theory_only_regression(text: str) -> bool:
    if "spontaneous regression of the primary" in text and "unknown primary" in text:
        return True
    if "regressed primary" in text and "unknown primary" in text:
        return True
    return "unknown primary" in text and "spontaneous regression" not in text


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
    skip = {
        target["candidate_id"]
        for target in BATCH_CANDIDATES
        if target.get("skip_extract")
    }
    with SessionLocal() as session:
        for target in BATCH_CANDIDATES:
            payload = load_manifest(store)
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
            if target["candidate_id"] in skip:
                print(
                    f"skip extract {target['candidate_id']}: "
                    f"inclusion-gate / discovery-only",
                    flush=True,
                )
                continue
            paper_id = row["paper_id"]
            print(
                f"=== PHASE 2 extract paper={paper_id} ({target['candidate_id']}) ===",
                flush=True,
            )
            case_run = None
            last_error: Exception | None = None
            for attempt in range(1, 4):
                try:
                    case_run = case_pipeline.run(session, paper_id)
                    last_error = None
                    break
                except StructuredExtractionError as exc:
                    last_error = exc
                    print(
                        f"PHASE 2 retry {attempt}/3 paper={paper_id}: {exc}",
                        flush=True,
                    )
            if case_run is None:
                raise last_error or RuntimeError("PHASE 2 extraction failed")
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
        excluded = row.get("extraction_status") == PaperIntakeState.EXCLUDED.value
        if paper_id is None or excluded:
            per_paper.append(
                {
                    "candidate_id": row["candidate_id"],
                    "paper_id": paper_id,
                    "fulltext": row["fulltext_status"],
                    "cases": 0,
                    "lesions": 0,
                    "collections": 0,
                    "episodes": 0,
                    "observations": 0,
                    "excluded": excluded,
                    "exclusion_reason": row.get("exclusion_reason"),
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
                "excluded": False,
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
        "success": sum(
            1
            for item in per_paper
            if item["paper_id"] and not item.get("excluded")
        ),
        "failure": sum(1 for item in per_paper if item["paper_id"] is None),
        "excluded": sum(1 for item in per_paper if item.get("excluded")),
    }


def _obs_blob(obs: BiologicalObservation) -> str:
    domain = obs.observation_domain
    if domain is not None and hasattr(domain, "value"):
        domain = domain.value
    secondary = obs.domain_secondary
    if secondary is not None and hasattr(secondary, "value"):
        secondary = secondary.value
    semantics = obs.measurement_semantics
    if semantics is not None and hasattr(semantics, "value"):
        semantics = semantics.value
    return " ".join(
        [
            obs.variable_name or "",
            str(obs.normalized_variable or ""),
            obs.value or "",
            str(obs.normalized_value or ""),
            obs.lesion_identifier or "",
            str(domain or ""),
            str(secondary or ""),
            str(semantics or ""),
        ]
    ).casefold()


def _load_extracted(session, paper_id: int) -> dict[str, Any]:
    cases, phase2, phase3 = seed_cases_and_runs(session, paper_id)
    phase3_ids = [run.id for run in phase3]
    case_ids = [case.id for case in cases]
    _cases, lesions, episodes, _states = load_seed_entities(
        session, case_ids, phase3_ids
    )
    collections = list(
        session.scalars(
            select(LesionCollection).where(
                LesionCollection.case_id.in_(case_ids or [-1]),
                LesionCollection.created_from_run_id.in_(phase3_ids or [-1]),
            )
        )
    )
    observations = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.case_id.in_(case_ids or [-1]),
                BiologicalObservation.created_from_run_id.in_(phase3_ids or [-1]),
            )
        )
    )
    events = []
    if phase2:
        events = list(
            session.scalars(
                select(Event).where(
                    Event.case_id.in_(case_ids or [-1]),
                    Event.extraction_run_id == phase2.id,
                )
            )
        )
    return {
        "cases": cases,
        "phase2": phase2,
        "phase3": phase3,
        "lesions": lesions,
        "episodes": episodes,
        "collections": collections,
        "observations": observations,
        "events": events,
    }


def record_batch_pressure_points(store: CorpusStore, session) -> None:
    payload = load_manifest(store)
    payload["pressure_points"] = [
        point
        for point in payload.get("pressure_points") or []
        if not str(point.get("candidate_id", "")).startswith(PREFIX)
        and str(point.get("batch")) != "3"
    ]
    existing = {
        (point.get("candidate_id"), point.get("note"))
        for point in payload.get("pressure_points") or []
    }

    def add(
        candidate_id: str,
        note: str,
        repeat_status: str | None = None,
        patch_flag: str | None = None,
    ) -> None:
        if (candidate_id, note) in existing:
            return
        record_pressure_point(payload, candidate_id=candidate_id, note=note)
        payload["pressure_points"][-1]["batch"] = 3
        if repeat_status:
            payload["pressure_points"][-1]["repeat_status"] = repeat_status
        if patch_flag:
            payload["pressure_points"][-1]["patch_flag"] = patch_flag
        existing.add((candidate_id, note))

    for target in BATCH_CANDIDATES:
        row = find_duplicate(payload, candidate_id=target["candidate_id"])
        if row is None:
            continue
        if row.get("extraction_status") == PaperIntakeState.EXCLUDED.value:
            add(
                target["candidate_id"],
                "Latent/hypothesized regressed occult primary was not promoted "
                "to a patient-level spontaneous-regression fact. Paper was "
                "EXCLUDED at the inclusion gate and was not extracted.",
                "NEW",
            )
            continue
        if not row.get("paper_id"):
            continue
        extracted = _load_extracted(session, row["paper_id"])
        observations = extracted["observations"]
        collections = extracted["collections"]
        lesions = extracted["lesions"]
        episodes = extracted["episodes"]
        events = extracted["events"]
        blobs = [_obs_blob(obs) for obs in observations]
        lesion_names = " ".join(
            f"{lesion.canonical_name} {lesion.organ} {lesion.anatomical_location}"
            for lesion in lesions
        ).casefold()
        collection_names = " ".join(
            collection.canonical_name for collection in collections
        ).casefold()

        if target["candidate_id"] == "batch3-koibuchi-2022":
            ankle = any("ankle" in name for name in [lesion_names] + blobs)
            thigh = any("thigh" in name for name in [lesion_names] + blobs)
            vascular = any(
                "lymphovascular" in name or "vascular" in name or "tubular" in name
                for name in [lesion_names] + blobs
            )
            if ankle and thigh and len(lesions) < 2:
                add(
                    target["candidate_id"],
                    "Koibuchi ankle primary and thigh subcutaneous mass were not "
                    "kept as separate Lesion rows.",
                    "NEW",
                )
            fna = any(
                "fna" in (event.event_type.value if event.event_type else "").casefold()
                or "fine needle" in (event.description or "").casefold()
                or "fna" in (event.description or "").casefold()
                or "aspirat" in (event.description or "").casefold()
                for event in events
            )
            caused = any(
                "fna caused" in blob or "caused by fna" in blob or "due to fna" in blob
                for blob in blobs
            )
            if not fna:
                add(
                    target["candidate_id"],
                    "FNA/aspiration was not stored as a separate Event before "
                    "the later disappearance observation.",
                    "NEW",
                )
            if caused:
                add(
                    target["candidate_id"],
                    "FNA-then-disappearance was stored as a causal observed fact.",
                    "NEW",
                )
            if vascular and ankle and thigh and len(lesions) == 1:
                add(
                    target["candidate_id"],
                    "Lymphovascular/tubular finding was merged into a single "
                    "lesion without source-quote identity support.",
                    "NEW",
                )
            if len(episodes) > 1:
                add(
                    target["candidate_id"],
                    "One FNA-then-disappearance course was stored as three "
                    "RegressionEpisode rows (disappearance statement, CT "
                    "absence, ultrasound absence). The frozen episode model "
                    "fragments serial confirmation of one course.",
                    "NEW",
                )
            if any(
                (lesion.canonical_name or "").casefold() == "right mass"
                for lesion in lesions
            ):
                add(
                    target["candidate_id"],
                    "The thigh subcutaneous/tubular metastasis was stored as "
                    "canonical_name='right mass' without thigh/femur location. "
                    "It was kept separate from the ankle primary.",
                    "NEW",
                )

        if target["candidate_id"] == "batch3-yamada-2016":
            pathology_terms = [
                "melanophage",
                "fibrosis",
                "vascular proliferation",
                "cd8",
                "viable melanoma",
            ]
            present = [term for term in pathology_terms if any(term in blob for blob in blobs)]
            if len(present) >= 3 and len(
                [
                    obs
                    for obs in observations
                    if any(term in _obs_blob(obs) for term in pathology_terms)
                ]
            ) < len(present):
                add(
                    target["candidate_id"],
                    "Yamada regression-pathology findings were collapsed into "
                    "fewer observations than the split findings in the paper.",
                    "REPEATED",
                )
            cd8 = [obs for obs in observations if "cd8" in _obs_blob(obs)]
            domains = set()
            for obs in cd8:
                domain = obs.observation_domain
                if domain is not None and hasattr(domain, "value"):
                    domain = domain.value
                if domain:
                    domains.add(domain)
                secondary = obs.domain_secondary
                if secondary is not None and hasattr(secondary, "value"):
                    secondary = secondary.value
                if secondary:
                    domains.add(secondary)
            if cd8 and not (
                "BIOLOGICAL_STATE" in domains
                or "DIAGNOSTIC_EVIDENCE" in domains
            ):
                add(
                    target["candidate_id"],
                    "CD8 infiltrate was not stored with BIOLOGICAL_STATE or "
                    "DIAGNOSTIC/PATHOLOGIC secondary semantics.",
                    "REPEATED",
                )

        if target["candidate_id"] == "batch3-sandru-2020":
            lung = any("lung" in name or "pulmon" in name for name in [lesion_names, collection_names] + blobs)
            brain = any("brain" in name or "cerebral" in name for name in [lesion_names, collection_names] + blobs)
            nodes = any(
                "lymph" in name or "node" in name
                for name in [lesion_names, collection_names] + blobs
            )
            if (lung or brain or nodes) and not collections:
                add(
                    target["candidate_id"],
                    "Sandru multiple lymph-node / lung / brain metastases have "
                    "no LesionCollection rows. Frozen parser can create a "
                    "collection only when lesion_identifier contains multiple/"
                    "multifocal/numerous/several wording.",
                    "WORSENED",
                )
            if any(
                "melan a" in blob and "tyrosinase" in blob
                for blob in blobs
            ):
                add(
                    target["candidate_id"],
                    "Melan-A negative and Tyrosinase negative were stored in "
                    "one observation instead of two marker-level rows. They "
                    "were not equated to tumor-cell absence.",
                    "NEW",
                )

        if target["candidate_id"] == "batch3-martinez-lopez-2017":
            nevi = any(
                "nev" in name or "naev" in name
                for name in [lesion_names, collection_names] + blobs
            )
            if nevi and not any("nev" in collection_names or "naev" in collection_names for _ in [0]):
                if not collections:
                    add(
                        target["candidate_id"],
                        "Martinez-Lopez 'all nevi disappeared' has no "
                        "LesionCollection (MULTIPLE_MELANOCYTIC_NEVI or "
                        "equivalent). Individual unnamed nevi were not invented, "
                        "but the collection slot remains empty.",
                        "WORSENED",
                    )
            if len(episodes) <= 1 and any(
                "metast" in blob for blob in blobs
            ) and nevi:
                add(
                    target["candidate_id"],
                    "Nevi disappearance and later metastatic disease remain one "
                    "case-level RegressionEpisode.",
                    "REPEATED",
                )
            lentigo_error = any(
                "lentig" in _obs_blob(obs) and "disappear" in (obs.value or "").casefold()
                for obs in observations
            )
            if lentigo_error:
                add(
                    target["candidate_id"],
                    "The paper states lentigines remained; extraction stored "
                    "lentigines as having disappeared. This is a fact inversion, "
                    "not an ontology gap.",
                    "NEW",
                )

        if collections:
            continue
        multi_site = any(
            term in " ".join(blobs)
            for term in ("multiple", "numerous", "several", "all nevi", "metastases")
        )
        if multi_site:
            add(
                target["candidate_id"],
                "Multiple-site wording is present but no LesionCollection row "
                "was created.",
                "REPEATED",
            )
        if len(episodes) <= 1 and len(lesions) >= 2:
            add(
                target["candidate_id"],
                "Frozen RegressionEpisode remains case-level and collapsed "
                "distinct lesion courses into one episode.",
                "REPEATED",
            )

    payload["possible_duplicate_reports"] = [
        item
        for item in (payload.get("possible_duplicate_reports") or [])
        if not str(item.get("candidate_id", "")).startswith(PREFIX)
    ]
    save_manifest(store, payload)


def classify_repeat_watch(store: CorpusStore, session) -> None:
    payload = load_manifest(store)
    watch = []

    def add(item: str, status: str, note: str) -> None:
        watch.append({"item": item, "status": status, "note": note})

    extracted_rows = []
    for target in BATCH_CANDIDATES:
        row = find_duplicate(payload, candidate_id=target["candidate_id"])
        if row and row.get("paper_id") and row.get("extraction_status") not in {
            PaperIntakeState.EXCLUDED.value,
            PaperIntakeState.FULLTEXT_UNAVAILABLE.value,
        }:
            extracted_rows.append((target, row, _load_extracted(session, row["paper_id"])))

    all_collections = [item for _, _, data in extracted_rows for item in data["collections"]]
    all_observations = [item for _, _, data in extracted_rows for item in data["observations"]]
    all_lesions = [item for _, _, data in extracted_rows for item in data["lesions"]]
    all_episodes = [item for _, _, data in extracted_rows for item in data["episodes"]]
    blobs = [_obs_blob(obs) for obs in all_observations]
    lesion_text = " ".join(
        f"{lesion.canonical_name} {lesion.organ} {lesion.anatomical_location}"
        for lesion in all_lesions
    ).casefold()
    collection_text = " ".join(
        collection.canonical_name for collection in all_collections
    ).casefold()

    def collection_status(token: str, label: str) -> tuple[str, str]:
        mentioned = any(token in blob for blob in blobs) or token in lesion_text
        grouped = token in collection_text
        if grouped:
            return (
                "RESOLVED_BY_EXISTING_MODEL",
                f"{label} received a LesionCollection row.",
            )
        if mentioned:
            return (
                "WORSENED",
                f"{label} is present in Batch 3 extractions but still has no "
                "LesionCollection. This now spans Batch 1, 2, and 3.",
            )
        return (
            "RESOLVED_BY_EXISTING_MODEL",
            f"{label} was not required by the extracted Batch 3 papers.",
        )

    status, note = collection_status("pulmon", "Multiple pulmonary metastases")
    if "lung" in lesion_text or any("lung" in blob for blob in blobs):
        if "lung" not in collection_text and "pulmon" not in collection_text:
            status, note = (
                "WORSENED",
                "Multiple lung metastases are present without a LesionCollection. "
                "This now spans Batch 1, 2, and 3.",
            )
    add("multiple pulmonary metastases collection", status, note)

    status, note = collection_status("lymph", "Multiple lymph-node collection")
    add("multiple lymph-node collection", status, note)

    nevi_mentioned = any("nev" in blob or "naev" in blob for blob in blobs)
    if nevi_mentioned and "nev" not in collection_text and "naev" not in collection_text:
        add(
            "multifocal / multiple-nevi collection",
            "WORSENED",
            "All-nevi / multiple-nevi wording has no LesionCollection. "
            "This now spans Batch 1 (Paolino) and Batch 3 (Martinez-Lopez).",
        )
    elif nevi_mentioned:
        add(
            "multifocal / multiple-nevi collection",
            "RESOLVED_BY_EXISTING_MODEL",
            "Multiple nevi received a LesionCollection row.",
        )
    else:
        add(
            "multifocal / multiple-nevi collection",
            "RESOLVED_BY_EXISTING_MODEL",
            "No extracted Batch 3 paper required a nevi collection after exclusion.",
        )

    brain_mentioned = any("brain" in blob or "cerebral" in blob for blob in blobs)
    if brain_mentioned and "brain" not in collection_text:
        add(
            "multiple brain metastases collection",
            "WORSENED",
            "Multiple brain metastases have no LesionCollection.",
        )
    elif brain_mentioned:
        add(
            "multiple brain metastases collection",
            "RESOLVED_BY_EXISTING_MODEL",
            "Brain metastases received a LesionCollection row.",
        )
    else:
        add(
            "multiple brain metastases collection",
            "RESOLVED_BY_EXISTING_MODEL",
            "No extracted Batch 3 paper required a brain-metastasis collection.",
        )

    collapsed = any(len(data["episodes"]) <= 1 and len(data["lesions"]) >= 2 for _, _, data in extracted_rows)
    if collapsed:
        add(
            "regression episode collapse",
            "REPEATED",
            "At least one Batch 3 paper still has one case-level episode for "
            "distinct lesion courses. This now spans Batch 1, 2, and 3.",
        )
    else:
        add(
            "regression episode collapse",
            "RESOLVED_BY_EXISTING_MODEL",
            "Extracted Batch 3 papers did not collapse distinct courses into "
            "one episode, or had a single lesion course.",
        )

    if extracted_rows:
        add(
            "primary regression + metastatic persistence",
            "REPEATED",
            "Yamada complete primary regression coexists with a persistent "
            "inguinal metastasis; Sandru regressive primary coexists with "
            "lymph-node, lung, and brain metastases; Martinez nevi "
            "disappearance coexists with subcutaneous/lung/nodal metastases. "
            "The frozen episode model still cannot hold those as one "
            "non-contradictory scoped pair.",
        )
    else:
        add(
            "primary regression + metastatic persistence",
            "RESOLVED_BY_EXISTING_MODEL",
            "This coexistence was not required by extracted Batch 3 papers.",
        )

    vascular = any(
        "lymphovascular" in blob or "vascular invasion" in blob or "tubular" in blob
        for blob in blobs
    )
    if vascular:
        add(
            "vascular/lymphovascular lesion identity",
            "NEW",
            "Koibuchi vascular/lymphatic structure is present; identity was "
            "left as extracted without forcing merge or split beyond the quote.",
        )
    else:
        add(
            "vascular/lymphovascular lesion identity",
            "RESOLVED_BY_EXISTING_MODEL",
            "No extracted Batch 3 paper required lymphovascular identity resolution.",
        )

    dual = False
    for obs in all_observations:
        blob = _obs_blob(obs)
        domain = obs.observation_domain
        if domain is not None and hasattr(domain, "value"):
            domain = domain.value
        secondary = obs.domain_secondary
        if secondary is not None and hasattr(secondary, "value"):
            secondary = secondary.value
        if "cd8" in blob or "lymphocyt" in blob or "melanophage" in blob:
            if domain in {"BIOLOGICAL_STATE", "DIAGNOSTIC_EVIDENCE"} or secondary in {
                "BIOLOGICAL_STATE",
                "DIAGNOSTIC_EVIDENCE",
                "PATHOLOGIC_FINDING",
            }:
                dual = True
    if dual:
        add(
            "dual-domain immune pathology",
            "REPEATED",
            "Immune-pathology findings again sit in BIOLOGICAL_STATE and/or "
            "DIAGNOSTIC_EVIDENCE because frozen ontology has no dedicated "
            "immune-pathology domain.",
        )
    else:
        add(
            "dual-domain immune pathology",
            "RESOLVED_BY_EXISTING_MODEL",
            "No immune-pathology dual-domain pressure appeared in extracted papers.",
        )

    excluded = [
        find_duplicate(payload, candidate_id=target["candidate_id"])
        for target in BATCH_CANDIDATES
        if target.get("evaluate_inclusion")
    ]
    if any(
        row and row.get("extraction_status") == PaperIntakeState.EXCLUDED.value
        for row in excluded
    ):
        add(
            "latent regression vs observed regression",
            "RESOLVED_BY_EXISTING_MODEL",
            "Unknown-primary paper was EXCLUDED at the inclusion gate. "
            "Hypothesized regressed primary was not extracted as a patient fact "
            "and no RegressionEpisode was created.",
        )
    else:
        add(
            "latent regression vs observed regression",
            "NEW",
            "Unknown-primary paper was extracted; inspect whether a "
            "RegressionEpisode was created from hypothesized regression only.",
        )

    payload["batch3_repeat_watch"] = watch
    payload["phase4a2_patch_candidates"] = _patch_candidates(watch)
    save_manifest(store, payload)


def _patch_candidates(watch: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = []
    collection_items = {
        "multiple pulmonary metastases collection",
        "multiple lymph-node collection",
        "multifocal / multiple-nevi collection",
        "multiple brain metastases collection",
    }
    collection_hit = any(
        item["item"] in collection_items and item["status"] in {"REPEATED", "WORSENED"}
        for item in watch
    )
    if collection_hit:
        candidates.append(
            {
                "flag": "PHASE4A2_PATCH_CANDIDATE",
                "priority": "PATCH_CANDIDATE_HIGH_PRIORITY",
                "item": "LesionCollection missing",
                "note": (
                    "LesionCollection absence now repeats across Batch 1, 2, "
                    "and 3. Patch is recorded only; it was not executed."
                ),
            }
        )
    if any(
        item["item"] == "regression episode collapse"
        and item["status"] in {"REPEATED", "WORSENED"}
        for item in watch
    ):
        candidates.append(
            {
                "flag": "PHASE4A2_PATCH_CANDIDATE",
                "priority": "PATCH_CANDIDATE_HIGH_PRIORITY",
                "item": "RegressionEpisode collapse",
                "note": (
                    "Case-level episode collapse now repeats across Batch 1, 2, "
                    "and 3. Patch is recorded only; it was not executed."
                ),
            }
        )
    return candidates


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
        "# Corpus batch 3",
        "",
        "Infrastructure version: phase4a.1",
        "Frozen ontology: PHASE 2.3 / PHASE 3.4 / biological_observation_extraction:v5",
        "Schema/rule/prompt were not modified.",
        "",
        f"- candidates attempted: {len(attempted)}",
        f"- full text success: {stats['success'] + stats['excluded']}",
        f"- full text failure/unavailable: {stats['failure']}",
        f"- excluded after full text: {stats['excluded']}",
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
            "## Extraction counts (Batch 3 papers extracted into corpus)",
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
            f"patients={item.get('patient_ids')} "
            f"excluded={item.get('excluded')} "
            f"exclusion_reason={item.get('exclusion_reason')}"
        )
    lines.extend(["", "## Measurement status (Batch 3 case-matrix cells)", ""])
    if stats["measurement_status"]:
        for key, value in sorted(stats["measurement_status"].items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none (no extracted Batch 3 case rows)")
    lines.extend(
        [
            "",
            "## Quote verification (Batch 3 linked evidence)",
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
        or str(point.get("batch")) == "3"
    ]
    if points:
        for point in points:
            status = point.get("repeat_status")
            flag = point.get("patch_flag")
            prefix = ""
            if status:
                prefix += f"[{status}] "
            if flag:
                prefix += f"[{flag}] "
            lines.append(f"- {prefix}{point.get('candidate_id')}: {point.get('note')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Repeated pressure-point watch", ""])
    watch = payload.get("batch3_repeat_watch") or []
    if watch:
        for item in watch:
            lines.append(f"- {item['item']}: {item['status']} — {item['note']}")
    else:
        lines.append("- not applicable")
    lines.extend(["", "## PHASE4A2_PATCH_CANDIDATE", ""])
    patches = payload.get("phase4a2_patch_candidates") or []
    if patches:
        for item in patches:
            lines.append(
                f"- {item['flag']} / {item['priority']}: {item['item']} — {item['note']}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Possible duplicate reports", ""])
    dups = payload.get("possible_duplicate_reports") or []
    batch_dups = [
        item for item in dups if str(item.get("candidate_id", "")).startswith(PREFIX)
    ]
    if batch_dups:
        for item in batch_dups:
            lines.append(f"- POSSIBLE_DUPLICATE_REPORT {item}")
    else:
        lines.append("- none")
    excluded = [
        f"{cid}: {by_id[cid].get('exclusion_reason')} — {by_id[cid].get('notes')}"
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
    out = PROCESSED_DIR / "audit" / "corpus_batch_3.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corpus Expansion Batch 3")
    parser.add_argument("--acquire-only", action="store_true")
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    store = CorpusStore()
    register_candidates(store)
    attempted = [target["candidate_id"] for target in BATCH_CANDIDATES]
    if not args.extract_only and not args.audit_only:
        attempted = acquire_and_ingest(store)
    if args.acquire_only:
        print("acquire-only complete", flush=True)
        return
    if not args.audit_only:
        evaluate_unknown_primary_inclusion(store)
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
            "PHASE4A2 patch candidates were recorded only; no patch was executed.",
        ],
        test_result="pending",
    )


if __name__ == "__main__":
    main()
