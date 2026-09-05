import argparse
import json
from collections import defaultdict
from pathlib import Path

from sqlalchemy import func, select

from app.core.config import PROJECT_ROOT
from app.db.session import SessionLocal
from app.models import Evidence, Event, ExtractionRun, FieldEvidenceLink, Paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two extraction audit runs")
    parser.add_argument("--paper-id", type=int, required=True)
    parser.add_argument("--old-run", type=int, required=True)
    parser.add_argument("--new-run", type=int, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _field_values(run: ExtractionRun) -> dict[str, dict]:
    result = run.result_json or {}
    flattened: dict[str, dict] = {}
    for field_name, value in (result.get("metadata") or {}).items():
        flattened[f"paper.{field_name}"] = value
    for case_index, case in enumerate(result.get("cases") or [], start=1):
        for field_name, value in case.items():
            if field_name != "confidence":
                flattened[f"case[{case_index}].{field_name}"] = value
    return flattened


def _failure_fields(run: ExtractionRun) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for failure in (run.result_json or {}).get("verification_failures", []):
        grouped[failure["field"]].append(failure)
    return grouped


def _actual_evidence_types(session, run_id: int) -> dict[str, list[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    rows = session.execute(
        select(
            FieldEvidenceLink.entity_type,
            FieldEvidenceLink.field_name,
            Evidence.evidence_type,
        )
        .join(Evidence, Evidence.id == FieldEvidenceLink.evidence_id)
        .where(FieldEvidenceLink.extraction_run_id == run_id)
    )
    for entity_type, field_name, evidence_type in rows:
        grouped[f"{entity_type}.{field_name}"].add(evidence_type.value)
    return {key: sorted(values) for key, values in grouped.items()}


def _run_metrics(session, run: ExtractionRun) -> dict:
    evidence_count = session.scalar(
        select(func.count(func.distinct(FieldEvidenceLink.evidence_id))).where(
            FieldEvidenceLink.extraction_run_id == run.id
        )
    )
    event_count = session.scalar(
        select(func.count(Event.id)).where(Event.extraction_run_id == run.id)
    )
    type_rows = session.execute(
        select(Evidence.evidence_type, func.count(func.distinct(Evidence.id)))
        .join(FieldEvidenceLink, FieldEvidenceLink.evidence_id == Evidence.id)
        .where(FieldEvidenceLink.extraction_run_id == run.id)
        .group_by(Evidence.evidence_type)
    )
    result = run.result_json or {}
    return {
        "status": run.status.value,
        "case_count": len(result.get("cases") or []),
        "event_count": event_count or 0,
        "evidence_count": evidence_count or 0,
        "quote_rejected": len(result.get("verification_failures") or []),
        "reason_codes": run.reason_codes or result.get("partial_reason_codes") or [],
        "retry_count": run.retry_count,
        "prompt_version": run.prompt_version,
        "evidence_type_counts": {
            evidence_type.value: count for evidence_type, count in type_rows
        },
    }


def _display(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def build_diff(session, paper: Paper, old_run: ExtractionRun, new_run: ExtractionRun) -> str:
    old_metrics = _run_metrics(session, old_run)
    new_metrics = _run_metrics(session, new_run)
    old_fields = _field_values(old_run)
    new_fields = _field_values(new_run)
    old_failures = _failure_fields(old_run)
    new_failures = _failure_fields(new_run)
    old_types = _actual_evidence_types(session, old_run.id)
    new_types = _actual_evidence_types(session, new_run.id)

    lines = [
        f"# Paper {paper.id}: run {old_run.id} vs run {new_run.id}",
        "",
        "> Association does not imply causation. This report compares extraction "
        "behavior, not clinical truth.",
        "",
        "## Summary",
        "",
    ]
    for key in (
        "status",
        "case_count",
        "event_count",
        "evidence_count",
        "quote_rejected",
        "retry_count",
        "prompt_version",
        "evidence_type_counts",
        "reason_codes",
    ):
        lines.append(
            f"- `{key}`: {_display(old_metrics[key])} → {_display(new_metrics[key])}"
        )

    lines.extend(["", "## Changed fields", ""])
    changed_count = 0
    all_fields = sorted(set(old_fields) | set(new_fields))
    for field_name in all_fields:
        old = old_fields.get(field_name)
        new = new_fields.get(field_name)
        link_name = field_name.replace("[1]", "")
        old_evidence_types = old_types.get(link_name, [])
        new_evidence_types = new_types.get(link_name, [])
        old_verification = (
            "UNVERIFIED"
            if field_name.replace("[1].", ".") in old_failures
            else "VERIFIED"
            if old and old.get("evidence_refs")
            else "NOT_APPLICABLE"
        )
        new_verification = (
            "UNVERIFIED"
            if field_name.replace("[1].", ".") in new_failures
            else "VERIFIED"
            if new and new.get("evidence_refs")
            else "NOT_APPLICABLE"
        )
        differences = []
        if (old or {}).get("value") != (new or {}).get("value"):
            differences.append("value changed")
        if (old or {}).get("status") != (new or {}).get("status"):
            differences.append("field status changed")
        if old_evidence_types != new_evidence_types:
            differences.append("evidence type changed")
        if old_verification != new_verification:
            differences.append("quote verification changed")
        if not differences:
            continue
        changed_count += 1
        lines.extend(
            [
                f"### `{field_name}`",
                f"- Old value: {_display((old or {}).get('value'))}",
                f"- New value: {_display((new or {}).get('value'))}",
                f"- Old field status: {_display((old or {}).get('status'))}",
                f"- New field status: {_display((new or {}).get('status'))}",
                f"- Old evidence type: {_display(old_evidence_types)}",
                f"- New evidence type: {_display(new_evidence_types)}",
                f"- Old quote verification: `{old_verification}`",
                f"- New quote verification: `{new_verification}`",
                f"- Reason: {', '.join(differences)}.",
                "",
            ]
        )
    if changed_count == 0:
        lines.append("- No case or paper field changes detected.")

    lines.extend(["", "## Verification failures", ""])
    for label, run in (("Old", old_run), ("New", new_run)):
        failures = (run.result_json or {}).get("verification_failures") or []
        lines.append(f"### {label} run {run.id}")
        if not failures:
            lines.append("- None.")
        for failure in failures:
            lines.extend(
                [
                    f"- Field: `{failure['field']}`",
                    f"  - Status: `{failure.get('status', 'UNVERIFIED')}`",
                    f"  - Quote: {_display(failure.get('quote'))}",
                    f"  - Reason: {failure.get('reason')}",
                ]
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    with SessionLocal() as session:
        paper = session.get(Paper, args.paper_id)
        old_run = session.get(ExtractionRun, args.old_run)
        new_run = session.get(ExtractionRun, args.new_run)
        if paper is None or old_run is None or new_run is None:
            raise SystemExit("Paper or extraction run not found")
        if old_run.paper_id != paper.id or new_run.paper_id != paper.id:
            raise SystemExit("Both runs must belong to the selected paper")
        report = build_diff(session, paper, old_run, new_run)

    output = args.output or (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "audit"
        / f"paper_{paper.id}_run_{old_run.id}_vs_{new_run.id}.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
