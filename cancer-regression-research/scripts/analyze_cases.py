"""Descriptive, exploratory summaries of spontaneous-regression cases."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "cases.csv"
MISSING = {"", "na", "n/a", "unknown"}


def column(data: pd.DataFrame, name: str) -> pd.Series:
    if name in data.columns:
        return data[name]
    return pd.Series(pd.NA, index=data.index, dtype="string", name=name)


def norm(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.lower()


def is_missing(series: pd.Series) -> pd.Series:
    return series.isna() | norm(series).isin(MISSING)


def show_counts(title: str, series: pd.Series) -> None:
    absent = is_missing(series)
    print(f"\n{title} (missing={int(absent.sum())})")
    counts = series[~absent].value_counts()
    if counts.empty:
        print("  관찰값 없음")
    else:
        for value, count in counts.items():
            print(f"  {value}: {count}")


def make_groups(data: pd.DataFrame) -> pd.Series:
    surgery = norm(column(data, "surgery_before_regression"))
    infection = norm(column(data, "infection_before_regression"))
    result = pd.Series("unknown", index=data.index, dtype="string")
    result[(surgery == "yes") & (infection == "no")] = "surgery only"
    result[(surgery == "no") & (infection == "yes")] = "infection only"
    result[(surgery == "yes") & (infection == "yes")] = "surgery + infection"
    result[(surgery == "no") & (infection == "no")] = "neither"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    try:
        data = pd.read_csv(args.csv)
    except (OSError, pd.errors.ParserError) as exc:
        print(f"CSV를 읽을 수 없습니다: {exc}")
        return 1

    print("탐색적 기술 분석 - 효과 또는 인과관계 추정이 아닙니다.")
    print(f"\n1. 전체 사례 수: {len(data)} (missing case_id={int(is_missing(column(data, 'case_id')).sum())})")
    show_counts("2. 암종별 사례 수", column(data, "cancer_type"))
    show_counts("3. 완전/부분 관해 등 관해 유형별 사례 수", column(data, "regression_type"))
    show_counts("4. 수술 유무별 사례 수", column(data, "surgery_before_regression"))
    show_counts("5. 감염 유무별 사례 수", column(data, "infection_before_regression"))

    surgery_raw = column(data, "surgery_before_regression")
    infection_raw = column(data, "infection_before_regression")
    surgery, infection = norm(surgery_raw), norm(infection_raw)
    joint_missing = is_missing(surgery_raw) | is_missing(infection_raw)
    both = (surgery == "yes") & (infection == "yes")
    print(f"\n6. 수술+감염 동시 발생: {int(both.sum())} (missing={int(joint_missing.sum())})")

    for label, name in [("세균 감염", "bacterial_infection"), ("패혈증", "sepsis")]:
        values = column(data, name)
        print(f"\n7. {label} yes: {int((norm(values) == 'yes').sum())} (missing={int(is_missing(values).sum())})")

    interval = pd.to_numeric(column(data, "regression_start_days"), errors="coerce")
    median = interval.median() if interval.notna().any() else np.nan
    median_text = "NA" if pd.isna(median) else f"{median:g}"
    print(f"\n8. 주요 사건→관해 시작 중앙값(일): {median_text} (missing={int(interval.isna().sum())})")

    groups = make_groups(data)
    print("\n9. 사건 그룹 비교")
    for name in ["surgery only", "infection only", "surgery + infection", "neither", "unknown"]:
        selected = groups == name
        values = interval[selected]
        group_median = values.median() if values.notna().any() else np.nan
        text = "NA" if pd.isna(group_median) else f"{group_median:g}"
        print(f"  {name}: n={int(selected.sum())}, interval median={text}, interval missing={int(values.isna().sum())}")

    print("\n10. 각 항목에 missing 수를 함께 표시했습니다.")
    print("주의: 작은 표본과 보고 편향 때문에 이 요약은 가설 생성용이며 통계적 유의성이나 인과성을 뜻하지 않습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
