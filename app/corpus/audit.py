from __future__ import annotations

from pathlib import Path
from typing import Any

from app.corpus.states import PaperIntakeState
from app.corpus.store import CorpusStore
from app.corpus.versions import CORPUS_INFRA_VERSION
from app.core.config import PROJECT_ROOT


def write_batch_audit(
    store: CorpusStore,
    *,
    batch_number: int,
    attempted: list[str],
    summary: dict[str, Any],
    extra_notes: list[str] | None = None,
) -> Path:
    payload = store.read_json("corpus_manifest.json", {"papers": [], "pressure_points": []})
    by_id = {row["candidate_id"]: row for row in payload.get("papers", [])}
    lines = [
        f"# Corpus batch {batch_number}",
        "",
        f"Infrastructure version: {CORPUS_INFRA_VERSION}",
        "",
        f"- papers attempted: {len(attempted)}",
    ]
    success = 0
    failure = 0
    excluded = []
    for candidate_id in attempted:
        row = by_id.get(candidate_id, {})
        status = row.get("fulltext_status")
        if status == PaperIntakeState.FULLTEXT_UNAVAILABLE.value:
            failure += 1
        elif row.get("paper_id"):
            success += 1
        if row.get("extraction_status") == PaperIntakeState.EXCLUDED.value:
            excluded.append(f"{candidate_id}: {row.get('exclusion_reason')}")
    lines.extend(
        [
            f"- full text success: {success}",
            f"- full text failure/unavailable: {failure}",
            f"- cases extracted: {summary.get('cases', 0)}",
            f"- lesions: {summary.get('lesions', 0)}",
            f"- regression episodes: {summary.get('episodes', 0)}",
            f"- observations: {summary.get('observations', 'index-only')}",
            f"- genotypes: {summary.get('genotypes', 'index-only')}",
            f"- immune pathology: {summary.get('immune_pathology', 'index-only')}",
            f"- quote failures: {summary.get('quote_failures', 'not recomputed')}",
            "- ontology pressure points:",
        ]
    )
    points = payload.get("pressure_points") or []
    if points:
        for point in points:
            lines.append(f"  - {point.get('candidate_id')}: {point.get('note')}")
    else:
        lines.append("  - none")
    lines.append("- excluded papers:")
    if excluded:
        for item in excluded:
            lines.append(f"  - {item}")
    else:
        lines.append("  - none")
    if extra_notes:
        lines.append("")
        lines.append("## Notes")
        lines.append("")
        for note in extra_notes:
            lines.append(f"- {note}")
    lines.append("")
    out = PROJECT_ROOT / "data" / "processed" / "audit" / f"corpus_batch_{batch_number}.md"
    if store.root != PROJECT_ROOT / "data" / "corpus":
        out = store.root / f"corpus_batch_{batch_number}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
