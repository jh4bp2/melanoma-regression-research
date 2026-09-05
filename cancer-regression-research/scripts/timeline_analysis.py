"""Print conceptual timelines and plot documented event-to-regression intervals."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "cases.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "figures"


def numeric(data: pd.DataFrame, name: str) -> pd.Series:
    source = data[name] if name in data.columns else pd.Series(pd.NA, index=data.index)
    return pd.to_numeric(source, errors="coerce")


def labels(data: pd.DataFrame, name: str, fallback: str) -> pd.Series:
    source = data[name] if name in data.columns else pd.Series(pd.NA, index=data.index)
    values = source.astype("string").str.strip()
    return values.mask(values.isna() | (values == ""), fallback)


def chosen_interval(data: pd.DataFrame) -> pd.Series:
    """Prefer the explicitly selected event interval; never infer missing dates."""
    result = numeric(data, "regression_start_days")
    result = result.fillna(numeric(data, "days_surgery_to_regression"))
    return result.fillna(numeric(data, "days_infection_to_regression"))


def print_timelines(data: pd.DataFrame) -> None:
    case_ids = labels(data, "case_id", "unlabeled")
    complete = labels(data, "complete_remission", "unknown").str.lower()
    for index in data.index:
        endpoint = "complete remission or follow-up"
        if complete.loc[index] == "no":
            endpoint = "follow-up (complete remission not documented)"
        print(f"\n{case_ids.loc[index]}")
        print("cancer diagnosis\n|\nmetastatic progression\n|")
        print("major event (surgery/infection/sepsis/biopsy)\n|")
        print(f"regression first detected\n|\n{endpoint}")


def plot_case_timelines(data: pd.DataFrame, output_dir: Path) -> None:
    intervals = chosen_interval(data)
    usable = data.loc[intervals.notna()].copy()
    if usable.empty:
        print("기록된 사건-관해 간격이 없어 사례별 그림을 생성하지 않았습니다.")
        return
    usable["interval"] = intervals[intervals.notna()]
    case_ids = labels(usable, "case_id", "unlabeled")
    fig, ax = plt.subplots(figsize=(10, max(3.5, 0.45 * len(usable) + 1.5)))
    for y, (_, row) in enumerate(usable.iterrows()):
        days = float(row["interval"])
        ax.hlines(y, -days, 0, color="#4472C4", linewidth=2)
        ax.scatter([-days, 0], [y, y], color=["#ED7D31", "#70AD47"], zorder=3)
    ax.set_yticks(range(len(usable)), labels=case_ids.tolist())
    ax.set_xlabel("Days relative to regression first detected (day 0)")
    ax.set_ylabel("Case ID")
    ax.set_title("Documented major event to regression first detected")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    destination = output_dir / "case_timelines.png"
    fig.savefig(destination, dpi=160)
    plt.close(fig)
    print(f"사례별 타임라인 저장: {destination}")


def plot_distribution(data: pd.DataFrame, output_dir: Path) -> None:
    series, names = [], []
    for name, label in [
        ("days_surgery_to_regression", "surgery"),
        ("days_infection_to_regression", "infection"),
        ("regression_start_days", "selected major event"),
    ]:
        values = numeric(data, name).dropna()
        if not values.empty:
            series.append(values)
            names.append(label)
    if not series:
        print("기록된 간격이 없어 전체 간격 분포 그림을 생성하지 않았습니다.")
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(series, tick_labels=names, showmeans=True)
    ax.set_ylabel("Days to regression first detected")
    ax.set_title("Documented event-to-regression intervals")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    destination = output_dir / "event_interval_distribution.png"
    fig.savefig(destination, dpi=160)
    plt.close(fig)
    print(f"간격 분포 저장: {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        data = pd.read_csv(args.csv)
    except (OSError, pd.errors.ParserError) as exc:
        print(f"CSV를 읽을 수 없습니다: {exc}")
        return 1
    if data.empty:
        print("사례 데이터가 비어 있어 타임라인과 그림을 생성하지 않았습니다.")
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print_timelines(data)
    plot_case_timelines(data, args.output_dir)
    plot_distribution(data, args.output_dir)
    print("주의: 기록된 자료만 반영하며 누락된 날짜를 추정하지 않습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
