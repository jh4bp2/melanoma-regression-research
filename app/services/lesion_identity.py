from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import LesionScopeKind
from app.services.evidence_verifier import normalize_text


LATERALITY = {
    "left": "LEFT",
    "right": "RIGHT",
    "bilateral": "BILATERAL",
    "both": "BILATERAL",
}

ORGANS = (
    ("lymph node", "LYMPH_NODE"),
    ("lymph-node", "LYMPH_NODE"),
    ("axilla", "LYMPH_NODE"),
    ("axillary", "LYMPH_NODE"),
    ("inguinal", "LYMPH_NODE"),
    ("iliac", "LYMPH_NODE"),
    ("hilar", "LYMPH_NODE"),
    ("mediastinal", "LYMPH_NODE"),
    ("aortopulmonary", "LYMPH_NODE"),
    ("lung", "LUNG"),
    ("pulmonary", "LUNG"),
    ("lobe", "LUNG"),
    ("liver", "LIVER"),
    ("hepatic", "LIVER"),
    ("brain", "BRAIN"),
    ("cerebral", "BRAIN"),
    ("skin", "SKIN"),
    ("cutaneous", "SKIN"),
    ("subcutaneous", "SKIN"),
    ("thigh", "SKIN"),
    ("leg", "SKIN"),
    ("knee", "SKIN"),
    ("popliteal", "SKIN"),
    ("tibial", "SKIN"),
    ("heel", "SKIN"),
    ("ankle", "SKIN"),
    ("toe", "SKIN"),
    ("fingernail", "SKIN"),
    ("fingertip", "SKIN"),
    ("digit", "SKIN"),
    ("subungual", "SKIN"),
    ("nipple", "SKIN"),
    ("chest", "SKIN"),
    ("pectoral", "SKIN"),
    ("back", "SKIN"),
    ("bone", "BONE"),
)

LOCATIONS = (
    ("lower lobe", "LOWER_LOBE"),
    ("upper lobe", "UPPER_LOBE"),
    ("middle lobe", "MIDDLE_LOBE"),
    ("upper-lobe", "UPPER_LOBE"),
    ("lower-lobe", "LOWER_LOBE"),
    ("axilla", "AXILLA"),
    ("axillary", "AXILLA"),
    ("inguinal", "INGUINAL"),
    ("iliac", "ILIAC"),
    ("aortopulmonary", "AORTOPULMONARY"),
    ("popliteal", "POPLITEAL"),
    ("medial knee", "MEDIAL_KNEE"),
    ("fibular head", "FIBULAR_HEAD"),
    ("anterior tibial", "ANTERIOR_TIBIAL"),
    ("right heel", "HEEL"),
    ("heel", "HEEL"),
    ("ankle", "ANKLE"),
    ("fifth fingertip", "FIFTH_FINGERTIP"),
    ("fingertip", "FINGERTIP"),
    ("fifth digit", "FIFTH_DIGIT"),
    ("subungual", "SUBUNGUAL"),
    ("toe", "TOE"),
    ("upper right thigh", "UPPER_THIGH"),
    ("upper lateral right thigh", "UPPER_LATERAL_THIGH"),
    ("thigh", "THIGH"),
    ("nipple", "NIPPLE"),
    ("pectoral", "PECTORAL"),
    ("rectus", "RECTUS"),
    ("chin", "CHIN"),
    ("central back", "BACK"),
    ("back", "BACK"),
    ("sentinel", "SENTINEL"),
    ("primary", "PRIMARY_SITE"),
)

TYPES = (
    ("in-transit", "IN_TRANSIT"),
    ("in transit", "IN_TRANSIT"),
    ("lymph node", "LYMPH_NODE"),
    ("metastas", "METASTASIS"),
    ("nodule", "NODULE"),
    ("lesion", "LESION"),
    ("nevus", "PRIMARY"),
    ("primary", "PRIMARY"),
    ("mass", "MASS"),
)

COMPATIBLE_TYPES = {
    frozenset({"NODULE", "LESION"}),
    frozenset({"NODULE", "METASTASIS"}),
    frozenset({"LESION", "METASTASIS"}),
    frozenset({"LESION", "MASS"}),
    frozenset({"NODULE", "MASS"}),
    frozenset({"IN_TRANSIT", "METASTASIS"}),
    frozenset({"IN_TRANSIT", "LESION"}),
    frozenset({"IN_TRANSIT", "NODULE"}),
}


@dataclass(frozen=True)
class LesionParse:
    source_text: str
    laterality: str | None
    organ: str | None
    anatomical_location: str | None
    lesion_type: str | None
    procedure: str | None
    procedure_time: str | None
    is_collection: bool
    collection_kind: LesionScopeKind
    identity_key: str
    canonical_name: str


def parse_lesion_text(text: str | None) -> LesionParse | None:
    if not text or not str(text).strip():
        return None
    source = str(text).strip()
    normalized = normalize_text(source)
    laterality = _first_map(normalized, LATERALITY)
    organ = _first_tuple(normalized, ORGANS)
    location = _first_tuple(normalized, LOCATIONS)
    lesion_type = _first_tuple(normalized, TYPES)
    procedure = None
    if re.search(r"\bbiops", normalized):
        procedure = "BIOPSY"
    elif re.search(r"\b(?:resect|excis)", normalized):
        procedure = "RESECTION"
    procedure_time = None
    month_year = re.search(
        r"\b(january|february|march|april|may|june|july|august|"
        r"september|october|november|december)\s+(\d{4})\b",
        normalized,
    )
    if month_year:
        procedure_time = f"{month_year.group(1)}_{month_year.group(2)}"
    is_collection = bool(
        re.search(
            r"\b(?:bilateral|multifocal|multiple|numerous|several|"
            r"in-?transit metastases|all (?:non-?resected )?(?:in-?transit )?"
            r"(?:metastases|nodules|lesions)|aforementioned nodules)\b",
            normalized,
        )
    )
    if laterality == "BILATERAL":
        is_collection = True
    collection_kind = LesionScopeKind.UNKNOWN
    if is_collection:
        if re.search(r"\b(?:multifocal|in-?transit)\b", normalized):
            collection_kind = LesionScopeKind.MULTIFOCAL_DISEASE
        else:
            collection_kind = LesionScopeKind.LESION_COLLECTION
    elif laterality or organ or location:
        collection_kind = LesionScopeKind.SINGLE_LESION
    identity_key = "|".join(
        [
            laterality or "UNK",
            organ or "UNK",
            location or "UNK",
            lesion_type or "UNK",
            procedure or "NONE",
            procedure_time or "NONE",
            "COLL" if is_collection else "SINGLE",
        ]
    )
    return LesionParse(
        source_text=source,
        laterality=laterality,
        organ=organ,
        anatomical_location=location,
        lesion_type=lesion_type,
        procedure=procedure,
        procedure_time=procedure_time,
        is_collection=is_collection,
        collection_kind=collection_kind,
        identity_key=identity_key,
        canonical_name=_canonical_name(
            source, laterality, organ, location, lesion_type, is_collection
        ),
    )


def merge_decision(left: LesionParse, right: LesionParse) -> str:
    """Return CONFIRMED_ALIAS, POSSIBLE_SAME_LESION, or DISTINCT."""
    if left.is_collection != right.is_collection:
        return "DISTINCT"
    if left.laterality and right.laterality and left.laterality != right.laterality:
        return "DISTINCT"
    if left.organ and right.organ and left.organ != right.organ:
        return "DISTINCT"
    if (
        left.anatomical_location
        and right.anatomical_location
        and left.anatomical_location != right.anatomical_location
    ):
        return "DISTINCT"
    if (
        left.procedure_time
        and right.procedure_time
        and left.procedure_time != right.procedure_time
    ):
        return "DISTINCT"
    if not _types_compatible(left.lesion_type, right.lesion_type):
        if (
            {left.lesion_type, right.lesion_type} == {"NODULE", "LYMPH_NODE"}
            and left.laterality
            and left.laterality == right.laterality
            and left.anatomical_location
            and left.anatomical_location == right.anatomical_location
        ):
            return "POSSIBLE_SAME_LESION"
        return "DISTINCT"
    same_laterality = bool(left.laterality and left.laterality == right.laterality)
    same_organ = bool(left.organ and left.organ == right.organ)
    same_location = bool(
        left.anatomical_location
        and left.anatomical_location == right.anatomical_location
    )
    location_fill = (
        same_organ
        and same_laterality
        and bool(left.anatomical_location) != bool(right.anatomical_location)
    )
    same_procedure = bool(
        left.procedure
        and left.procedure == right.procedure
        and (
            not left.procedure_time
            or not right.procedure_time
            or left.procedure_time == right.procedure_time
        )
    )
    if left.identity_key == right.identity_key:
        return "CONFIRMED_ALIAS"
    if same_laterality and same_organ and same_location:
        return "CONFIRMED_ALIAS"
    if same_laterality and same_organ and location_fill:
        procedure_conflict = bool(
            left.procedure
            and right.procedure
            and left.procedure != right.procedure
        )
        if procedure_conflict:
            return "POSSIBLE_SAME_LESION"
        if same_procedure or left.procedure or right.procedure:
            return "CONFIRMED_ALIAS"
        if left.organ == "LUNG" and right.organ == "LUNG":
            return "CONFIRMED_ALIAS"
        return "POSSIBLE_SAME_LESION"
    if same_laterality and same_organ and not left.anatomical_location and not right.anatomical_location:
        return "POSSIBLE_SAME_LESION"
    return "DISTINCT"


def collection_membership_ok(collection: LesionParse, member: LesionParse) -> bool:
    if not collection.is_collection or member.is_collection:
        return False
    if collection.laterality == "BILATERAL":
        if member.laterality not in {None, "LEFT", "RIGHT"}:
            return False
    elif collection.laterality and member.laterality not in {None, collection.laterality}:
        return False
    if collection.organ and member.organ not in {None, collection.organ}:
        return False
    if (
        collection.anatomical_location
        and member.anatomical_location
        and member.anatomical_location != collection.anatomical_location
    ):
        return False
    return bool(collection.organ and (member.organ == collection.organ or member.laterality))


def _types_compatible(left: str | None, right: str | None) -> bool:
    if left is None or right is None or left == right:
        return True
    return frozenset({left, right}) in COMPATIBLE_TYPES


def _first_map(text: str, mapping: dict[str, str]) -> str | None:
    for token, value in mapping.items():
        if re.search(rf"\b{re.escape(token)}\b", text):
            return value
    return None


def _first_tuple(text: str, pairs: tuple[tuple[str, str], ...]) -> str | None:
    for token, value in pairs:
        if token in text:
            return value
    return None


GENERIC_NAMES = {
    "lesion",
    "lesions",
    "right lesion",
    "left lesion",
    "skin lesion",
    "skin lesions",
    "right nodule",
    "left nodule",
    "nodule",
    "lymph node lymph node",
    "lymph node lymph nodes",
}


def _canonical_name(
    source: str,
    laterality: str | None,
    organ: str | None,
    location: str | None,
    lesion_type: str | None,
    is_collection: bool,
) -> str:
    laterality_text = laterality.lower().replace("_", " ") if laterality else None
    location_text = location.lower().replace("_", " ") if location else None
    if organ == "LYMPH_NODE":
        node_label = "lymph nodes" if is_collection else "lymph node"
        parts = [laterality_text, location_text, node_label]
        name = " ".join(part for part in parts if part)
    elif organ == "LIVER":
        name = " ".join(
            part
            for part in [
                laterality_text,
                "hepatic lesions" if is_collection else "hepatic lesion",
            ]
            if part
        )
    else:
        type_label = (
            "lesions"
            if is_collection
            else (lesion_type or "lesion").lower().replace("_", " ")
        )
        if type_label == "lymph node" and location_text:
            type_label = "lymph node"
        organ_text = None
        if organ and organ not in {location, "SKIN"} and organ != "LYMPH_NODE":
            organ_text = organ.lower().replace("_", " ")
        parts = [laterality_text, location_text, organ_text, type_label]
        name = " ".join(part for part in parts if part)
    name = re.sub(r"\b(\w+)(?:\s+\1)+\b", r"\1", name).strip()
    if not name or name in GENERIC_NAMES:
        cleaned = re.sub(r"\s+", " ", source.strip())
        if cleaned and normalize_text(cleaned) not in {
            normalize_text(item) for item in GENERIC_NAMES
        }:
            return cleaned
    return name
