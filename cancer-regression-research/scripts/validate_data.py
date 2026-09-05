"""Validate case data and report non-blocking extraction warnings."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "data" / "cases.csv"
ALLOWED_BOOLEAN = {"yes", "no", "unknown"}
REQUIRED_COLUMNS = {
    "case_id", "paper_id", "cancer_type", "prior_cancer_treatment",
    "treatment_stopped_before_regression", "surgery_before_regression",
    "infection_before_regression", "complete_remission", "regression_type",
    "evidence_strength", "extraction_confidence", "source_page",
    "source_section", "source_evidence",
}
BOOLEAN_COLUMNS = [
    "treatment_stopped_before_regression", "surgery_before_regression",
    "infection_before_regression", "bacterial_infection", "viral_infection",
    "sepsis", "fever", "biopsy_or_tissue_injury", "blood_transfusion",
    "complete_remission",
]
NONNEGATIVE_COLUMNS = [
    "days_last_treatment_to_regression", "days_surgery_to_regression",
    "days_infection_to_regression", "regression_start_days",
    "remission_duration_months",
]


def norm(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.lower()


def is_missing(series: pd.Series, unknown_is_missing: bool = False) -> pd.Series:
    tokens = ["", "na", "n/a"] + (["unknown"] if unknown_is_missing else [])
    return series.isna() | norm(series).isin(tokens)


def get(data: pd.DataFrame, name: str) -> pd.Series:
    if name in data.columns:
        return data[name]
    return pd.Series(pd.NA, index=data.index, dtype="string", name=name)


def row_ids(data: pd.DataFrame, mask: pd.Series) -> str:
    ids = get(data, "case_id").where(~is_missing(get(data, "case_id")), "row")
    return ", ".join(ids[mask].astype(str).tolist())


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = pd.read_csv(path, dtype=str, keep_default_na=True)
    except (OSError, pd.errors.ParserError) as exc:
        return [f"Cannot read CSV: {exc}"], warnings

    absent = sorted(REQUIRED_COLUMNS - set(data.columns))
    if absent:
        return ["Missing required columns: " + ", ".join(absent)], warnings
    if data.empty:
        return errors, warnings

    duplicates = ~is_missing(data["case_id"]) & data["case_id"].duplicated(keep=False)
    if duplicates.any():
        errors.append("Duplicate case_id: " + row_ids(data, duplicates))

    nonblocking = {"evidence_strength", "extraction_confidence", "source_page", "source_section", "source_evidence"}
    for name in sorted(REQUIRED_COLUMNS - nonblocking):
        count = int(is_missing(data[name]).sum())
        if count:
            errors.append(f"Missing required field {name}: {count} row(s)")

    for name in BOOLEAN_COLUMNS:
        if name not in data.columns:
            errors.append(f"Missing boolean column: {name}")
            continue
        invalid = ~is_missing(data[name]) & ~norm(data[name]).isin(ALLOWED_BOOLEAN)
        if invalid.any():
            errors.append(f"Invalid {name} value in: {row_ids(data, invalid)}")

    for name in NONNEGATIVE_COLUMNS:
        if name not in data.columns:
            errors.append(f"Missing interval column: {name}")
            continue
        values = pd.to_numeric(data[name], errors="coerce")
        nonnumeric = ~is_missing(data[name]) & values.isna()
        if nonnumeric.any():
            errors.append(f"Non-numeric {name} in: {row_ids(data, nonnumeric)}")
        if (values < 0).any():
            errors.append(f"Negative {name} in: {row_ids(data, values < 0)}")

    complete, regression = norm(data["complete_remission"]), norm(data["regression_type"])
    conflict = ((complete == "yes") & (regression != "complete")) | ((complete == "no") & (regression == "complete"))
    if conflict.any():
        errors.append("Remission fields conflict in: " + row_ids(data, conflict))

    for flag, detail in [("infection_before_regression", "infection_type"), ("surgery_before_regression", "surgery_type")]:
        if detail not in data.columns:
            errors.append(f"Missing detail column: {detail}")
            continue
        invalid = (norm(data[flag]) == "no") & ~is_missing(data[detail], True)
        if invalid.any():
            errors.append(f"{flag}=no but {detail} is populated in: {row_ids(data, invalid)}")

    no_paper = is_missing(data["paper_id"], True)
    if no_paper.any():
        errors.append("Case without paper source: " + row_ids(data, no_paper))
    papers_path = path.parent / "papers.csv"
    if papers_path.exists():
        try:
            papers = pd.read_csv(papers_path, dtype=str)
            known = set(get(papers, "paper_id").dropna().astype(str).str.strip())
            unresolved = ~no_paper & ~data["paper_id"].astype(str).str.strip().isin(known)
            if unresolved.any():
                errors.append("paper_id not found in papers.csv: " + row_ids(data, unresolved))
        except (OSError, pd.errors.ParserError) as exc:
            warnings.append(f"Could not cross-check papers.csv: {exc}")
    else:
        warnings.append("papers.csv not found; paper_id cross-check skipped")

    infection_unknown = (norm(data["infection_before_regression"]) == "yes") & is_missing(get(data, "infection_type"), True)
    if infection_unknown.any():
        warnings.append("infection=yes but infection_type unknown: " + row_ids(data, infection_unknown))
    duration_missing = (complete == "yes") & is_missing(get(data, "remission_duration_months"), True)
    if duration_missing.any():
        warnings.append("complete_remission=yes but duration missing: " + row_ids(data, duration_missing))

    interval_present = ~is_missing(get(data, "regression_start_days"), True)
    major_event = (
        norm(get(data, "surgery_before_regression")).eq("yes")
        | norm(get(data, "infection_before_regression")).eq("yes")
        | norm(get(data, "biopsy_or_tissue_injury")).eq("yes")
        | norm(get(data, "sepsis")).eq("yes")
        | ~is_missing(get(data, "other_major_stressor"), True)
    )
    no_event = interval_present & ~major_event
    if no_event.any():
        warnings.append("regression_start_days present but major event absent: " + row_ids(data, no_event))

    for name in ["evidence_strength", "extraction_confidence"]:
        absent_value = is_missing(data[name], True)
        if absent_value.any():
            warnings.append(f"{name} missing: " + row_ids(data, absent_value))

    confidence_invalid = ~is_missing(data["extraction_confidence"], True) & ~norm(
        data["extraction_confidence"]
    ).isin({"high", "medium", "low"})
    if confidence_invalid.any():
        errors.append("Invalid extraction_confidence in: " + row_ids(data, confidence_invalid))

    treatment = norm(data["prior_cancer_treatment"])
    has_treatment = ~is_missing(data["prior_cancer_treatment"], True) & ~treatment.isin(["none", "no"])
    no_timing = is_missing(get(data, "last_cancer_treatment_date"), True) & is_missing(get(data, "days_last_treatment_to_regression"), True)
    if (has_treatment & no_timing).any():
        warnings.append("Previous treatment present but treatment-to-regression timing missing: " + row_ids(data, has_treatment & no_timing))

    evidence_missing = is_missing(data["source_page"], True) & is_missing(data["source_section"], True) & is_missing(data["source_evidence"], True)
    if evidence_missing.any():
        warnings.append("Source location/evidence missing: " + row_ids(data, evidence_missing))
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_CASES)
    args = parser.parse_args()
    errors, warnings = validate(args.csv)
    print(f"Validation: {len(errors)} error(s), {len(warnings)} warning(s)")
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
