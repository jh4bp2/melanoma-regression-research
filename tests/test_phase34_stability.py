from pathlib import Path

from app.llm.fake import FakeLLMProvider
from app.models import (
    Event,
    EventType,
    ExplanatoryAlternative,
    GenotypeObservation,
    GenotypeOrigin,
    GenotypeState,
    ImmuneRelatedAdverseEvent,
    ObservationDomain,
)
from app.services.biological_observation_pipeline import BiologicalObservationPipeline
from app.services.golden_expectations import core_signatures_for_run, stability_score
from app.services.genotype_semantics import is_genotype_claim, parse_genotype
from app.services.irae_semantics import canonical_irae_groups
from app.services.recall_hardening import (
    classify_explanatory_alternative,
    scan_explanatory_alternatives,
    scan_genotype_text,
    scan_immune_pathology,
)
from app.services.regression_episodes import build_regression_episodes
from app.services.chunking import chunk_pages, read_page_text
from tests.test_phase3_biological_observations import _setup_case


MOREIRA_RECALL_TEXT = """=== PAGE 1 ===
Case Presentation
BRAFV600 status was found to be wild-type.
The nodule became ulcerated and chronically infected.
=== PAGE 2 ===
Case Presentation
Dual immunohistochemical staining of CD3 and CD8 with the melanoma marker SOX10 demonstrated brisk infiltration with CD3+ and CD8+ T cells in both surgically resected in transit metastases, suggesting a T cell mediated immune response against the tumor in both samples.
Discussion
It is intriguing to speculate that his exposure to ipilimumab almost 2 years prior to the onset of tumor regression also contributed to the tumor response.
"""

TITLE_ONLY_TEXT = """=== PAGE 1 ===
Title
BRAF mutant melanoma two years after ipilimumab
Abstract
Delayed responses after ipilimumab are rarely seen.
=== PAGE 2 ===
Case Presentation
A patient with metastatic melanoma was observed.
"""

OSWALT_RECALL_TEXT = """=== PAGE 1 ===
Case Presentation
BRAF mutation analysis was positive and detected a V600E mutation (p.Val600Glu;c.1799T>A).
The patient developed grade 3 hepatotoxicity after the first ipilimumab/nivolumab cycle.
She was admitted for polymyositis associated with an elevated aldolase.
Repeat notes again described polymyositis after checkpoint blockade.
Discussion again mentioned polymyositis while on anti-PD-1 therapy.
=== PAGE 2 ===
Conclusions
Whole-exome sequencing studies determined this patient to harbor a germline P369S/R408Q variant of the pyrin inflammasome, consistent with a previously reported genotype.
"""


def _empty_provider():
    return FakeLLMProvider([{"observations": [], "rejected_interpretations": []}])


def test_brafv600_glued_token_is_wild_type():
    parsed = parse_genotype("BRAFV600 status was found to be wild-type.")
    assert parsed is not None
    assert parsed.gene == "BRAF"
    assert parsed.state == GenotypeState.WILD_TYPE.value


def test_non_whitelist_gene_is_accepted():
    parsed = parse_genotype("Tumor sequencing showed an ALK fusion variant.")
    assert parsed is not None
    assert parsed.gene == "ALK"
    assert parsed.state == GenotypeState.VARIANT_PRESENT.value


def test_braf_mek_inhibitor_is_not_a_genotype_claim():
    assert not is_genotype_claim(
        "She was transitioned to BRAF/MEK inhibitor therapy in June."
    )


def test_unclear_gene_mention_is_not_clear_state():
    parsed = parse_genotype("The specimen was BRAF V600.")
    assert parsed is not None
    assert parsed.state == GenotypeState.UNKNOWN.value


def test_delayed_ipilimumab_is_an_alternative_not_observation():
    assert (
        classify_explanatory_alternative(
            "It is intriguing to speculate that ipilimumab two years prior contributed."
        )
        == "delayed_immunotherapy_effect"
    )


def test_literature_delayed_ipilimumab_is_ignored():
    assert (
        classify_explanatory_alternative(
            "Delayed tumor responses have been reported in melanoma patients treated with ipilimumab."
        )
        is None
    )


def test_immune_and_genotype_and_alternative_scans():
    pages = {
        1: "Case Presentation\nBRAFV600 status was found to be wild-type.",
        2: (
            "Case Presentation\nDual immunohistochemical staining of CD3 and CD8 demonstrated brisk "
            "infiltration with CD3+ and CD8+ T cells in both metastases."
        ),
        3: (
            "Discussion\nIt is intriguing to speculate that his exposure to ipilimumab almost "
            "2 years prior also contributed to the tumor response."
        ),
    }
    chunks = chunk_pages(1, pages)
    immune = scan_immune_pathology(pages, chunks)
    genotypes = scan_genotype_text(pages, chunks)
    alternatives = scan_explanatory_alternatives(pages, chunks)
    assert any("CD3" in hit.variable_name for hit in immune)
    assert any(hit.gene == "BRAF" and hit.state == "WILD_TYPE" for hit in genotypes)
    assert any(
        hit.alternative_type == "delayed_immunotherapy_effect" for hit in alternatives
    )


def test_mefv_long_discussion_sentence_is_truncated_to_fact():
    from app.services.recall_hardening import _factual_genotype_quote

    quote = _factual_genotype_quote(
        "Whole-exome sequencing studies determined this patient to harbor a "
        "germline P369S/R408Q variant of the pyrin inflammasome, consistent "
        "with a previously reported genotype associated with atypical symptoms "
        "of FMF. Other authors have also indicated that these mutations may "
        "be sufficient to drive inflammatory toxicities."
    )
    parsed = parse_genotype(quote)
    assert "consistent with" not in quote.lower()
    assert parsed is not None
    assert parsed.gene == "MEFV"
    assert parsed.state == GenotypeState.VARIANT_PRESENT.value
    assert parsed.origin == GenotypeOrigin.GERMLINE.value


def test_title_only_genotype_is_not_scanned():
    pages = read_page_text_from_string(TITLE_ONLY_TEXT)
    chunks = chunk_pages(1, pages)
    hits = [hit for hit in scan_genotype_text(pages, chunks) if hit.status == "READY"]
    assert hits == []


def read_page_text_from_string(text: str) -> dict[int, str]:
    from app.services.chunking import PAGE_MARKER_RE

    matches = list(PAGE_MARKER_RE.finditer(text))
    pages: dict[int, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        pages[int(match.group(1))] = text[start:end].strip()
    return pages


def test_irae_duplicates_collapse_to_one():
    events = [
        Event(
            case_id=1,
            event_type=EventType.OTHER,
            description="Grade 3 hepatotoxicity after ipilimumab/nivolumab.",
        ),
        Event(
            case_id=1,
            event_type=EventType.OTHER,
            description="Admission for polymyositis after checkpoint blockade.",
        ),
        Event(
            case_id=1,
            event_type=EventType.OTHER,
            description="Notes again described polymyositis on anti-PD-1 therapy.",
        ),
        Event(
            case_id=1,
            event_type=EventType.OTHER,
            description="Discussion mentioned polymyositis while on anti-PD-1 therapy.",
        ),
    ]
    groups = canonical_irae_groups(events)
    types = {parsed.event_type for parsed, _rows in groups}
    assert "polymyositis" in types
    assert "hepatotoxicity" in types
    polymyositis = next(rows for parsed, rows in groups if parsed.event_type == "polymyositis")
    assert len(polymyositis) == 3


def test_episode_restatement_is_not_duplicated():
    events = [
        Event(
            case_id=1,
            event_type=EventType.TUMOR_REGRESSION,
            description="All in-transit metastases had completely disappeared clinically.",
            relation_to_regression="DURING",
        ),
        Event(
            case_id=1,
            event_type=EventType.TUMOR_REGRESSION,
            description="All in-transit metastases had resolved clinically and radiographically.",
            relation_to_regression="DURING",
        ),
    ]
    drafts = build_regression_episodes(events)
    assert len(drafts) == 1
    assert drafts[0].associated_event_ids == [events[0].id, events[1].id]


def test_pipeline_recovers_moreira_core_when_llm_is_empty(
    db_session, tmp_path: Path
):
    case, source_run, _event = _setup_case(db_session, tmp_path)
    Path(case.paper.extracted_text_path).write_text(MOREIRA_RECALL_TEXT, encoding="utf-8")
    db_session.add(
        Event(
            case_id=case.id,
            extraction_run_id=source_run.id,
            event_type=EventType.OTHER,
            description="BRAFV600 status was found to be wild-type.",
        )
    )
    db_session.commit()
    run = BiologicalObservationPipeline(_empty_provider()).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    assert run.schema_version == "phase3.4"
    genotypes = (
        db_session.query(GenotypeObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert len(genotypes) == 1
    assert genotypes[0].gene == "BRAF"
    assert genotypes[0].state == GenotypeState.WILD_TYPE
    from app.models import BiologicalObservation

    observations = (
        db_session.query(BiologicalObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert any(
        row.observation_domain == ObservationDomain.BIOLOGICAL_STATE.value
        and row.domain_secondary == ObservationDomain.DIAGNOSTIC_EVIDENCE.value
        and "CD3" in row.variable_name
        for row in observations
    )
    alternatives = (
        db_session.query(ExplanatoryAlternative)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert any(
        row.alternative_type == "delayed_immunotherapy_effect" for row in alternatives
    )
    recovered = (run.result_json or {}).get("recovered_from_recall", [])
    kinds = {row["kind"] for row in recovered}
    assert {"immune", "genotype", "alternative"} <= kinds


def test_pipeline_recovers_oswalt_genotypes_and_dedups_irae(
    db_session, tmp_path: Path
):
    case, source_run, _event = _setup_case(db_session, tmp_path)
    Path(case.paper.extracted_text_path).write_text(OSWALT_RECALL_TEXT, encoding="utf-8")
    for description in (
        "Grade 3 hepatotoxicity after ipilimumab/nivolumab.",
        "Admission for polymyositis after checkpoint blockade.",
        "Notes again described polymyositis on anti-PD-1 therapy.",
        "Discussion mentioned polymyositis while on anti-PD-1 therapy.",
        "BRAF mutation analysis was positive and detected a V600E mutation.",
        "Germline P369S/R408Q variant of the pyrin inflammasome.",
    ):
        db_session.add(
            Event(
                case_id=case.id,
                extraction_run_id=source_run.id,
                event_type=EventType.OTHER,
                description=description,
            )
        )
    db_session.commit()
    run = BiologicalObservationPipeline(_empty_provider()).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    genotype_rows = (
        db_session.query(GenotypeObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    braf = [row for row in genotype_rows if row.gene == "BRAF"]
    assert braf
    assert braf[0].state == GenotypeState.MUTATED
    mefv = [
        row
        for row in db_session.query(GenotypeObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
        if row.gene == "MEFV"
    ]
    assert mefv
    assert mefv[0].state == GenotypeState.VARIANT_PRESENT
    assert (
        mefv[0].origin == GenotypeOrigin.GERMLINE
        or mefv[0].origin == GenotypeOrigin.GERMLINE.value
    )
    iraes = (
        db_session.query(ImmuneRelatedAdverseEvent)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    polymyositis = [row for row in iraes if row.event_type == "polymyositis"]
    assert len(polymyositis) == 1


def test_unclear_phase2_event_is_reconciliation_required(
    db_session, tmp_path: Path
):
    case, source_run, _event = _setup_case(db_session, tmp_path)
    Path(case.paper.extracted_text_path).write_text(
        "=== PAGE 1 ===\nCase Presentation\nA patient with metastatic melanoma was observed.\n",
        encoding="utf-8",
    )
    db_session.add(
        Event(
            case_id=case.id,
            extraction_run_id=source_run.id,
            event_type=EventType.OTHER,
            description="The specimen was BRAF V600.",
        )
    )
    db_session.commit()
    run = BiologicalObservationPipeline(_empty_provider()).run_case(
        db_session, case.id, source_run_id=source_run.id
    )
    genotypes = (
        db_session.query(GenotypeObservation)
        .filter_by(created_from_run_id=run.id)
        .all()
    )
    assert genotypes == []
    required = (run.result_json or {}).get("reconciliation_required", [])
    assert any(row["kind"] == "genotype" for row in required)


def test_core_signature_stability_is_perfect_on_identical_sets():
    first = {("genotype", "braf", "wild_type"), ("immune", "infiltration")}
    assert stability_score([first, first, first]) == 1.0
    assert stability_score([first, first, set()]) == 0.0
