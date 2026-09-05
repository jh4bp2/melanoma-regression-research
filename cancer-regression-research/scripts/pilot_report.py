"""Report whether the schema captures five manually reviewed pilot cases."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "cases.csv"
MISSING_TOKENS = {"", "na", "n/a", "unknown"}
IMMUNE_FIELDS = ["immune_findings", "cd8_tcell_findings", "nk_cell_findings", "ifn_gamma_findings", "mhc1_findings", "pd_l1_findings"]
METABOLIC_FIELDS = ["metabolic_findings", "methionine_findings", "sam_findings", "sah_findings", "lactate_findings", "glucose_findings", "glutamine_findings", "alpha_ketoglutarate_findings", "acetyl_coa_findings"]


def get(data: pd.DataFrame, name: str) -> pd.Series:
    return data[name] if name in data.columns else pd.Series(pd.NA, index=data.index, dtype="string", name=name)


def missing(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip().str.lower()
    return series.isna() | values.isin(MISSING_TOKENS)


def any_recorded(data: pd.DataFrame, fields: list[str]) -> pd.Series:
    result = pd.Series(False, index=data.index)
    for name in fields:
        result |= ~missing(get(data, name))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    try:
        data = pd.read_csv(args.csv, dtype=str)
    except (OSError, pd.errors.ParserError) as exc:
        print(f"Cannot read CSV: {exc}")
        return 1

    total = len(data)
    print("Pilot schema-completeness report (not an analysis of remission causes)")
    print(f"Total cases: {total}")
    if total == 0:
        print("No case rows. Missing ratios and field rankings are undefined.")
    else:
        ratios = pd.Series({name: float(missing(data[name]).mean()) for name in data.columns}).sort_values(ascending=False)
        print("\nMissing ratio by field:")
        for name, ratio in ratios.items():
            print(f"  {name}: {ratio:.1%}")
        print("\nTop 10 most-missing variables:")
        for name, ratio in ratios.head(10).items():
            print(f"  {name}: {ratio:.1%} ({int(round(ratio * total))}/{total})")

    print(f"\nCases with infection status information: {int((~missing(get(data, 'infection_before_regression'))).sum())}")
    print(f"Cases with surgery status information: {int((~missing(get(data, 'surgery_before_regression'))).sum())}")
    event_time = pd.to_numeric(get(data, "regression_start_days"), errors="coerce")
    print(f"Cases with event-to-regression timing: {int(event_time.notna().sum())}")
    print(f"Cases with immune biomarker information: {int(any_recorded(data, IMMUNE_FIELDS).sum())}")
    print(f"Cases with metabolic biomarker information: {int(any_recorded(data, METABOLIC_FIELDS).sum())}")

    confidence = get(data, "extraction_confidence")
    known = confidence[~missing(confidence)].str.strip().str.lower()
    print("Extraction confidence distribution:")
    if known.empty:
        print(f"  recorded: 0; missing: {total}")
    else:
        for value, count in known.value_counts().items():
            print(f"  {value}: {count}")
        print(f"  missing: {int(missing(confidence).sum())}")
    print("Use this output only to assess schema fitness and extraction completeness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
