import json
import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select

from app.core.config import PROJECT_ROOT
from app.db.session import SessionLocal
from app.models import Case, Event, EventType, Evidence, ExtractionRun, Paper
from app.services.chunking import chunk_pages, read_page_text
from app.services.evidence_verifier import normalize_text
from scripts.generate_human_audit import (
    RESULT_FIELD_NAMES,
    _case_id_for_run,
    _evidence_by_field,
    _possible_missed_items,
)


OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "audit" / "phase2_2_human_adjudication.md"
)
TARGETS = [
    ("Ong", 2, 11, 5),
    ("Behnia", 1, 10, 1),
]
SPECIAL_TERMS = [
    "complete regression",
    "spontaneous regression",
    "no evidence of disease",
    "disappearance",
    "disappear",
    "completely",
    "complete",
    "partially",
    "partial",
    "resolved",
    "resolution",
    "regression",
]


@dataclass(frozen=True)
class SourceSentence:
    page: int
    section: str
    chunk_index: int
    sentence_index: int
    text: str


def _display(value) -> str:
    if value is None:
        return "NONE"
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _source_sentences(paper: Paper) -> list[SourceSentence]:
    pages = read_page_text(Path(paper.extracted_text_path))
    chunks = chunk_pages(paper.id, pages)
    records: list[SourceSentence] = []
    for chunk in chunks:
        dehyphenated = re.sub(
            r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)", "", chunk.text
        )
        collapsed = re.sub(r"\s+", " ", dehyphenated).strip()
        sentences = [
            sentence
            for sentence in re.split(r"(?<=[.!?])\s+", collapsed)
            if sentence.strip()
        ]
        for index, sentence in enumerate(sentences):
            records.append(
                SourceSentence(
                    page=chunk.page_start,
                    section=chunk.section,
                    chunk_index=chunk.chunk_index,
                    sentence_index=index,
                    text=sentence.strip(),
                )
            )
    return records


def _best_sentence(
    source_records: list[SourceSentence], page: int, target: str
) -> SourceSentence:
    normalized_target = normalize_text(target)
    candidates = [record for record in source_records if record.page == page]
    exact = next(
        (
            record
            for record in candidates
            if normalize_text(record.text) == normalized_target
        ),
        None,
    )
    if exact:
        return exact

    target_words = set(re.findall(r"\w+", normalized_target))

    def score(record: SourceSentence) -> float:
        words = set(re.findall(r"\w+", normalize_text(record.text)))
        return len(words & target_words) / max(len(words | target_words), 1)

    best = max(candidates, key=score, default=None)
    if best is None or score(best) < 0.45:
        raise ValueError(f"Could not locate review source on page {page}: {target}")
    return best


def _context_window(
    source_records: list[SourceSentence], target: SourceSentence
) -> list[tuple[str, SourceSentence]]:
    same_chunk = [
        record
        for record in source_records
        if record.chunk_index == target.chunk_index
    ]
    position = next(
        index for index, record in enumerate(same_chunk) if record == target
    )
    start = max(0, position - 2)
    end = min(len(same_chunk), position + 3)
    window = []
    for index in range(start, end):
        label = "TARGET" if index == position else (
            f"PREVIOUS {position - index}" if index < position else f"NEXT {index - position}"
        )
        window.append((label, same_chunk[index]))
    return window


def _run_context(session, paper: Paper, run: ExtractionRun):
    case_result = (run.result_json or {})["cases"][0]
    case_id = _case_id_for_run(session, run.id)
    if case_id is None:
        raise ValueError(f"Run {run.id} has no persisted case")
    case = session.get(Case, case_id)
    field_evidence = _evidence_by_field(session, run.id, "case", case.id)
    events = list(
        session.scalars(
            select(Event)
            .where(Event.extraction_run_id == run.id, Event.case_id == case.id)
            .order_by(Event.id)
        )
    )
    event_evidence: dict[int, list[Evidence]] = {}
    for event in events:
        grouped = _evidence_by_field(session, run.id, "event", event.id)
        event_evidence[event.id] = list(
            {
                evidence.id: evidence
                for evidence_list in grouped.values()
                for evidence in evidence_list
            }.values()
        )
    review_items = _possible_missed_items(
        paper, case_result, events, field_evidence, event_evidence
    )
    return case_result, field_evidence, events, event_evidence, review_items


def _current_state(
    target: str,
    case_result: dict,
    field_evidence: dict[str, list[Evidence]],
    events: list[Event],
) -> tuple[object, str, str]:
    result_name = RESULT_FIELD_NAMES.get(target, target)
    if result_name in case_result:
        field = case_result[result_name]
        evidence = field_evidence.get(result_name, [])
        confidence = (
            f"{max(item.confidence for item in evidence):.2f}"
            if evidence
            else "N/A — NO VERIFIED FIELD EVIDENCE"
        )
        return field.get("value"), field.get("status", "NOT_REPORTED"), confidence

    if target == "regression":
        values = {
            name: {
                "value": case_result.get(name, {}).get("value"),
                "status": case_result.get(name, {}).get("status"),
            }
            for name in (
                "regression_start_date",
                "regression_confirmed_date",
                "regression_type",
                "partial_or_complete",
            )
        }
        values["tumor_regression_events"] = [
            event.description
            for event in events
            if event.event_type == EventType.TUMOR_REGRESSION
        ]
        confidence_values = [
            item.confidence
            for name in (
                "regression_start_date",
                "regression_confirmed_date",
                "regression_type",
                "partial_or_complete",
            )
            for item in field_evidence.get(name, [])
        ]
        return (
            values,
            "MIXED — SEE INDIVIDUAL REGRESSION FIELDS",
            f"{max(confidence_values):.2f}" if confidence_values else "N/A",
        )
    return None, "UNKNOWN", "N/A"


def _options(target: str) -> list[tuple[str, str, str]]:
    if target == "primary_site":
        return [
            (
                "OPTION A: REPORTED = no cutaneous primary identified",
                "The patient-specific Case Report explicitly says no cutaneous melanoma was identified.",
                "It does not provide an anatomical primary site; an absence state may not fit the current free-text field semantics.",
            ),
            (
                "OPTION B: UNCERTAIN",
                "The source supports an occult or unidentified primary possibility.",
                "The paper does not establish where the primary melanoma arose.",
            ),
            (
                "OPTION C: NOT_REPORTED",
                "No positive primary-site location is reported.",
                "This loses the explicit negative finding that no cutaneous melanoma was identified.",
            ),
        ]
    if target == "partial_or_complete":
        return [
            (
                "OPTION A: REPORTED = complete regression",
                "Histopathology reports completely infarcted/necrotic cells and no viable cells in the nodule.",
                "The paper does not explicitly use 'complete regression', and the lesion was surgically resected.",
            ),
            (
                "OPTION B: UNCERTAIN",
                "Imaging reduction plus no viable cells supports a strong regression signal.",
                "Extent before resection and the category boundary between complete and partial are not explicitly stated.",
            ),
            (
                "OPTION C: NOT_REPORTED",
                "The explicit categorical label complete/partial is absent for this patient.",
                "This omits a potentially classifiable histopathologic endpoint.",
            ),
        ]
    if target == "regression_start_date":
        return [
            (
                "OPTION A: REPORTED = relative expression only",
                "The source explicitly preserves a 19-month period after initial diagnosis.",
                "It describes continued decrease, not the onset date of regression.",
            ),
            (
                "OPTION B: UNCERTAIN",
                "The statement gives temporal follow-up for regression behavior.",
                "The first moment of regression is not identified.",
            ),
            (
                "OPTION C: NOT_REPORTED",
                "No explicit regression start date is stated.",
                "The available relative follow-up remains useful elsewhere in Timeline/outcome.",
            ),
        ]
    return [
        (
            "OPTION A: REPORTED / LINK AS ADDITIONAL EVIDENCE",
            "The source contains a patient-specific documented regression statement.",
            "It may support an existing field or Event without defining onset, extent, or confirmation date.",
        ),
        (
            "OPTION B: UNCERTAIN",
            "The statement is clinically relevant but its exact schema target is ambiguous.",
            "A human must decide which regression dimension it supports.",
        ),
        (
            "OPTION C: KEEP CURRENT EXTRACTION",
            "Existing verified fields and Events may already represent the core observation.",
            "The reviewed statement would remain unlinked as duplicate or contextual evidence.",
        ),
    ]


def _render_context(
    lines: list[str],
    source_records: list[SourceSentence],
    page: int,
    source_text: str,
) -> SourceSentence:
    target = _best_sentence(source_records, page, source_text)
    lines.extend(
        [
            "### SOURCE CONTEXT",
            "",
            f"PAGE: {target.page}",
            f"SECTION: {target.section}",
            "",
        ]
    )
    for label, record in _context_window(source_records, target):
        lines.append(f"{label}: {_display(record.text)}")
    lines.append("")
    return target


def _render_temporal_review(
    lines: list[str], item: dict, target_sentence: SourceSentence
) -> None:
    if item["target"] not in {
        "treatment",
        "timeline",
        "treatment_before_regression",
        "treatment_status",
        "regression_start_date",
        "regression_confirmed_date",
    }:
        return
    normalized = normalize_text(target_sentence.text)
    date_expressions = re.findall(
        r"\b\d+\s+(?:day|days|month|months|year|years)\b", normalized
    )
    relative_expressions = re.findall(
        r"\b(?:before|after|following|throughout|later|earlier)\b[^.;]{0,80}",
        normalized,
    )
    lines.extend(
        [
            "### TREATMENT / TEMPORAL REVIEW",
            "",
            f"EXACT SOURCE EXPRESSION: {_display(target_sentence.text)}",
            f"DATE EXPRESSIONS: {_display(date_expressions)}",
            f"RELATIVE TIME EXPRESSIONS: {_display(relative_expressions)}",
            "RELATION TO REGRESSION: UNKNOWN unless explicitly stated in the source context.",
            "INFERRED CALENDAR DATE: NONE",
            "",
        ]
    )


def _render_review_item(
    lines: list[str],
    item_number: int,
    item: dict,
    source_records: list[SourceSentence],
    case_result: dict,
    field_evidence: dict[str, list[Evidence]],
    events: list[Event],
) -> None:
    value, status, confidence = _current_state(
        item["target"], case_result, field_evidence, events
    )
    lines.extend(
        [
            f"## Review Item {item_number}",
            "",
            f"ITEM ID: {item['item_id']}",
            f"FIELD OR EVENT: {item['target']}",
            f"CURRENT VALUE: {_display(value)}",
            f"CURRENT STATUS: {status}",
            f"CURRENT CONFIDENCE: {confidence}",
            f"WHY REVIEW_REQUIRED: {item['reason']}",
            "",
        ]
    )
    target_sentence = _render_context(
        lines, source_records, item["page"], item["quote"]
    )
    _render_temporal_review(lines, item, target_sentence)
    lines.extend(["### POSSIBLE INTERPRETATIONS", ""])
    for title, possible, missing in _options(item["target"]):
        lines.extend(
            [
                title,
                f"- Why possible: {possible}",
                f"- What is missing: {missing}",
                "",
            ]
        )


def _matched_terms(sentence: str) -> list[str]:
    normalized = normalize_text(sentence)
    matched = []
    for term in SPECIAL_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", normalized):
            matched.append(term)
    return matched


def _render_ong_special_search(
    lines: list[str], source_records: list[SourceSentence]
) -> None:
    matches = [record for record in source_records if _matched_terms(record.text)]
    lines.extend(
        [
            "## Special Review: partial_or_complete",
            "",
            "RULE: 'spontaneous regression' alone must not be classified as complete regression.",
            f"MATCHED LOCATIONS: {len(matches)}",
            "",
        ]
    )
    for index, record in enumerate(matches, start=1):
        lines.extend(
            [
                f"### Expression Location {index}",
                f"MATCHED EXPRESSIONS: {_display(_matched_terms(record.text))}",
                f"PAGE: {record.page}",
                f"SECTION: {record.section}",
                "",
            ]
        )
        for label, context_record in _context_window(source_records, record):
            lines.append(f"{label}: {_display(context_record.text)}")
        lines.append("")


def generate_pack(session) -> str:
    lines: list[str] = []
    total_items = 0
    for label, paper_id, run_id, expected_count in TARGETS:
        paper = session.get(Paper, paper_id)
        run = session.get(ExtractionRun, run_id)
        if paper is None or run is None or run.paper_id != paper.id:
            raise ValueError(f"Invalid target paper/run: {paper_id}/{run_id}")
        (
            case_result,
            field_evidence,
            events,
            _event_evidence,
            review_items,
        ) = _run_context(session, paper, run)
        if len(review_items) != expected_count:
            raise ValueError(
                f"{label} expected {expected_count} review items, got {len(review_items)}"
            )
        source_records = _source_sentences(paper)
        lines.extend([f"# {label}", ""])
        for index, item in enumerate(review_items, start=1):
            item = {**item, "item_id": f"{label.upper()}-{index}"}
            _render_review_item(
                lines,
                index,
                item,
                source_records,
                case_result,
                field_evidence,
                events,
            )
        if label == "Ong":
            _render_ong_special_search(lines, source_records)
        total_items += len(review_items)

    if total_items != 6:
        raise ValueError(f"Expected exactly 6 review items, got {total_items}")
    lines.extend(
        [
            "# Proposed Schema Lessons",
            "",
            "- `primary_site` needs to distinguish a reported negative finding "
            "(no primary identified) from `NOT_REPORTED`.",
            "- `regression_type` and `partial_or_complete` represent different "
            "dimensions but can be conflated by free-text extraction.",
            "- Regression onset, first observed reduction, and histopathologic "
            "confirmation need distinct temporal semantics.",
            "- A treatment history attribute and a timed treatment Event require "
            "separate evidence links and uncertainty states.",
            "- Figure captions and Discussion can contain documented observations; "
            "section alone cannot determine Evidence type.",
            "- Explicit absence and missing reporting require distinct schema states.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    with SessionLocal() as session:
        report = generate_pack(session)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
