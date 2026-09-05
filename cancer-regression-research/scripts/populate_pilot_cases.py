"""Populate the six source-verified pilot melanoma case extractions."""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATE = "2026-08-31"


def base(case_id: str, paper_id: str, year: str, age: str, sex: str) -> dict[str, str]:
    return {
        "case_id": case_id,
        "paper_id": paper_id,
        "publication_year": year,
        "patient_age": age,
        "patient_sex": sex,
        "cancer_type": "metastatic melanoma",
        "treatment_stopped_before_regression": "unknown",
        "surgery_before_regression": "unknown",
        "infection_before_regression": "unknown",
        "bacterial_infection": "unknown",
        "viral_infection": "unknown",
        "sepsis": "unknown",
        "fever": "unknown",
        "biopsy_or_tissue_injury": "unknown",
        "blood_transfusion": "unknown",
        "complete_remission": "unknown",
        "reviewer": "Codex",
        "extraction_date": DATE,
        "exact_text_available": "yes",
        "interpretation_required": "yes",
        "confidence_level": "medium",
    }


rows: list[dict[str, str]] = []

r = base("C001", "P001", "2013", "44", "male")
r.update({
    "histology": "cutaneous malignant melanoma; Breslow depth 2 mm; Clark level III/IV",
    "stage": "T2bN1aM0 stage IIIB initially; later stage IV",
    "metastatic_sites": "right thigh in-transit cutaneous/subcutaneous lesions; left chest; left axilla; chin; back; right middle lung; right external iliac node; aortopulmonary window node",
    "prior_cancer_treatment": "wide local excision and sentinel-node biopsy; right inguinal lymph-node dissection; adjuvant high-dose interferon alfa for 1 year; palliative radiotherapy 40 Gy/10 fractions to thigh nodules and 30 Gy/10 fractions to intervening skin; excision of chest lesion",
    "days_last_treatment_to_regression": "270",
    "treatment_stopped_before_regression": "yes",
    "surgery_before_regression": "yes",
    "surgery_type": "primary-site re-excision; sentinel and inguinal node surgery; excision of chest metastasis",
    "infection_before_regression": "no",
    "bacterial_infection": "no",
    "viral_infection": "no",
    "sepsis": "no",
    "fever": "yes",
    "biopsy_or_tissue_injury": "yes",
    "blood_transfusion": "unknown",
    "other_major_stressor": "Adacel tetanus-diphtheria-acellular pertussis vaccination followed by a 2-day local and systemic febrile reaction",
    "regression_type": "partial",
    "complete_remission": "no",
    "regression_start_days": "7",
    "immune_findings": "HLA typing: HLA-A2, A29, B8, B44, CW7; HERV-K-MEL was not tested",
    "cd8_tcell_findings": "No direct CD8 measurement; authors note HERV-K-MEL presentation is HLA-A2-restricted",
    "authors_proposed_mechanism": "Authors propose vaccine-associated fever/danger signaling and possible pathogen-peptide cross-reactivity with HERV-K-MEL activating antitumor T cells",
    "alternative_explanations": "Delayed interferon or radiotherapy effect; heterogeneous natural history; residual left axillary melanoma required resection",
    "evidence_strength": "moderate: pathologically confirmed melanoma at multiple sites and close vaccine-regression timing, but uncontrolled case report with prior interferon/radiotherapy and no mechanistic assay",
    "source_quote_or_note": "One week after a 2-day febrile vaccine reaction, clinical improvement was noted; most nodules later vanished, but a persistent left axillary node contained melanoma and was resected",
    "data_quality_notes": "Treatment-to-regression interval is approximate: vaccine was 9 months after completion of interferon and improvement began 1 week later. Disease-free status followed resection of the residual axillary node, so spontaneous complete remission was not assigned.",
    "source_page": "journal pp. e270-e272",
    "source_section": "Case Description; Discussion",
    "source_evidence": "Stage IV cutaneous, nodal and small lung lesions were documented; improvement began 1 week after Tdap-associated fever and serial imaging showed reduction",
    "extraction_confidence": "high",
    "confidence_level": "high",
})
rows.append(r)

r = base("C002", "P002", "2017", "84", "male")
r.update({
    "histology": "cutaneous malignant melanoma with focal necrosis; BRAF V600 wild-type",
    "stage": "multifocal in-transit metastatic melanoma without distant metastasis",
    "metastatic_sites": "right lower-extremity cutaneous and subcutaneous in-transit metastases",
    "prior_cancer_treatment": "ipilimumab 3 mg/kg every 3 weeks for 4 cycles (Dec 2012-Feb 2013); two palliative resections (Feb and Aug 2014)",
    "last_cancer_treatment_date": "August 2014",
    "days_last_treatment_to_regression": "90",
    "treatment_stopped_before_regression": "yes",
    "surgery_before_regression": "yes",
    "surgery_type": "palliative resection of dominant right popliteal lesion in Feb 2014 and right medial-knee lesion in Aug 2014",
    "days_surgery_to_regression": "273",
    "infection_before_regression": "yes",
    "infection_type": "chronically infected ulcerated tumor followed by wound dehiscence and recurrent postoperative wound infections for about 3 months; organism not reported",
    "bacterial_infection": "unknown",
    "viral_infection": "no",
    "sepsis": "no",
    "fever": "unknown",
    "biopsy_or_tissue_injury": "yes",
    "blood_transfusion": "yes",
    "regression_type": "complete",
    "complete_remission": "yes",
    "regression_start_days": "273",
    "remission_duration_months": "21",
    "immune_findings": "Dual IHC showed brisk CD3+ and CD8+ T-cell infiltration in both resected metastases; Feb 2014 specimen was highly necrotic with viable SOX10+ areas",
    "cd8_tcell_findings": "Brisk CD8+ T-cell infiltration in both Feb and Aug 2014 surgical specimens by CD8/SOX10 dual IHC",
    "authors_proposed_mechanism": "Authors hypothesize operative trauma and postoperative infection triggered innate inflammation and a tumor-specific immune response, possibly aided by prior ipilimumab",
    "alternative_explanations": "Very delayed ipilimumab response; effects of serial debulking; heterogeneous lesion-level response",
    "evidence_strength": "moderate: clinical, PET/CT and tissue evidence with immune IHC, but single case and prior checkpoint blockade is a major competing explanation",
    "source_quote_or_note": "Shrinkage began by Nov 2014, 9 months after the first resection; all nonresected lesions disappeared clinically by Mar 2015 and complete clinical/radiographic response was present by Aug 2016",
    "data_quality_notes": "days_surgery_to_regression/regression_start_days approximate 9 months from Feb to Nov 2014. days_last_treatment_to_regression approximate 3 months from Aug surgery. Remission duration uses Mar 2015 clinical disappearance to Aug 2016 confirmed complete clinical/radiographic response.",
    "source_page": "article pp. 2-4",
    "source_section": "Case presentation; Conclusion; Fig. 1-2",
    "source_evidence": "Serial examination and PET/CT documented progression after ipilimumab, then regression after two resections and wound infections; CD3/CD8 IHC showed brisk infiltration",
    "extraction_confidence": "high",
    "confidence_level": "high",
})
rows.append(r)

r = base("C003", "P003", "2018", "55", "female")
r.update({
    "histology": "biopsy-proven metastatic melanoma; primary site not identified",
    "stage": "metastatic disease involving lung, brain and spinal cord described in discussion",
    "metastatic_sites": "left lower-lobe lung nodule; bilateral upper-lobe cavitary lesions; left hilar node; brain; spinal cord",
    "prior_cancer_treatment": "prior ipilimumab with initial response; recurrence was described as ipilimumab-resistant",
    "treatment_stopped_before_regression": "yes",
    "surgery_before_regression": "no",
    "infection_before_regression": "no",
    "bacterial_infection": "no",
    "viral_infection": "no",
    "sepsis": "no",
    "fever": "no",
    "biopsy_or_tissue_injury": "yes",
    "blood_transfusion": "unknown",
    "regression_type": "mixed",
    "complete_remission": "no",
    "immune_findings": "No patient-specific immune assay reported",
    "authors_proposed_mechanism": "Authors postulate that biopsy trauma induced a local inflammatory response leading to regression of the biopsied lesion",
    "alternative_explanations": "Delayed/localized ipilimumab effect; lesion heterogeneity; measurement variability; regression was limited to the biopsied lesion while other pulmonary disease progressed",
    "evidence_strength": "moderate for lesion-level regression: biopsy-confirmed lesion shrank on CT/PET, but systemic disease progressed and prior ipilimumab confounds causality",
    "source_quote_or_note": "At PET/CT 43 days after baseline CT, the biopsied nodule decreased from 27x23 mm to 17x14 mm with minimal FDG uptake (SUV 2.5), while bilateral upper-lobe lesions increased",
    "data_quality_notes": "Exact biopsy date relative to baseline CT/PET was not reported, so no numeric biopsy-to-regression interval was assigned. The lesion continued to decrease over 19 months. This is mixed/lesion-level regression, not systemic remission.",
    "source_page": "article pp. 2-4",
    "source_section": "Case report; Discussion; Figs. 1-3",
    "source_evidence": "CT-guided biopsy confirmed melanoma; subsequent PET/CT documented shrinkage and metabolic quiescence only in that lesion with progression elsewhere",
    "extraction_confidence": "high",
    "confidence_level": "high",
})
rows.append(r)

r = base("C004", "P004", "2015", "83", "male")
r.update({
    "histology": "pulmonary malignant melanoma positive for S-100 and Melan-A on CT-guided biopsy; no primary identified",
    "stage": "solitary pulmonary metastatic melanoma; small hilar/mediastinal nodes cytologically negative",
    "metastatic_sites": "left upper-lobe lingular lung nodule",
    "prior_cancer_treatment": "none before regression; VATS wedge resection performed after regression evidence at 8 months",
    "treatment_stopped_before_regression": "unknown",
    "surgery_before_regression": "no",
    "infection_before_regression": "no",
    "bacterial_infection": "no",
    "viral_infection": "no",
    "sepsis": "no",
    "fever": "no",
    "biopsy_or_tissue_injury": "yes",
    "blood_transfusion": "unknown",
    "regression_type": "complete",
    "complete_remission": "yes",
    "regression_start_days": "180",
    "metabolic_findings": "Lesion FDG SUV declined from 3.4 initially to 0.9 at 6 months, interpreted as reduced metabolic activity",
    "glucose_findings": "FDG-PET SUV fell from 3.4 to 0.9 by 6 months",
    "authors_proposed_mechanism": "No case-specific mechanism established; authors discuss immunologic factors, surgery and infection as general possibilities",
    "alternative_explanations": "Biopsy-induced local injury; sampling or classification uncertainty because no cutaneous primary was found; lesion was ultimately resected",
    "evidence_strength": "moderate-high for regression before treatment: initial biopsy and later resection pathology plus serial PET/CT; single-lesion case with unknown primary",
    "source_quote_or_note": "SUV declined to 0.9 at 6 months; at 8-month wedge resection the nodule contained infarcted/necrotic ghost cells with no viable cells and negative S-100/Melan-A",
    "data_quality_notes": "The 180-day interval is the 6-month scan when reduction was demonstrated, not necessarily first onset. Complete regression is histologic; the residual necrotic nodule was surgically removed.",
    "source_page": "journal pp. 7-9",
    "source_section": "Case Report; Discussion; Figs. 1-2",
    "source_evidence": "Biopsy confirmed melanoma, serial PET showed falling FDG avidity without treatment, and resection pathology at 8 months showed no viable tumor",
    "extraction_confidence": "high",
    "confidence_level": "high",
})
rows.append(r)

r = base("C005", "P005", "1984", "72", "male")
r.update({
    "histology": "malignant melanoma with local neck recurrence; pulmonary metastases assessed radiographically",
    "stage": "metastatic visceral malignant melanoma",
    "metastatic_sites": "neck recurrence; lung nodules",
    "prior_cancer_treatment": "palliative treatment; details require image-only full-text review",
    "treatment_stopped_before_regression": "unknown",
    "surgery_before_regression": "unknown",
    "infection_before_regression": "unknown",
    "regression_type": "partial",
    "complete_remission": "no",
    "remission_duration_months": "53",
    "authors_proposed_mechanism": "Authors report no evidence that the immune system was artificially stimulated",
    "alternative_explanations": "Older chest-radiograph-era evidence; pulmonary nodules lacked reported histologic confirmation in the accessible abstract; palliative treatment details are incomplete",
    "evidence_strength": "low: prolonged serial chest-X-ray regression but incomplete accessible treatment/timeline detail and no reported biopsy confirmation of lung nodules",
    "source_quote_or_note": "Pulmonary nodules regressed over 4 years 5 months from discovery until death; no increase was seen on chest X-rays during the final 3 months",
    "data_quality_notes": "Provisional extraction from bibliographic abstract because the archived article is image-only and machine-readable case text was unavailable. Keep in sensitivity/legacy-evidence stratum pending manual page review.",
    "source_page": "journal pp. 1391-1396 (abstract-level extraction; exact case pages pending)",
    "source_section": "Abstract",
    "source_evidence": "Abstract reports a 72-year-old man with neck recurrence and pulmonary metastases that regressed over 4 years 5 months under palliative care",
    "extraction_confidence": "low",
    "exact_text_available": "no",
    "confidence_level": "low",
})
rows.append(r)

r = base("C006", "P006", "1998", "35", "female")
r.update({
    "histology": "primary cutaneous melanoma, unclassified type, Breslow depth 1.3 mm; pleural biopsy confirmed pulmonary metastatic melanoma",
    "stage": "recurrent metastatic melanoma involving axillary nodes/soft tissue and lung/pleura",
    "metastatic_sites": "left axillary lymph node; left axillary scar; lung; pleura",
    "prior_cancer_treatment": "wide local excision of primary; left axillary node biopsy/dissection; local management of axillary scar recurrence; no conventional or alternative therapy during pulmonary regression",
    "treatment_stopped_before_regression": "yes",
    "surgery_before_regression": "yes",
    "surgery_type": "pleural biopsy confirming pulmonary metastasis; earlier primary excision and axillary lymph-node dissection",
    "infection_before_regression": "no",
    "bacterial_infection": "no",
    "viral_infection": "no",
    "sepsis": "no",
    "fever": "unknown",
    "biopsy_or_tissue_injury": "yes",
    "blood_transfusion": "unknown",
    "other_major_stressor": "Two pregnancies occurred between primary diagnosis and pulmonary metastatic disease",
    "regression_type": "complete",
    "complete_remission": "yes",
    "remission_duration_months": "36",
    "authors_proposed_mechanism": "No definitive mechanism established; pregnancy/hormonal history and biopsy timing are notable associations",
    "alternative_explanations": "Biopsy-associated injury; hormonal/pregnancy-related influence; effects of earlier local treatment; single case",
    "evidence_strength": "moderate-high for spontaneous pulmonary regression: both primary and pulmonary lesions were histologically confirmed and complete regression occurred without therapy",
    "source_quote_or_note": "Partial regression was seen on staging CT before trial enrollment; complete regression occurred over 5 months without conventional or alternative therapy; disease-free at 3 years",
    "data_quality_notes": "Age 35 at pulmonary metastatic diagnosis; primary melanoma was diagnosed at age 29 during pregnancy. Exact biopsy-to-regression interval was not available, so regression_start_days is blank.",
    "source_page": "journal pp. 915-919",
    "source_section": "Case Report; Results",
    "source_evidence": "Pleural biopsy confirmed metastatic melanoma; serial CT documented partial then complete pulmonary regression without intervening therapy",
    "extraction_confidence": "medium",
})
rows.append(r)


def write_csv(path: Path, fieldnames: list[str], records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in fieldnames})


with (DATA / "extraction_template.csv").open(encoding="utf-8-sig", newline="") as handle:
    extraction_fields = next(csv.reader(handle))
with (DATA / "cases.csv").open(encoding="utf-8-sig", newline="") as handle:
    case_fields = next(csv.reader(handle))

write_csv(DATA / "extraction_template.csv", extraction_fields, rows)
write_csv(DATA / "cases.csv", case_fields, rows)

