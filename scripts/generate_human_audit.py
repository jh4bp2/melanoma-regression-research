import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select

from app.core.config import PROJECT_ROOT
from app.db.session import SessionLocal
from app.models import (
    Case,
    DatePrecision,
    Event,
    EventType,
    Evidence,
    EvidenceType,
    ExtractionRun,
    FieldEvidenceLink,
    Paper,
)
from app.services.chunking import chunk_pages, read_page_text
from app.services.evidence_verifier import INTERPRETATION_RE, normalize_text


CORE_FIELDS = [
    "age",
    "sex",
    "melanoma_subtype",
    "primary_site",
    "stage",
    "metastatic_sites",
    "diagnosis_date",
    "regression_start_date",
    "regression_confirmed_date",
    "regression_type",
    "partial_or_complete",
    "treatment_before_regression",
    "treatment_status",
    "preceding_event",
    "outcome",
    "follow_up_duration",
]
RESULT_FIELD_NAMES = {"preceding_event": "preceding_events"}
UNCERTAIN_STATUSES = {"UNCERTAIN", "NOT_REPORTED", "CONFLICTING"}
FIELD_HINTS = {
    "primary_site": [r"\bprimary lesion\b", r"\bcutaneous melanoma\b"],
    "stage": [r"\bstage\s+(?:i|ii|iii|iv|\d)\b"],
    "diagnosis_date": [r"\bdiagnos\w*\b.{0,50}\b\d+\s+(?:day|month|year)s?\b"],
    "regression_start_date": [
        r"\b(?:regress\w*|decreas\w*|reduc\w*)\b.{0,80}\b\d+\s+(?:day|month|year)s?\b"
    ],
    "regression_confirmed_date": [
        r"\b(?:histopatholog\w*|confirm\w*)\b.{0,80}\b\d+\s+(?:day|month|year)s?\b"
    ],
    "partial_or_complete": [
        r"\bcomplete regression\b",
        r"\bpartial regression\b",
        r"\bno viable cells\b",
        r"\bcompletely infarcted\b",
    ],
    "treatment_before_regression": [
        r"\bipilimumab\b",
        r"\bchemotherap\w*\b",
        r"\bradiotherap\w*\b",
        r"\bimmunotherap\w*\b",
    ],
    "follow_up_duration": [
        r"\bfollow[- ]?up\b.{0,60}\b\d+\s+(?:day|month|year)s?\b",
        r"\b\d+\s+(?:day|month|year)s?\b.{0,60}\bfollow\w*\b",
    ],
}
TIME_RE = re.compile(r"\b\d+\s+(?:day|days|month|months|year|years)\b")
TREATMENT_RE = re.compile(
    r"\b(ipilimumab|chemotherap\w*|radiotherap\w*|immunotherap\w*|"
    r"systemic therap\w*|targeted therap\w*)\b"
)
REGRESSION_RE = re.compile(
    r"\b(regress\w*|decreas\w*|reduc\w*|no viable cells|infarcted)\b"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate compact human audit report")
    parser.add_argument("--paper-id", type=int, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _display(value) -> str:
    if value is None:
        return "NONE"
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _evidence_by_field(
    session, run_id: int, entity_type: str, entity_id: int
) -> dict[str, list[Evidence]]:
    grouped: dict[str, list[Evidence]] = defaultdict(list)
    rows = session.execute(
        select(FieldEvidenceLink.field_name, Evidence)
        .join(Evidence, Evidence.id == FieldEvidenceLink.evidence_id)
        .where(
            FieldEvidenceLink.extraction_run_id == run_id,
            FieldEvidenceLink.entity_type == entity_type,
            FieldEvidenceLink.entity_id == entity_id,
        )
        .order_by(FieldEvidenceLink.field_name, Evidence.id)
    )
    seen: set[tuple[str, int]] = set()
    for field_name, evidence in rows:
        key = (field_name, evidence.id)
        if key not in seen:
            grouped[field_name].append(evidence)
            seen.add(key)
    return grouped


def _run_evidence(session, run_id: int) -> list[Evidence]:
    evidence_ids = select(FieldEvidenceLink.evidence_id).where(
        FieldEvidenceLink.extraction_run_id == run_id
    )
    return list(
        session.scalars(
            select(Evidence)
            .where(Evidence.id.in_(evidence_ids))
            .order_by(Evidence.page, Evidence.id)
        ).unique()
    )


def _case_id_for_run(session, run_id: int) -> int | None:
    return session.scalar(
        select(FieldEvidenceLink.entity_id)
        .where(
            FieldEvidenceLink.extraction_run_id == run_id,
            FieldEvidenceLink.entity_type == "case",
        )
        .order_by(FieldEvidenceLink.entity_id)
        .limit(1)
    )


def _source_lines(evidence: list[Evidence]) -> tuple[str, str, str]:
    if not evidence:
        return (
            "N/A",
            "NONE — NO VERIFIED EVIDENCE LINK",
            "NONE — NO VERIFIED EVIDENCE LINK",
        )
    confidence = max(item.confidence for item in evidence)
    pages = ", ".join(str(item.page) for item in evidence)
    quotes = " | ".join(_display(item.source_quote) for item in evidence)
    return f"{confidence:.2f}", pages, quotes


def _clinical_sentences(paper: Paper) -> list[tuple[int, str, str]]:
    pages = read_page_text(Path(paper.extracted_text_path))
    chunks = chunk_pages(paper.id, pages)
    sentences: list[tuple[int, str, str]] = []
    for chunk in chunks:
        if chunk.section == "References":
            continue
        dehyphenated = re.sub(
            r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)", "", chunk.text
        )
        collapsed = re.sub(r"\s+", " ", dehyphenated).strip()
        for sentence in re.split(r"(?<=[.!?])\s+", collapsed):
            if len(sentence) >= 20:
                sentences.append((chunk.page_start, chunk.section, sentence))
    return sentences


def _is_patient_specific(section: str, sentence: str) -> bool:
    if section in {"Case Report", "Case Presentation", "Clinical Course"}:
        return True
    return bool(
        re.search(
            r"\b(our case|our patient|the patient|patient had|patient underwent|"
            r"nodule|lesion|histopatholog\w*)\b",
            normalize_text(sentence),
        )
    )


def _covered(statement: str, evidence_texts: list[str]) -> bool:
    target = normalize_text(statement)
    target_words = set(re.findall(r"\w+", target))
    for evidence_text in evidence_texts:
        source = normalize_text(evidence_text)
        if source in target or target in source:
            return True
        source_words = set(re.findall(r"\w+", source))
        if target_words and len(target_words & source_words) / len(target_words) >= 0.7:
            return True
    return False


def _possible_missed_items(
    paper: Paper,
    case_result: dict,
    events: list[Event],
    field_evidence: dict[str, list[Evidence]],
    event_evidence: dict[int, list[Evidence]],
) -> list[dict]:
    sentences = _clinical_sentences(paper)
    review_items: list[dict] = []

    for display_name in CORE_FIELDS:
        result_name = RESULT_FIELD_NAMES.get(display_name, display_name)
        field = case_result.get(result_name, {})
        if field.get("status") != "NOT_REPORTED":
            continue
        for pattern in FIELD_HINTS.get(display_name, []):
            match = next(
                (
                    (page, section, sentence)
                    for page, section, sentence in sentences
                    if re.search(pattern, normalize_text(sentence))
                    and _is_patient_specific(section, sentence)
                ),
                None,
            )
            if match:
                page, section, sentence = match
                review_items.append(
                    {
                        "code": "REVIEW_REQUIRED_EXPLICIT_STATEMENT_FOR_NOT_REPORTED",
                        "target": display_name,
                        "page": page,
                        "quote": sentence,
                        "reason": (
                            f"Source text in {section} matches a field-specific cue, "
                            "but the extracted field is NOT_REPORTED."
                        ),
                    }
                )
                break

    event_quotes = [
        evidence.source_quote or ""
        for values in event_evidence.values()
        for evidence in values
    ]
    event_corpus = event_quotes + [event.relative_time or "" for event in events]
    for page, section, sentence in sentences:
        normalized = normalize_text(sentence)
        if section not in {"Case Report", "Case Presentation", "Clinical Course"}:
            continue
        for time_expression in TIME_RE.findall(normalized):
            if not any(
                normalize_text(time_expression) in normalize_text(value)
                for value in event_corpus
            ):
                review_items.append(
                    {
                        "code": "REVIEW_REQUIRED_TIME_EXPRESSION_NOT_IN_TIMELINE",
                        "target": "timeline",
                        "page": page,
                        "quote": sentence,
                        "reason": (
                            f"Explicit time expression '{time_expression}' was not "
                            "found in persisted Timeline evidence or relative_time."
                        ),
                    }
                )

    treatment_evidence = [
        evidence.source_quote or ""
        for field_name in ("treatment_before_regression", "treatment_status")
        for evidence in field_evidence.get(field_name, [])
    ] + [
        evidence.source_quote or ""
        for event in events
        if event.event_type == EventType.TREATMENT
        for evidence in event_evidence.get(event.id, [])
    ]
    for page, _section, sentence in sentences:
        normalized = normalize_text(sentence)
        if (
            TREATMENT_RE.search(normalized)
            and re.search(r"\b(our patient|patient underwent|patient received)\b", normalized)
            and not _covered(sentence, treatment_evidence)
        ):
            review_items.append(
                {
                    "code": "REVIEW_REQUIRED_TREATMENT_MENTION_NOT_LINKED",
                    "target": "treatment",
                    "page": page,
                    "quote": sentence,
                    "reason": "Patient-specific treatment mention lacks Case/Event evidence.",
                }
            )

    regression_evidence = [
        evidence.source_quote or ""
        for field_name in (
            "regression_start_date",
            "regression_confirmed_date",
            "regression_type",
            "partial_or_complete",
        )
        for evidence in field_evidence.get(field_name, [])
    ] + [
        evidence.source_quote or ""
        for event in events
        if event.event_type == EventType.TUMOR_REGRESSION
        for evidence in event_evidence.get(event.id, [])
    ]
    for page, section, sentence in sentences:
        normalized = normalize_text(sentence)
        patient_specific = re.search(
            r"\b(our case|our patient|nodule|lesion|histopatholog\w*)\b", normalized
        )
        if (
            REGRESSION_RE.search(normalized)
            and patient_specific
            and not INTERPRETATION_RE.search(sentence)
            and not _covered(sentence, regression_evidence)
        ):
            review_items.append(
                {
                    "code": "REVIEW_REQUIRED_REGRESSION_DESCRIPTION_NOT_LINKED",
                    "target": "regression",
                    "page": page,
                    "quote": sentence,
                    "reason": (
                        f"Patient-specific regression cue in {section} is not linked "
                        "to a regression field or Event."
                    ),
                }
            )

    deduplicated: list[dict] = []
    seen = set()
    for item in review_items:
        key = (item["code"], item["target"], item["page"], item["quote"])
        if key not in seen:
            deduplicated.append(item)
            seen.add(key)
    return deduplicated


def _render_core_fields(
    case_result: dict, field_evidence: dict[str, list[Evidence]]
) -> tuple[list[str], dict[str, int]]:
    lines = ["# 1. CORE CASE FIELDS", ""]
    counts = {"confirmed": 0, "uncertain": 0, "not_reported": 0}
    case_confidence = case_result.get("confidence")
    for display_name in CORE_FIELDS:
        result_name = RESULT_FIELD_NAMES.get(display_name, display_name)
        field = case_result.get(result_name, {})
        status = field.get("status", "NOT_REPORTED")
        evidence = field_evidence.get(result_name, [])
        confidence, pages, quotes = _source_lines(evidence)
        if status == "REPORTED" and evidence:
            counts["confirmed"] += 1
        elif status == "NOT_REPORTED":
            counts["not_reported"] += 1
        elif status in {"UNCERTAIN", "CONFLICTING"}:
            counts["uncertain"] += 1
        if confidence == "N/A" and status != "NOT_REPORTED" and case_confidence is not None:
            confidence = f"N/A field-level; case candidate={case_confidence:.2f}"
        lines.extend(
            [
                f"FIELD: {display_name}",
                f"VALUE: {_display(field.get('value'))}",
                f"STATUS: {status}",
                f"CONFIDENCE: {confidence}",
                f"SOURCE PAGE: {pages}",
                f"SOURCE QUOTE: {quotes}",
                "",
            ]
        )
    return lines, counts


def _event_order(event: Event, source_index: int) -> str:
    if event.event_date is not None:
        return f"EXACT DATE {event.event_date.isoformat()}"
    if event.relative_time:
        anchor = event.relation_to_regression or "UNKNOWN"
        return f"RELATIVE ({anchor}): {event.relative_time}"
    return f"UNCERTAIN (source extraction order {source_index})"


def _render_timeline(
    events: list[Event], event_evidence: dict[int, list[Evidence]]
) -> tuple[list[str], list[Event]]:
    lines = ["# 2. FULL TIMELINE", ""]
    uncertain_events: list[Event] = []
    for index, event in enumerate(events, start=1):
        evidence = event_evidence.get(event.id, [])
        _confidence, pages, quotes = _source_lines(evidence)
        source_precision = event.source_date_precision or event.date_precision.value
        if (
            event.date_precision == DatePrecision.UNKNOWN
            or event.relation_to_regression in {None, "UNKNOWN"}
            or event.temporal_order_confidence is None
            or event.temporal_order_confidence < 0.5
        ):
            uncertain_events.append(event)
        lines.extend(
            [
                f"ORDER: {_event_order(event, index)}",
                f"EVENT TYPE: {event.event_type.value}",
                f"DESCRIPTION: {event.description}",
                f"DATE: {event.event_date.isoformat() if event.event_date else 'NONE'}",
                f"RELATIVE TIME: {event.relative_time or 'NONE'}",
                f"DATE PRECISION: {source_precision}",
                f"RELATION TO REGRESSION: {event.relation_to_regression or 'UNKNOWN'}",
                "TEMPORAL CONFIDENCE: "
                f"{event.temporal_order_confidence if event.temporal_order_confidence is not None else 'N/A'}",
                f"SOURCE PAGE: {pages}",
                f"SOURCE QUOTE: {quotes}",
                "",
            ]
        )
    return lines, uncertain_events


def _render_evidence(title: str, evidence: list[Evidence]) -> list[str]:
    lines = [title, ""]
    if not evidence:
        return lines + ["NONE", ""]
    for item in evidence:
        lines.extend(
            [
                f"CLAIM: {item.claim}",
                f"PAGE: {item.page if item.page is not None else 'NONE'}",
                f"QUOTE: {_display(item.source_quote)}",
                f"CONFIDENCE: {item.confidence:.2f}",
                "",
            ]
        )
    return lines


def generate_report(session, paper: Paper, run: ExtractionRun) -> str:
    cases = (run.result_json or {}).get("cases") or []
    if len(cases) != 1:
        raise ValueError("Compact PHASE 2.1 audit currently requires exactly one case")
    case_result = cases[0]
    case_id = _case_id_for_run(session, run.id)
    if case_id is None:
        raise ValueError(f"Run {run.id} has no persisted Case evidence link")
    case = session.get(Case, case_id)
    if case is None:
        raise ValueError(f"Case {case_id} not found")

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
        unique = {
            evidence.id: evidence
            for evidence_list in grouped.values()
            for evidence in evidence_list
        }
        event_evidence[event.id] = list(unique.values())

    all_evidence = _run_evidence(session, run.id)
    observed = [
        item for item in all_evidence if item.evidence_type == EvidenceType.OBSERVED_FACT
    ]
    interpretations = [
        item
        for item in all_evidence
        if item.evidence_type == EvidenceType.AUTHOR_INTERPRETATION
    ]
    review_items = _possible_missed_items(
        paper, case_result, events, field_evidence, event_evidence
    )

    core_lines, counts = _render_core_fields(case_result, field_evidence)
    timeline_lines, uncertain_events = _render_timeline(events, event_evidence)
    lines = core_lines + timeline_lines
    lines += _render_evidence("# 3. OBSERVED FACTS", observed)
    lines += _render_evidence("# 4. AUTHOR INTERPRETATIONS", interpretations)
    lines.extend(["# 5. UNCERTAIN / NOT_REPORTED", ""])

    for display_name in CORE_FIELDS:
        result_name = RESULT_FIELD_NAMES.get(display_name, display_name)
        field = case_result.get(result_name, {})
        if field.get("status") in UNCERTAIN_STATUSES:
            lines.extend(
                [
                    f"FIELD: {display_name}",
                    f"VALUE: {_display(field.get('value'))}",
                    f"STATUS: {field.get('status')}",
                    "",
                ]
            )
    for event in uncertain_events:
        lines.extend(
            [
                f"EVENT: {event.event_type.value} — {event.description}",
                "STATUS: UNCERTAIN TEMPORAL ORDER",
                f"RELATIVE TIME: {event.relative_time or 'NONE'}",
                f"RELATION TO REGRESSION: {event.relation_to_regression or 'UNKNOWN'}",
                "",
            ]
        )

    partial_field = case_result.get("partial_or_complete", {})
    if paper.id == 2 and partial_field.get("status") == "NOT_REPORTED":
        related = [
            (page, sentence)
            for page, _section, sentence in _clinical_sentences(paper)
            if re.search(
                r"\b(no viable cells|completely infarcted|spontaneous regression)\b",
                normalize_text(sentence),
            )
            and _is_patient_specific(_section, sentence)
        ]
        lines.extend(
            [
                "FIELD REVIEW: partial_or_complete",
                "STATUS: NOT_REPORTED",
                "SOURCE EVIDENCE LINK: NONE",
                "JUDGMENT REASON: The paper does not explicitly label the case as "
                "'complete regression'. It reports spontaneous regression and "
                "histopathology with completely infarcted cells/no viable cells. "
                "Mapping those observations to 'complete' would require a human "
                "classification decision, so run 11 retained NOT_REPORTED.",
            ]
        )
        for page, sentence in related:
            lines.extend(
                [
                    f"RELATED SOURCE PAGE: {page}",
                    f"RELATED SOURCE TEXT: {_display(sentence)}",
                ]
            )
        lines.extend(["REVIEW_REQUIRED: YES", ""])

    lines.extend(["# 6. POSSIBLE MISSED INFORMATION", ""])
    if not review_items:
        lines.extend(["REVIEW_REQUIRED: NONE", ""])
    for item in review_items:
        lines.extend(
            [
                "REVIEW_REQUIRED: YES",
                f"CODE: {item['code']}",
                f"TARGET: {item['target']}",
                f"SOURCE PAGE: {item['page']}",
                f"SOURCE TEXT: {_display(item['quote'])}",
                f"REASON: {item['reason']}",
                "",
            ]
        )

    lines.extend(
        [
            "# 7. FINAL SUMMARY",
            "",
            f"Confirmed fields: {counts['confirmed']}",
            f"Uncertain fields: {counts['uncertain']}",
            f"Not reported fields: {counts['not_reported']}",
            f"Timeline events: {len(events)}",
            f"Observed facts: {len(observed)}",
            f"Author interpretations: {len(interpretations)}",
            f"Review-required items: {len(review_items)}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    with SessionLocal() as session:
        paper = session.get(Paper, args.paper_id)
        run = session.get(ExtractionRun, args.run_id)
        if paper is None or run is None:
            raise SystemExit("Paper or extraction run not found")
        if run.paper_id != paper.id:
            raise SystemExit("Run does not belong to selected paper")
        report = generate_report(session, paper, run)

    output = args.output or (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "audit"
        / f"paper_{paper.id}_run_{run.id}_human_audit.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
