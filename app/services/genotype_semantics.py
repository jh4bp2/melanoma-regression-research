from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import GenotypeOrigin, GenotypeState, GenotypeVariantType
from app.services.evidence_verifier import normalize_text


WILD_TYPE_RE = re.compile(r"\bwild[\s-]*type\b", re.IGNORECASE)
NOT_DETECTED_RE = re.compile(r"\b(?:not detected|undetectable)\b", re.IGNORECASE)
GERMLINE_RE = re.compile(r"\bgermline\b", re.IGNORECASE)
SOMATIC_RE = re.compile(r"\bsomatic\b", re.IGNORECASE)
RS_RE = re.compile(r"\b(rs\d+)\b", re.IGNORECASE)
CYTO_RE = re.compile(r"\bdel\(\s*([^)]+?)\s*\)|\b(\d+q-)\b", re.IGNORECASE)
PROTEIN_RE = re.compile(r"\b([A-Z])(\d{2,4})([A-Z])\b")
BRAF_GLUED_RE = re.compile(r"\bBRAF\s*V600\w*\b|\bBRAFV600\w*\b", re.IGNORECASE)
GENOTYPE_LANGUAGE_RE = re.compile(
    r"\b(?:wild[\s-]*type|mutation|mutated|variant|germline|somatic|"
    r"deletion|deleted|amplification|amplified|not detected|"
    r"rs\d+|c\.\d+|p\.[A-Za-z]{3}\d+)\b",
    re.IGNORECASE,
)
TREATMENT_ONLY_RE = re.compile(
    r"\b(?:inhibitor|inhibitors|therapy|treated with|combination)\b",
    re.IGNORECASE,
)
MUTATION_ASSAY_RE = re.compile(
    r"\b(?:mutation analysis|molecular testing|genotyp|sequenc|"
    r"wild[\s-]*type|variant|germline|somatic)\b",
    re.IGNORECASE,
)
HUGO_RE = re.compile(r"\b([A-Z]{2,}[A-Z0-9]{0,6})\b")
GENE_BEFORE_CONTEXT_RE = re.compile(
    r"\b([A-Za-z]{2,8})(?:V600\w*)?\s+"
    r"(?:mutation|wild[\s-]*type|status|genotyp|amplif|delet)",
    re.IGNORECASE,
)
GENE_ALIASES = {
    "PYRIN": "MEFV",
    "BRAFV600": "BRAF",
    "BRAFV600E": "BRAF",
    "BRAFV600K": "BRAF",
}
ENGLISH_STOP = {
    "THE",
    "OF",
    "BE",
    "TO",
    "IN",
    "AND",
    "FOR",
    "ON",
    "OR",
    "AN",
    "AS",
    "AT",
    "BY",
    "IF",
    "IS",
    "IT",
    "NO",
    "SO",
    "WE",
    "THIS",
    "THAT",
    "WITH",
    "FROM",
    "WERE",
    "BEEN",
    "INTO",
    "OVER",
    "ALSO",
    "HAVE",
    "HAS",
    "HAD",
    "WAS",
    "ARE",
    "NOT",
    "BUT",
    "HIS",
    "HER",
    "SHE",
    "THEY",
    "THEIR",
    "THAN",
    "THEN",
    "WHEN",
    "WHICH",
    "WHAT",
    "THERE",
    "THESE",
    "THOSE",
    "BOTH",
    "EACH",
    "OTHER",
    "AFTER",
    "BEFORE",
    "DURING",
    "BETWEEN",
    "INITIAL",
    "INDEL",
    "BINDING",
    "DOMAIN",
    "TABLE",
    "FIGURE",
    "PAGE",
    "ROLE",
    "SCORE",
    "VALUE",
    "GENE",
    "PROTEIN",
    "PMR",
    "GCA",
    "FMF",
    "IHC",
    "SNP",
    "WES",
    "NGS",
    "HOW",
    "DISTINCT",
    "GENETIC",
    "ANNOVAR",
    "PROVEAN",
    "POLYPHEN",
    "SIFT",
    "ENSEMBL",
    "RESULTS",
    "DISCUSSION",
    "METHODS",
    "CONCLUSIONS",
    "COMPLEX",
    "PATHWAY",
    "IDENTIFIED",
    "USING",
    "PACKAGE",
    "GLOBAL",
    "EACH",
    "REVIEWED",
    "LIKELY",
    "FUNCTIONAL",
    "ALTERATION",
    "HOMOLOG",
    "HUGO",
    "SIGNALS",
}
GENE_STOP = {
    "MUTATION",
    "VARIANT",
    "GERMLINE",
    "SOMATIC",
    "STATUS",
    "ANALYSIS",
    "DETECTED",
    "POSITIVE",
    "NEGATIVE",
    "WILD",
    "TYPE",
    "TUMOR",
    "TUMOUR",
    "MELANOMA",
    "PATIENT",
    "SPECIMEN",
    "SEQUENCING",
    "MOLECULAR",
    "TESTING",
    "LESION",
    "BIOPSY",
    "WHOLE",
    "EXOME",
    "FUSION",
    "COPY",
    "NUMBER",
    "PROTEIN",
    "CODING",
}
IHC_OR_NON_GENE = {
    "CD1",
    "CD2",
    "CD3",
    "CD4",
    "CD5",
    "CD8",
    "CD20",
    "CD34",
    "CD45",
    "CD56",
    "CD68",
    "CD99",
    "SOX10",
    "S100",
    "MART",
    "MART1",
    "MELANA",
    "HMB45",
    "KI67",
    "LCA",
    "CGA",
    "SYN",
    "PLAP",
    "CK",
    "AE1",
    "AE3",
    "GATA3",
    "MITF",
    "PRAME",
    "VIMENTIN",
    "PD1",
    "PDL1",
    "CTLA4",
    "PET",
    "CT",
    "MRI",
    "IHC",
    "SNP",
    "FMF",
    "PMA",
    "LN",
    "DNA",
    "RNA",
    "PCR",
    "NGS",
    "WES",
    "SUV",
    "FDG",
    "ALT",
    "AST",
    "CRP",
    "FDA",
    "USA",
    "LD",
    "MEK",
    "PD",
    "CTLA",
    "TABLE",
    "FIG",
    "PAGE",
}


@dataclass(frozen=True)
class ParsedGenotype:
    gene: str
    variant: str | None
    transcript: str | None
    coding_change: str | None
    protein_change: str | None
    rs_id: str | None
    variant_type: str
    zygosity: str | None
    origin: str
    state: str
    assay: str | None
    source_context: str


def _extract_gene(raw: str) -> str | None:
    cyto = CYTO_RE.search(raw)
    if cyto:
        return f"del({cyto.group(1) or cyto.group(2)})"
    if BRAF_GLUED_RE.search(raw):
        return "BRAF"
    if re.search(r"\bpyrin\b", raw, re.IGNORECASE) and PROTEIN_RE.search(raw):
        return "MEFV"
    ranked: list[str] = []
    for match in GENE_BEFORE_CONTEXT_RE.finditer(raw):
        token = GENE_ALIASES.get(match.group(1).upper(), match.group(1).upper())
        if (
            _usable_gene_token(token)
            and _token_looks_like_symbol(match.group(1))
            and not _treatment_only_span(raw, match.start(), match.end())
        ):
            ranked.append(token)
    for match in HUGO_RE.finditer(raw):
        token = GENE_ALIASES.get(match.group(1).upper(), match.group(1).upper())
        if not _usable_gene_token(token):
            continue
        if not _token_looks_like_symbol(match.group(1)):
            continue
        if _treatment_only_span(raw, match.start(), match.end()):
            continue
        ranked.append(token)
    return ranked[0] if ranked else None


def _token_looks_like_symbol(original: str) -> bool:
    if original.isupper() and 3 <= len(original) <= 8:
        return True
    if re.match(r"^[A-Z]{2,7}\d[A-Z0-9]?$", original):
        return True
    if original.islower() and original.casefold() not in {
        word.casefold() for word in ENGLISH_STOP
    }:
        return True
    return False


def _usable_gene_token(token: str) -> bool:
    if token in IHC_OR_NON_GENE or token in GENE_STOP or token in ENGLISH_STOP:
        return False
    if len(token) < 3:
        return False
    if token.startswith("CD") and token[2:].isdigit():
        return False
    return token.isalpha() or any(char.isdigit() for char in token)


def _treatment_only_span(raw: str, start: int, end: int) -> bool:
    window = raw[max(0, start - 24) : min(len(raw), end + 36)]
    if not TREATMENT_ONLY_RE.search(window):
        return False
    return not MUTATION_ASSAY_RE.search(window)


def parse_genotype(*parts: str | None) -> ParsedGenotype | None:
    text = normalize_text(" ".join(part for part in parts if part))
    if not text:
        return None
    raw = " ".join(part for part in parts if part)
    gene = _extract_gene(raw)
    if gene is None:
        return None
    variant_type = GenotypeVariantType.UNKNOWN.value
    protein_change = None
    coding_change = None
    variant = None
    cyto = CYTO_RE.search(raw)
    if cyto:
        variant_type = GenotypeVariantType.CYTOGENETIC.value
        variant = gene
    else:
        proteins = [
            f"{match.group(1)}{match.group(2)}{match.group(3)}"
            for match in PROTEIN_RE.finditer(raw)
        ]
        if proteins:
            protein_change = "/".join(dict.fromkeys(proteins))
            variant = protein_change
            variant_type = (
                GenotypeVariantType.SNV.value
                if len(proteins[0]) <= 6
                else GenotypeVariantType.OTHER.value
            )
        v600 = re.search(r"\b(v600\w*)\b", text, re.IGNORECASE)
        if v600 and not protein_change:
            variant = v600.group(1).upper()
            protein_change = variant
            variant_type = GenotypeVariantType.SNV.value
        elif BRAF_GLUED_RE.search(raw) and not protein_change:
            glued = re.search(r"v600\w*", raw, re.IGNORECASE)
            if glued:
                variant = glued.group(0).upper()
                protein_change = variant
                variant_type = GenotypeVariantType.SNV.value
        coding = re.search(r"\b(c\.\S+)", raw)
        if coding:
            coding_change = coding.group(1).rstrip(").,;")
    if WILD_TYPE_RE.search(text) or WILD_TYPE_RE.search(raw):
        state = GenotypeState.WILD_TYPE.value
    elif NOT_DETECTED_RE.search(text):
        state = GenotypeState.NOT_DETECTED.value
    elif re.search(r"\bamplif\w*", text):
        state = GenotypeState.AMPLIFIED.value
        variant_type = GenotypeVariantType.OTHER.value
    elif cyto or re.search(r"\bdelet\w*", text):
        state = (
            GenotypeState.VARIANT_PRESENT.value
            if GERMLINE_RE.search(text)
            else GenotypeState.DELETED.value
        )
        variant_type = variant_type or GenotypeVariantType.DELETION.value
    elif GERMLINE_RE.search(text) or re.search(r"\bvariant\b", text):
        state = GenotypeState.VARIANT_PRESENT.value
    elif re.search(r"\bmutat\w*", text):
        state = GenotypeState.MUTATED.value
    else:
        state = GenotypeState.UNKNOWN.value
    if GERMLINE_RE.search(text):
        origin = GenotypeOrigin.GERMLINE.value
    elif SOMATIC_RE.search(text):
        origin = GenotypeOrigin.SOMATIC.value
    else:
        origin = GenotypeOrigin.UNKNOWN.value
    rs_match = RS_RE.search(raw)
    assay = None
    if re.search(r"\bwhole[\s-]*exome|wes\b", text):
        assay = "whole-exome sequencing"
    elif re.search(r"\b(?:ngs|next-generation sequencing)\b", text):
        assay = "next-generation sequencing"
    elif re.search(r"\bbiopsy\b", text):
        assay = "lesion biopsy sequencing"
    return ParsedGenotype(
        gene=gene,
        variant=variant,
        transcript=None,
        coding_change=coding_change,
        protein_change=protein_change,
        rs_id=rs_match.group(1).lower() if rs_match else None,
        variant_type=variant_type,
        zygosity=None,
        origin=origin,
        state=state,
        assay=assay,
        source_context=raw.strip()[:500],
    )


def is_genotype_claim(*parts: str | None) -> bool:
    text = " ".join(part for part in parts if part)
    if not text:
        return False
    if CYTO_RE.search(text):
        return True
    if _extract_gene(text) is None:
        return False
    if _treatment_only_span(text, 0, len(text)) and not GENOTYPE_LANGUAGE_RE.search(text):
        return False
    return bool(GENOTYPE_LANGUAGE_RE.search(text) or BRAF_GLUED_RE.search(text))


def genotype_state_is_clear(parsed: ParsedGenotype | None) -> bool:
    if parsed is None:
        return False
    return parsed.state != GenotypeState.UNKNOWN.value
