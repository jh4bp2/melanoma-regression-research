from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pymupdf
from sqlalchemy import select

from app.corpus.inclusion_gate import (
    INCLUDED_SPONTANEOUS_REGRESSION,
    LATENT_REGRESSION_DISCOVERY_SOURCE,
    TREATMENT_ASSOCIATED_REFERENCE,
    classify_inclusion,
    compact_text,
)
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
from app.corpus.polarity import PolarityDecision, check_claim_against_quote
from app.corpus.reconciliation import reconcile_paper
from app.corpus.runs import latest_reconciliation_runs, seed_cases_and_runs
from app.corpus.states import ExclusionReason, PaperIntakeState, QualityStatus
from app.corpus.store import CorpusStore
from app.corpus.versions import CORPUS_INFRA_VERSION, CORPUS_RULE_VERSION, frozen_ontology
from app.core.config import PROJECT_ROOT, get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.llm.base import StructuredExtractionError
from app.llm.provider import create_provider
from app.models import (
    BiologicalObservation,
    Case,
    Evidence,
    Event,
    EvidenceType,
    FieldEvidenceLink,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    LesionCollection,
    Paper,
    QuoteVerificationStatus,
    RegressionEpisode,
    RegressionEpisodeType,
)
from app.services.biological_observation_pipeline import BiologicalObservationPipeline
from app.services.extraction_pipeline import ExtractionPipeline
from app.services.paper_parser import PdfTextExtractionError, parse_pdf


PAPERS_DIR = PROJECT_ROOT / "data" / "papers"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PAPERS_MANIFEST = PAPERS_DIR / "manifest.json"
PREFIX = "batch6-"
AUDIT_PATH = PROCESSED_DIR / "audit" / "corpus_batch_6.md"

BATCH_CANDIDATES = [
    {
        "candidate_id": "batch6-pique-2011",
        "title": "Complete regression of melanoma associated with vitiligo",
        "doi": "10.5070/D37SN7H2J7",
        "pmid": "21272495",
        "pmcid": None,
        "year": 2011,
        "journal": "Dermatology Online Journal",
        "filename": "pique_2011_doj.pdf",
        "selection_reason": (
            "Complete primary regression with vitiligo, melanophages, fibroplasia, "
            "telangiectasia, later inguinal nodal metastasis"
        ),
        "source_urls": [
            "https://escholarship.org/content/qt7sn7h2j7/qt7sn7h2j7.pdf",
            "https://escholarship.org/uc/item/7sn7h2j7.pdf",
            "https://dermatology.cdlib.org/1701/4_case_presentations/4_11-00092/pique.html",
        ],
        "access_note": "UC eScholarship / Dermatology Online Journal OA PDF",
        "forced_inclusion": INCLUDED_SPONTANEOUS_REGRESSION,
        "query_slot": "vitiligo_complete_primary",
        "site_subtype": "CUTANEOUS",
        "identifier_notes": (
            "Europe PMC stores DOI as 10.5070/d37sn7h2j7 (lowercase). "
            "Author given as MaSol Martínez-Martín; user suggestion María Sol Martínez-Martín."
        ),
    },
    {
        "candidate_id": "batch6-patel-2022",
        "title": (
            "Partial spontaneous regression of choroidal melanoma: "
            "A case image with histopathology and gene expression profiling"
        ),
        "doi": "10.1016/j.ajoc.2022.101517",
        "pmid": "35496766",
        "pmcid": "PMC9048143",
        "year": 2022,
        "journal": "American Journal of Ophthalmology Case Reports",
        "filename": "patel_2022_pmc9048143.pdf",
        "selection_reason": (
            "Partial spontaneous choroidal melanoma regression with serial ultrasound "
            "and gene-expression profiling; non-cutaneous boundary stress-test"
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC9048143.1/PMC9048143.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9048143/pdf/main.pdf",
            "https://europepmc.org/articles/PMC9048143?pdf=render",
        ],
        "access_note": "PMC / Europe PMC OA PDF",
        "forced_inclusion": INCLUDED_SPONTANEOUS_REGRESSION,
        "query_slot": "partial_choroidal",
        "site_subtype": "UVEAL_CHOROIDAL",
        "identifier_notes": "Identifiers match the user suggestion.",
    },
    {
        "candidate_id": "batch6-goncharov-2025",
        "title": (
            "Spontaneous regression of metastases in malignant melanoma: "
            "a case report"
        ),
        "doi": "10.20333/25000136-2025-3-102-105",
        "pmid": None,
        "pmcid": None,
        "year": 2025,
        "journal": "Siberian Medical Review",
        "filename": "goncharov_2025_smr.pdf",
        "selection_reason": (
            "Long metastatic remission without anti-tumor therapy; "
            "fucoidan/diet exposures must stay non-causal"
        ),
        "source_urls": [
            "https://journals.rcsi.science/1819-9496/article/download/413125/680297",
        ],
        "access_note": "Siberian Medical Review publisher OA PDF",
        "forced_inclusion": INCLUDED_SPONTANEOUS_REGRESSION,
        "query_slot": "long_remission_no_systemic_treatment",
        "site_subtype": "CUTANEOUS",
        "identifier_notes": (
            "No PMID/PMCID in Europe PMC at validation. Publisher DOI confirmed."
        ),
    },
    {
        "candidate_id": "batch6-emanuel-2008",
        "title": "Complete regression of primary malignant melanoma",
        "doi": "10.1097/DAD.0b013e318165641a",
        "pmid": "18360126",
        "pmcid": None,
        "year": 2008,
        "journal": "The American Journal of Dermatopathology",
        "filename": "emanuel_2008_ajd.pdf",
        "selection_reason": (
            "Two-case complete primary regression series with detailed histopathology"
        ),
        "source_urls": [
            "https://journals.lww.com/amjdermatopathology/Abstract/2008/04000/Complete_Regression_of_Primary_Malignant_Melanoma.17.aspx",
        ],
        "access_note": (
            "LWW closed access. ResearchGate not used. "
            "No institutional/author-manuscript PDF located."
        ),
        "forced_inclusion": INCLUDED_SPONTANEOUS_REGRESSION,
        "query_slot": "two_case_complete_primary",
        "site_subtype": "CUTANEOUS",
        "identifier_notes": (
            "Europe PMC stores DOI as 10.1097/dad.0b013e318165641a (lowercase)."
        ),
    },
    {
        "candidate_id": "batch6-lallas-2012",
        "title": (
            "Extensive regression in pigmented skin lesions: "
            "a dangerous confounding feature"
        ),
        "doi": "10.5826/dpc.0202a08",
        "pmid": "23785596",
        "pmcid": "PMC3663342",
        "year": 2012,
        "journal": "Dermatology Practical & Conceptual",
        "filename": "lallas_2012_pmc3663342.pdf",
        "selection_reason": (
            "Discovery slot: unused human fully-regressed cutaneous melanoma "
            "with ipsilateral axillary metastasis, fibrosis/melanophages, legal PMC PDF. "
            "Nevus and LPLK comparators are not Cases."
        ),
        "source_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC3663342.1/PMC3663342.1.pdf",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3663342/pdf/",
            "https://europepmc.org/articles/PMC3663342?pdf=render",
        ],
        "access_note": "PMC / Europe PMC OA PDF",
        "forced_inclusion": INCLUDED_SPONTANEOUS_REGRESSION,
        "query_slot": "discovery_no_obvious_trigger",
        "site_subtype": "CUTANEOUS",
        "identifier_notes": (
            "Neutral query over OA case-report journals; not in the exclusion author list."
        ),
    },
]

_IMMUNE_PATH_RE = re.compile(
    r"infiltrat|melanophage|necrosis|fibrosis|histiocyt|lymphocyt|"
    r"cd3|cd8|t-cell|t cell",
    re.I,
)
_CAUSAL_TOKENS = ("caused", "due to", "because", "triggered by", "secondary to")

PATCH_WATCH_ITEMS = (
    "lesion_collection_missing",
    "episode_over_splitting",
    "episode_collapse",
    "fact_inversion",
    "negation_scope",
    "phantom_lesion",
    "treatment_associated_contamination",
    "cross_case_contamination",
)


def _access_source(url: str, pmcid: str | None) -> str:
    if "pmc-oa-opendata.s3.amazonaws.com" in url:
        return f"NIH NLM NCBI PMC Article Datasets on AWS ({pmcid}.1)"
    if "ncbi.nlm.nih.gov/pmc" in url or "pmc.ncbi.nlm.nih.gov" in url:
        return f"NCBI PMC OA PDF ({pmcid})"
    if "europepmc.org" in url:
        return f"Europe PMC full-text PDF ({pmcid})"
    if "scielo.br" in url:
        return "SciELO Anais Brasileiros de Dermatologia publisher OA PDF"
    if "spandidos-publications.com" in url:
        return "Spandidos Oncology Letters publisher OA PDF"
    if "cureus.com" in url:
        return "Cureus publisher open-access PDF"
    if "biomedres.us" in url or "biomedres.info" in url:
        return "BJSTR publisher open-access PDF"
    if "openresearch.surrey.ac.uk" in url:
        return "University of Surrey institutional repository PDF"
    if "sagepub.com" in url:
        return "Sage publisher PDF"
    if "jle.com" in url:
        return "John Libbey Eurotext publisher PDF"
    if "escholarship.org" in url or "cdlib.org" in url:
        return "UC eScholarship / Dermatology Online Journal OA PDF"
    if "journals.rcsi.science" in url or "smr.krasgmu" in url:
        return "Siberian Medical Review publisher OA PDF"
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
        "notes": "Corpus Expansion Batch 6 candidate.",
        "role": "batch_6",
        "batch": 6,
        "site_subtype": target.get("site_subtype"),
        "identifier_notes": target.get("identifier_notes"),
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
        if (
            (target["pmid"] and ids.get("pmid") == target["pmid"])
            or (target["pmcid"] and ids.get("pmcid") == target["pmcid"])
            or (target["doi"] and ids.get("doi") == target["doi"])
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
                f"=== acquire {target['candidate_id']} {target['pmcid']} ===",
                flush=True,
            )
            try:
                source_url = _download(target["source_urls"], dest)
                sha256, size, pages = _verify_pdf(dest)
                parse_pdf(dest)
            except Exception as exc:
                print(f"FULLTEXT_UNAVAILABLE {target['candidate_id']}: {exc}", flush=True)
                pipeline.mark_fulltext_unavailable(
                    target["candidate_id"], note=target["access_note"]
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
                            if target["pmid"]
                            else (
                                f"https://doi.org/{target['doi']}"
                                if target["doi"]
                                else None
                            )
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


def _paper_text(filename: str) -> str:
    pdf_path = PAPERS_DIR / filename
    if pdf_path.exists():
        parsed = parse_pdf(pdf_path)
        return "\n".join(parsed.pages)
    return ""


def apply_inclusion_gate(store: CorpusStore) -> None:
    payload = load_manifest(store)
    papers_payload = json.loads(PAPERS_MANIFEST.read_text(encoding="utf-8"))
    for target in BATCH_CANDIDATES:
        row = find_duplicate(payload, candidate_id=target["candidate_id"])
        if row is None or row.get("paper_id") is None:
            continue
        text = _paper_text(target["filename"])
        decision = classify_inclusion(
            candidate_id=target["candidate_id"],
            text=text,
            forced=target.get("forced_inclusion"),
        )
        row["inclusion_class"] = decision.intake_class
        row["research_class"] = decision.research_class
        row["discovery_track"] = decision.discovery_track
        target["skip_extract"] = not decision.extract
        if decision.extract:
            row["notes"] = decision.note
            save_manifest(store, payload)
            print(
                f"{target['candidate_id']}: {decision.intake_class} / "
                f"{decision.research_class}",
                flush=True,
            )
            continue
        reason = ExclusionReason(decision.exclusion_reason or ExclusionReason.OTHER.value)
        if row["extraction_status"] != PaperIntakeState.EXCLUDED.value:
            transition_paper(row, "extraction_status", PaperIntakeState.EXCLUDED)
        row["exclusion_reason"] = reason.value
        row["notes"] = decision.note
        row["quality_status"] = QualityStatus.REVIEW.value
        row["research_use"] = decision.intake_class
        save_manifest(store, payload)
        for item in papers_payload["papers"]:
            ids = item.get("candidate_identifiers") or {}
            if (target["pmid"] and ids.get("pmid") == target["pmid"]) or (
                target["doi"] and ids.get("doi") == target["doi"]
            ):
                item["status"] = "EXCLUDED"
                item["exclusion_reason"] = reason.value
                item["discovery_track"] = decision.discovery_track
                item["inclusion_class"] = decision.intake_class
                break
        print(
            f"{target['candidate_id']}: {decision.intake_class} / "
            f"{decision.research_class} — {decision.note}",
            flush=True,
        )
    PAPERS_MANIFEST.write_text(
        json.dumps(papers_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    save_manifest(store, payload)


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
                    f"skip extract {target['candidate_id']}: inclusion-gate",
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
                    print(f"PHASE 2 retry {attempt}/3 paper={paper_id}: {exc}", flush=True)
            if case_run is None:
                raise last_error or RuntimeError("PHASE 2 extraction failed")
            cases = list(
                session.scalars(
                    select(Case)
                    .where(Case.paper_id == paper_id, Case.extraction_run_id == case_run.id)
                    .order_by(Case.id)
                )
            )
            print(
                f"paper={paper_id} case_run={case_run.id} "
                f"status={case_run.status.value} cases={[case.id for case in cases]}",
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
                    f"episodes={metrics.get('regression_episodes', 0)}",
                    flush=True,
                )
            _advance(row, "extraction_status", PaperIntakeState.EXTRACTED)
            save_manifest(store, payload)


def reconcile_extracted(store: CorpusStore) -> list[dict[str, Any]]:
    results = []
    payload = load_manifest(store)
    with SessionLocal() as session:
        for target in BATCH_CANDIDATES:
            row = find_duplicate(payload, candidate_id=target["candidate_id"])
            if row is None or not row.get("paper_id"):
                continue
            if row.get("extraction_status") not in {
                PaperIntakeState.EXTRACTED.value,
                PaperIntakeState.AUDITED.value,
            }:
                continue
            print(f"=== reconcile {target['candidate_id']} paper={row['paper_id']} ===", flush=True)
            result = reconcile_paper(session, row["paper_id"])
            results.append(result)
            print(result, flush=True)
    return results


def _obs_blob(obs: BiologicalObservation) -> str:
    return " ".join(
        part
        for part in (obs.variable_name, obs.value, obs.lesion_identifier)
        if part
    ).casefold()


def _load_extracted(session, paper_id: int) -> dict[str, Any]:
    cases, phase2, phase3 = seed_cases_and_runs(session, paper_id)
    phase3_ids = [run.id for run in phase3]
    recon = latest_reconciliation_runs(session, paper_id)
    recon_ids = [run.id for run in recon]
    case_ids = [case.id for case in cases]
    _cases, lesions, hist_episodes, _states = load_seed_entities(
        session, case_ids, phase3_ids
    )
    episodes = hist_episodes
    if recon_ids:
        _c, _l, recon_episodes, _s = load_seed_entities(session, case_ids, recon_ids)
        episodes = recon_episodes or hist_episodes
    collections = list(
        session.scalars(
            select(LesionCollection).where(
                LesionCollection.case_id.in_(case_ids or [-1]),
                LesionCollection.created_from_run_id.in_((recon_ids or phase3_ids) or [-1]),
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
    recon_obs = list(
        session.scalars(
            select(BiologicalObservation).where(
                BiologicalObservation.case_id.in_(case_ids or [-1]),
                BiologicalObservation.created_from_run_id.in_(recon_ids or [-1]),
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
    genotypes = list(
        session.scalars(
            select(GenotypeObservation).where(
                GenotypeObservation.case_id.in_(case_ids or [-1]),
                GenotypeObservation.created_from_run_id.in_(phase3_ids or [-1]),
            )
        )
    )
    iraes = list(
        session.scalars(
            select(ImmuneRelatedAdverseEvent).where(
                ImmuneRelatedAdverseEvent.case_id.in_(case_ids or [-1]),
                ImmuneRelatedAdverseEvent.created_from_run_id.in_(
                    (phase3_ids + recon_ids) or [-1]
                ),
            )
        )
    )
    return {
        "cases": cases,
        "phase2": phase2,
        "phase3": phase3,
        "lesions": lesions,
        "episodes": episodes,
        "historical_episodes": hist_episodes,
        "collections": collections,
        "observations": observations,
        "recon_observations": recon_obs,
        "events": events,
        "genotypes": genotypes,
        "iraes": iraes,
        "recon_ids": recon_ids,
    }


def collect_batch_stats(session, store: CorpusStore) -> dict[str, Any]:
    payload = load_manifest(store)
    batch_rows = [
        row
        for row in payload["papers"]
        if str(row.get("candidate_id", "")).startswith(PREFIX)
    ]
    quote_counts: Counter[str] = Counter()
    case_ids: list[int] = []
    per_paper: list[dict[str, Any]] = []
    observation_count = 0
    treatment_events = 0
    inversions = 0
    genotypes = 0
    iraes = 0
    immune_pathology = 0
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
                    "inclusion_class": row.get("inclusion_class"),
                    "research_class": row.get("research_class"),
                }
            )
            continue
        extracted = _load_extracted(session, paper_id)
        case_ids.extend(case.id for case in extracted["cases"])
        observation_count += len(extracted["observations"])
        genotypes += len(extracted["genotypes"])
        iraes += len(extracted["iraes"])
        immune_pathology += sum(
            1
            for obs in extracted["observations"]
            if _IMMUNE_PATH_RE.search(_obs_blob(obs))
        )
        treatment_events += sum(
            1
            for event in extracted["events"]
            if (event.event_type.value if event.event_type else "")
            in {"treatment", "drug_exposure"}
        )
        phase3_ids = [run.id for run in extracted["phase3"]]
        links = list(
            session.scalars(
                select(FieldEvidenceLink).where(
                    FieldEvidenceLink.extraction_run_id.in_(
                        [*(phase3_ids), *([extracted["phase2"].id] if extracted["phase2"] else [])]
                        or [-1]
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
        quotes = {item.id: item for item in evidence}
        obs_quote: dict[int, str] = {}
        for link in links:
            item = quotes.get(link.evidence_id)
            if item is None:
                continue
            quote_counts[item.verification_status or "UNKNOWN"] += 1
            text = item.raw_source_quote or item.normalized_source_quote or ""
            if link.entity_type == "biological_observation":
                obs_quote.setdefault(link.entity_id, text)
        for obs in extracted["observations"]:
            result = check_claim_against_quote(
                obs_quote.get(obs.id),
                " ".join(part for part in (obs.variable_name, obs.value) if part),
                subject=obs.variable_name,
            )
            if result.decision == PolarityDecision.FACT_INVERSION:
                inversions += 1
        per_paper.append(
            {
                "candidate_id": row["candidate_id"],
                "paper_id": paper_id,
                "fulltext": row["fulltext_status"],
                "cases": len(extracted["cases"]),
                "lesions": len(extracted["lesions"]),
                "collections": len(extracted["collections"]),
                "episodes": len(extracted["episodes"]),
                "historical_episodes": len(extracted["historical_episodes"]),
                "observations": len(extracted["observations"]),
                "patient_ids": [case.patient_identifier for case in extracted["cases"]],
                "excluded": False,
                "inclusion_class": row.get("inclusion_class"),
                "research_class": row.get("research_class"),
                "treatment_events": sum(
                    1
                    for event in extracted["events"]
                    if (event.event_type.value if event.event_type else "")
                    in {"treatment", "drug_exposure"}
                ),
                "genotypes": len(extracted["genotypes"]),
                "iraes": len(extracted["iraes"]),
                "immune_pathology": sum(
                    1
                    for obs in extracted["observations"]
                    if _IMMUNE_PATH_RE.search(_obs_blob(obs))
                ),
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
        "treatment_events": treatment_events,
        "genotypes": genotypes,
        "iraes": iraes,
        "immune_pathology": immune_pathology,
        "fact_inversions": inversions,
        "success": sum(1 for item in per_paper if item["paper_id"] and not item.get("excluded")),
        "fulltext_ok": sum(1 for item in per_paper if item["paper_id"]),
        "failure": sum(1 for item in per_paper if item["paper_id"] is None),
        "excluded": sum(1 for item in per_paper if item.get("excluded")),
    }


def _is_causal_observed_fact(obs: BiologicalObservation, *terms: str) -> bool:
    blob = _obs_blob(obs)
    if obs.evidence_type != EvidenceType.OBSERVED_FACT.value:
        return False
    if not any(term in blob for term in terms):
        return False
    return any(token in blob for token in _CAUSAL_TOKENS)


def record_batch_pressure_points(store: CorpusStore, session) -> dict[str, Any]:
    payload = load_manifest(store)
    payload["pressure_points"] = [
        point
        for point in payload.get("pressure_points") or []
        if not str(point.get("candidate_id", "")).startswith(PREFIX)
        and str(point.get("batch")) != "6"
    ]
    existing = {
        (point.get("candidate_id"), point.get("note"))
        for point in payload.get("pressure_points") or []
    }
    watch = {item: "PASS" for item in PATCH_WATCH_ITEMS}
    notes: list[str] = []

    def add(candidate_id: str, note: str) -> None:
        if (candidate_id, note) in existing:
            return
        record_pressure_point(payload, candidate_id=candidate_id, note=note)
        payload["pressure_points"][-1]["batch"] = 6
        existing.add((candidate_id, note))
        notes.append(f"{candidate_id}: {note}")

    def fail(item: str, *, repeated: bool = False) -> None:
        watch[item] = "REPEATED_FAILURE" if repeated else "NEW_FAILURE"

    for target in BATCH_CANDIDATES:
        row = find_duplicate(payload, candidate_id=target["candidate_id"])
        if row is None:
            continue
        text = _paper_text(target["filename"])
        compact = compact_text(text)
        if "biopsy" in compact and ("trigger" in compact or "caused" in compact):
            add(
                target["candidate_id"],
                "Author mentions biopsy as a possible trigger; must remain "
                "AUTHOR_INTERPRETATION, not OBSERVED_FACT causation.",
            )
        if any(term in compact for term in ("fever", "infection", "erysipelas")) and (
            "trigger" in compact or "caused" in compact
        ):
            add(
                target["candidate_id"],
                "Author mentions fever/infection as a possible trigger; must "
                "remain AUTHOR_INTERPRETATION, not OBSERVED_FACT causation.",
            )
        if row.get("extraction_status") == PaperIntakeState.EXCLUDED.value:
            continue
        if not row.get("paper_id"):
            continue
        extracted = _load_extracted(session, row["paper_id"])
        multiple_mets = bool(
            re.search(
                r"\b(?:multiple|several|four|seven)\b.{0,40}\b(?:metastas|lesion|nodule)",
                compact,
            )
        )
        if multiple_mets and not extracted["collections"]:
            fail("lesion_collection_missing")
            add(
                target["candidate_id"],
                "Multiple metastases are described but no LesionCollection was recovered.",
            )
        for obs in extracted["observations"]:
            ident = (obs.lesion_identifier or "").casefold().strip()
            if not ident:
                continue
            tokens = [token for token in ident.replace("-", " ").split() if len(token) > 3]
            if tokens and not any(token in compact for token in tokens):
                fail("phantom_lesion")
                add(
                    target["candidate_id"],
                    f"Observation lesion_identifier {obs.lesion_identifier!r} "
                    "has no supporting tokens in the paper text.",
                )
                break
        if (
            "partial" in compact
            and "complete" in compact
            and len(extracted["episodes"]) > 1
            and "recurr" not in compact
        ):
            fail("episode_over_splitting", repeated=True)
            add(
                target["candidate_id"],
                "Partial-to-complete wording of one course remains more than "
                "one canonical episode.",
            )
        if "recurr" in compact and len(extracted["historical_episodes"]) > 1:
            if len(extracted["episodes"]) == 1:
                fail("episode_collapse")
                add(
                    target["candidate_id"],
                    "Recurrence after regression may have been collapsed into "
                    "one canonical episode.",
                )
        causal_biopsy = any(
            _is_causal_observed_fact(obs, "biopsy")
            for obs in extracted["observations"]
        )
        causal_infection = any(
            _is_causal_observed_fact(obs, "fever", "infection", "erysipelas")
            for obs in extracted["observations"]
        )
        if causal_biopsy or causal_infection:
            fail("negation_scope")
            add(
                target["candidate_id"],
                "Biopsy/fever/infection was stored as a causal OBSERVED_FACT.",
            )
        for episode in extracted["episodes"]:
            if episode.episode_type != RegressionEpisodeType.SPONTANEOUS:
                continue
            desc = (episode.description or "").casefold()
            if any(
                token in desc
                for token in (
                    "pembrolizumab",
                    "ipilimumab",
                    "nivolumab",
                    "vemurafenib",
                    "dabrafenib",
                )
            ):
                fail("treatment_associated_contamination")
                add(
                    target["candidate_id"],
                    "Treatment-associated wording entered a spontaneous episode.",
                )
        if any(
            obs.evidence_type == EvidenceType.OBSERVED_FACT.value
            and any(
                token in _obs_blob(obs)
                for token in ("immune activation", "triggered by biopsy")
            )
            for obs in extracted["observations"]
        ):
            add(
                target["candidate_id"],
                "Hypothesis wording was stored as OBSERVED_FACT.",
            )
        causal_exposure = any(
            _is_causal_observed_fact(
                obs, "fucoidan", "green tea", "antioxidant", "pineapple", "diet"
            )
            for obs in extracted["observations"]
        )
        causal_vitiligo = any(
            _is_causal_observed_fact(obs, "vitiligo", "leukoderma")
            for obs in extracted["observations"]
        )
        if causal_exposure or causal_vitiligo:
            fail("negation_scope")
            add(
                target["candidate_id"],
                "Exposure or vitiligo phenotype was stored as a causal OBSERVED_FACT.",
            )
        if target["candidate_id"] == "batch6-lallas-2012":
            if len(extracted["cases"]) > 1:
                fail("cross_case_contamination")
                add(
                    target["candidate_id"],
                    "Nevus/LPLK comparators were stored as additional Cases.",
                )
        if target["candidate_id"] == "batch6-patel-2022":
            add(
                target["candidate_id"],
                "ONTOLOGY_PRESSURE_POINT: MELANOMA_SITE_SUBTYPE. "
                "Choroidal/uveal melanoma must not share a cutaneous denominator "
                "in PHASE 4B. Frozen schema has organ/location fields but no "
                "CUTANEOUS/UVEAL_CHOROIDAL/MUCOSAL/ACRAL/UNKNOWN enum.",
            )
            if len(extracted["episodes"]) != 1:
                fail("episode_over_splitting")
                add(
                    target["candidate_id"],
                    "Partial choroidal course should remain one canonical episode.",
                )
        add(
            target["candidate_id"],
            f"Research site/subtype metadata: {target.get('site_subtype')}.",
        )
    payload["batch6_patch_regression"] = {"watch": watch, "notes": notes}
    save_manifest(store, payload)
    return {"watch": watch, "notes": notes}


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
    recon_results: list[dict[str, Any]],
    patch: dict[str, Any],
    extra_notes: list[str],
    test_result: str,
) -> Path:
    payload = load_manifest(store)
    by_id = {row["candidate_id"]: row for row in payload["papers"]}
    frozen = frozen_ontology()
    watch = dict(patch.get("watch") or {item: "PASS" for item in PATCH_WATCH_ITEMS})
    if stats.get("fact_inversions"):
        watch["fact_inversion"] = "NEW_FAILURE"
    lines = [
        "# Corpus batch 6",
        "",
        f"- corpus infra: {CORPUS_INFRA_VERSION}",
        f"- rule: {CORPUS_RULE_VERSION}",
        f"- PHASE 2: {frozen['phase2_schema']} / {frozen['phase2_rule']}",
        f"- PHASE 3: {frozen['phase3_schema']} / {frozen['phase3_rule']}",
        f"- prompt: {frozen['phase3_prompt']}",
        "- Schema/rule/prompt were not modified.",
        "- Historical extraction and reconciliation runs were preserved.",
        "",
        f"- candidates attempted: {len(attempted)}",
        f"- full text success: {stats['fulltext_ok']}",
        f"- full text failure/unavailable: {stats['failure']}",
        f"- excluded after full text: {stats['excluded']}",
        f"- extracted into corpus: {stats['success']}",
        "",
        "## Candidates and source verification",
        "",
    ]
    for target in BATCH_CANDIDATES:
        row = by_id.get(target["candidate_id"], {})
        lines.append(
            f"- `{target['candidate_id']}` title={target['title']} "
            f"doi={target['doi']} pmid={target['pmid']} pmcid={target['pmcid']} "
            f"year={target['year']} journal={target['journal']} "
            f"site_subtype={target.get('site_subtype')}"
        )
        lines.append(
            f"  fulltext={row.get('fulltext_status')} access={row.get('access_source')} "
            f"url={row.get('source_url')} sha256={row.get('sha256')} "
            f"pages={row.get('page_count')} bytes={row.get('bytes')}"
        )
        if target.get("identifier_notes"):
            lines.append(f"  identifier_notes={target['identifier_notes']}")
    lines.extend(["", "## Inclusion classification", ""])
    for item in stats["per_paper"]:
        row = by_id.get(item["candidate_id"], {})
        lines.append(
            f"- `{item['candidate_id']}` paper_id={item['paper_id']} "
            f"intake={row.get('inclusion_class')} research={row.get('research_class')} "
            f"discovery={row.get('discovery_track')} "
            f"excluded={item.get('excluded')} reason={item.get('exclusion_reason')}"
        )
    lines.extend(
        [
            "",
            "## Extraction counts (Batch 6 papers extracted into corpus)",
            "",
            f"- Case: {stats['cases']}",
            f"- lesion: {stats['lesions']}",
            f"- collection: {stats['collections']}",
            f"- regression episode (canonical): {stats['episodes']}",
            f"- observation: {stats['observations']}",
            f"- treatment-associated events: {stats['treatment_events']}",
            f"- genotype: {stats['genotypes']}",
            f"- irAE: {stats['iraes']}",
            f"- immune pathology observations: {stats['immune_pathology']}",
            f"- FACT_INVERSION: {stats['fact_inversions']}",
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
            f"patients={item.get('patient_ids')} excluded={item.get('excluded')}"
        )
    lines.extend(["", "## Measurement status (Batch 6 case-matrix cells)", ""])
    if stats["measurement_status"]:
        for key, value in sorted(stats["measurement_status"].items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none (no extracted Batch 6 case rows)")
    lines.extend(
        [
            "",
            "## Quote verification (Batch 6 linked evidence)",
            "",
            f"- VERIFIED_EXACT: {stats['quote_counts'].get(QuoteVerificationStatus.VERIFIED_EXACT.value, 0)}",
            f"- VERIFIED_NORMALIZED: {stats['quote_counts'].get(QuoteVerificationStatus.VERIFIED_NORMALIZED.value, 0)}",
            f"- UNVERIFIED: {stats['quote_counts'].get(QuoteVerificationStatus.UNVERIFIED.value, 0)}",
            "",
            "## PHASE 4A.2 reconciliation",
            "",
            f"- recon runs this batch: {len(recon_results)}",
        ]
    )
    for result in recon_results:
        lines.append(
            f"- paper {result.get('paper_id')}: collections={result.get('collections_created')} "
            f"episodes {result.get('episodes_before')}→{result.get('episodes_after')} "
            f"merged={result.get('merged_episodes')} inversions={result.get('fact_inversions')}"
        )
    lines.extend(
        [
            "",
            "## PHASE 4A.2 patch regression",
            "",
            f"- LesionCollection missing: {watch.get('lesion_collection_missing')}",
            f"- RegressionEpisode over-splitting: {watch.get('episode_over_splitting')}",
            f"- RegressionEpisode collapse: {watch.get('episode_collapse')}",
            f"- fact inversion: {watch.get('fact_inversion')}",
            f"- negation scope: {watch.get('negation_scope')}",
            f"- phantom lesion: {watch.get('phantom_lesion')}",
            f"- treatment-associated contamination: {watch.get('treatment_associated_contamination')}",
            f"- cross-case contamination: {watch.get('cross_case_contamination')}",
            "",
            "## Ontology pressure points",
            "",
        ]
    )
    points = [
        point
        for point in (payload.get("pressure_points") or [])
        if str(point.get("candidate_id", "")).startswith(PREFIX)
        or str(point.get("batch")) == "6"
    ]
    if points:
        for point in points:
            lines.append(f"- {point.get('candidate_id')}: {point.get('note')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Possible duplicate reports", ""])
    dups = [
        item
        for item in (payload.get("possible_duplicate_reports") or [])
        if str(item.get("candidate_id", "")).startswith(PREFIX)
    ]
    if dups:
        for item in dups:
            lines.append(f"- POSSIBLE_DUPLICATE_REPORT {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Excluded / discovery-source papers", ""])
    excluded = [
        f"{cid}: {by_id[cid].get('inclusion_class')} — {by_id[cid].get('notes')}"
        for cid in attempted
        if by_id.get(cid, {}).get("extraction_status") == PaperIntakeState.EXCLUDED.value
    ]
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
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return AUDIT_PATH


def corpus_inventory(store: CorpusStore) -> dict[str, int]:
    payload = load_manifest(store)
    papers = payload.get("papers") or []
    included = [
        row
        for row in papers
        if row.get("inclusion_class") == INCLUDED_SPONTANEOUS_REGRESSION
        or (
            row.get("paper_id")
            and row.get("extraction_status")
            in {
                PaperIntakeState.EXTRACTED.value,
                PaperIntakeState.AUDITED.value,
            }
            and row.get("inclusion_class")
            not in {
                TREATMENT_ASSOCIATED_REFERENCE,
                LATENT_REGRESSION_DISCOVERY_SOURCE,
            }
        )
    ]
    fulltext = [
        row
        for row in papers
        if row.get("fulltext_status") == PaperIntakeState.FULLTEXT_FOUND.value
        or row.get("paper_id")
    ]
    excluded = [
        row
        for row in papers
        if row.get("extraction_status") == PaperIntakeState.EXCLUDED.value
        or str(row.get("candidate_id", "")).startswith("unavailable-")
        or row.get("inclusion_class")
        in {TREATMENT_ASSOCIATED_REFERENCE, LATENT_REGRESSION_DISCOVERY_SOURCE}
    ]
    return {
        "total_candidate_papers": len(papers),
        "fulltext_papers": len(fulltext),
        "included_spontaneous_papers": len(included),
        "excluded_or_reference_papers": len(excluded),
        "total_included_cases": sum(int(row.get("case_count") or 0) for row in included),
        "lesions": sum(int(row.get("lesion_count") or 0) for row in included),
        "collections": 0,
        "canonical_regression_episodes": sum(
            int(row.get("episode_count") or 0) for row in included
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corpus Expansion Batch 6")
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
    recon_results: list[dict[str, Any]] = []
    if not args.extract_only and not args.audit_only:
        attempted = acquire_and_ingest(store)
    if args.acquire_only:
        print("acquire-only complete", flush=True)
        return
    if not args.audit_only:
        apply_inclusion_gate(store)
        extract_ingested(store)
        recon_results = reconcile_extracted(store)
    pipeline = CorpusPipeline(store)
    with SessionLocal() as session:
        summary = pipeline.rebuild_indexes_and_matrix(session)
        patch = record_batch_pressure_points(store, session)
        mark_audited(store)
        stats = collect_batch_stats(session, store)
    print(f"index rebuild: {summary}", flush=True)
    print(f"batch stats: {stats}", flush=True)
    write_audit(
        store,
        attempted,
        stats,
        recon_results,
        patch,
        extra_notes=[
            "Frozen PHASE 2.3 / 3.4 ontology and PHASE 4A.2 patch were not redesigned.",
            "Abstracts were not used as Evidence.",
            "Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.",
            "PHASE 4B was not started.",
            "Discovery paper is Lallas 2012 (PMC3663342), not a hypothesis-biased query.",
            "ICI/COVID blue-nevus melanoma (PMID 41030443) was rejected as treatment-associated.",
            "Vitiligo/fucoidan/diet remain phenotype or exposure, not cause.",
            "Review-section historical cases and Lallas nevus/LPLK comparators are not Cases.",
            f"Corpus inventory: {corpus_inventory(store)}",
        ],
        test_result="pending",
    )
    print(f"wrote {AUDIT_PATH}", flush=True)


if __name__ == "__main__":
    main()
