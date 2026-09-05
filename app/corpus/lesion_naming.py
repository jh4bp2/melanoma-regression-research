from __future__ import annotations

import re

from app.services.evidence_verifier import normalize_text
from app.services.lesion_identity import parse_lesion_text


WEAK_NAME_RE = re.compile(
    r"^(?:the )?(?:right |left )?(?:mass|lesion|nodule|tumor)$",
    re.I,
)


def is_weak_lesion_name(name: str | None) -> bool:
    if not name:
        return True
    return bool(WEAK_NAME_RE.match(name.strip()))


def improved_lesion_name(
    current: str | None,
    evidence_texts: list[str],
    *,
    forbidden_names: list[str] | None = None,
) -> str | None:
    if not is_weak_lesion_name(current):
        return None
    laterality = None
    if current and re.search(r"\bright\b", current, re.I):
        laterality = "right"
    elif current and re.search(r"\bleft\b", current, re.I):
        laterality = "left"
    forbidden = {normalize_text(name) for name in (forbidden_names or []) if name}
    ranked: list[str] = []
    for text in evidence_texts:
        normalized = normalize_text(text)
        if re.search(r"\b(?:thigh|femur)\b", normalized) and re.search(
            r"\b(?:mass|tubular|lymphovascular|subcutaneous)\b", normalized
        ):
            side = f"{laterality} " if laterality else ""
            if "lymphovascular" in normalized or "tubular" in normalized:
                ranked.append(f"{side}thigh lymphovascular mass".strip())
            else:
                layer = "subcutaneous " if "subcutaneous" in normalized else ""
                ranked.append(f"{side}{layer}thigh mass".replace("  ", " ").strip())
            continue
        parsed = parse_lesion_text(text)
        if (
            parsed
            and parsed.anatomical_location
            and parsed.anatomical_location not in {"PRIMARY_SITE", "ANKLE"}
        ):
            label = parsed.canonical_name
            if laterality and laterality not in label:
                label = f"{laterality} {label}"
            ranked.append(label)
    for best in ranked:
        if normalize_text(best) in forbidden:
            continue
        if normalize_text(best) != normalize_text(current or ""):
            return best
    return None
