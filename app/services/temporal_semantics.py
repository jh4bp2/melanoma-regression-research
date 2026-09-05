from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import TemporalSemanticPrecision


MONTHS = (
    "january|february|march|april|may|june|july|august|"
    "september|october|november|december|"
    "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
)


@dataclass(frozen=True)
class ParsedTemporal:
    temporal_text: str
    temporal_value: float | None
    temporal_unit: str | None
    temporal_relation: str | None
    temporal_precision: TemporalSemanticPrecision
    calendar_date: str | None = None


def parse_temporal(text: str | None) -> ParsedTemporal | None:
    if not text or not str(text).strip():
        return None
    source = str(text).strip()
    folded = source.casefold()

    exact = re.fullmatch(r"\d{4}-\d{2}-\d{2}", source)
    if exact:
        return ParsedTemporal(
            temporal_text=source,
            temporal_value=None,
            temporal_unit=None,
            temporal_relation=None,
            temporal_precision=TemporalSemanticPrecision.EXACT_DATE,
            calendar_date=source,
        )

    month_year = re.search(
        rf"\b(?:by\s+)?({MONTHS})\s+(?:of\s+)?(\d{{4}})\b",
        folded,
    )
    if month_year:
        relation = "BY" if "by " in folded else None
        return ParsedTemporal(
            temporal_text=source,
            temporal_value=float(month_year.group(2)),
            temporal_unit="year_month",
            temporal_relation=relation,
            temporal_precision=TemporalSemanticPrecision.APPROXIMATE_DATE,
        )

    interval = re.search(
        r"\b(?:during|over|throughout|for)\s+(?:the\s+)?"
        r"(?:following|next|preceding|previous|past)?\s*"
        r"(\d+|several|a few|one|two|three|four|five|six)\s+"
        r"(day|days|week|weeks|month|months|year|years)\b",
        folded,
    )
    if interval:
        return ParsedTemporal(
            temporal_text=source,
            temporal_value=_amount(interval.group(1)),
            temporal_unit=_unit(interval.group(2)),
            temporal_relation=_relation(folded) or "DURING",
            temporal_precision=TemporalSemanticPrecision.INTERVAL,
        )

    relative = re.search(
        r"\b(?:approximately|about|around|roughly)?\s*"
        r"(\d+|several|a few|one|two|three|four|five|six)\s+"
        r"(day|days|week|weeks|month|months|year|years)\s+"
        r"(before|after|later|earlier|following|prior)\b|"
        r"\b(before|after|following|later|earlier)\b.{0,20}"
        r"(\d+|several|a few|one|two|three|four|five|six)\s+"
        r"(day|days|week|weeks|month|months|year|years)\b|"
        r"\bat\s+(\d+|several|a few|one|two|three|four|five|six)\s+"
        r"(day|days|week|weeks|month|months|year|years)\b",
        folded,
    )
    if relative:
        if relative.group(1):
            amount, unit, relation_word = (
                relative.group(1),
                relative.group(2),
                relative.group(3),
            )
        elif relative.group(4):
            relation_word, amount, unit = (
                relative.group(4),
                relative.group(5),
                relative.group(6),
            )
        else:
            amount, unit, relation_word = (
                relative.group(7),
                relative.group(8),
                "after",
            )
        precision = (
            TemporalSemanticPrecision.APPROXIMATE_DATE
            if re.search(r"\b(?:approximately|about|around|roughly|several|a few)\b", folded)
            else TemporalSemanticPrecision.RELATIVE_TIME
        )
        return ParsedTemporal(
            temporal_text=source,
            temporal_value=_amount(amount),
            temporal_unit=_unit(unit),
            temporal_relation=_normalize_relation(relation_word),
            temporal_precision=precision,
        )

    if re.search(
        r"\b(?:several months later|weeks later|months later|years later|"
        r"one week later|one month later|shortly after|thereafter)\b",
        folded,
    ):
        unit = "month"
        if "week" in folded:
            unit = "week"
        elif "year" in folded:
            unit = "year"
        value = 1.0 if re.search(r"\b(?:one|1)\b", folded) else None
        return ParsedTemporal(
            temporal_text=source,
            temporal_value=value,
            temporal_unit=unit,
            temporal_relation="AFTER",
            temporal_precision=TemporalSemanticPrecision.RELATIVE_TIME,
        )

    if re.search(r"\b(?:during|after|before|following|later|earlier)\b", folded):
        return ParsedTemporal(
            temporal_text=source,
            temporal_value=None,
            temporal_unit=None,
            temporal_relation=_relation(folded),
            temporal_precision=TemporalSemanticPrecision.RELATIVE_TIME,
        )

    return ParsedTemporal(
        temporal_text=source,
        temporal_value=None,
        temporal_unit=None,
        temporal_relation=None,
        temporal_precision=TemporalSemanticPrecision.UNKNOWN,
    )


def _amount(token: str) -> float | None:
    words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "several": None,
        "a few": None,
    }
    if token.isdigit():
        return float(token)
    return words.get(token)


def _unit(token: str) -> str:
    if token.startswith("day"):
        return "day"
    if token.startswith("week"):
        return "week"
    if token.startswith("month"):
        return "month"
    return "year"


def _normalize_relation(token: str) -> str:
    if token in {"before", "earlier", "prior"}:
        return "BEFORE"
    if token in {"after", "later", "following"}:
        return "AFTER"
    return token.upper()


def _relation(text: str) -> str | None:
    if re.search(r"\b(?:before|earlier|prior)\b", text):
        return "BEFORE"
    if re.search(r"\b(?:after|later|following)\b", text):
        return "AFTER"
    if re.search(r"\bduring\b", text):
        return "DURING"
    return None
