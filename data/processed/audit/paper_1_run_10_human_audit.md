# 1. CORE CASE FIELDS

FIELD: age
VALUE: 55
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1
SOURCE QUOTE: "A 55-year-old woman presented with night sweats, cough, and hemoptysis."

FIELD: sex
VALUE: "woman"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1
SOURCE QUOTE: "A 55-year-old woman presented with night sweats, cough, and hemoptysis."

FIELD: melanoma_subtype
VALUE: "metastatic melanoma"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1
SOURCE QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."

FIELD: primary_site
VALUE: "No primary lesion identified on clinical examination"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1
SOURCE QUOTE: "Patient had no history of melanoma and clinical examination did not reveal a primary lesion."

FIELD: stage
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: metastatic_sites
VALUE: ["lungs (left lower lobe and bilateral upper lungs)", "left hilar node", "brain", "spinal cord"]
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1, 2, 3
SOURCE QUOTE: "In addition to the left lower lobe pulmonary nodule, smaller cavitary lesions were seen in the bilateral upper lungs (Fig. 2)." | "Note left hilar nodal spread (arrowhead)." | "Unfortunately, as is common with this form of treatment, melanoma recurred with lung, brain, and spinal cord metastases, this time resistant to ipilimumab."

FIELD: diagnosis_date
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: regression_start_date
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: regression_confirmed_date
VALUE: "43 days after the baseline CT"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1, 1
SOURCE QUOTE: "The time interval between the baseline CT and PET-CT was 43 days." | "On the other hand, the previously biopsied left lung nodule has decreased in size and showed very minimal FDG uptake with max SUV of 2.5 (Fig. 3A and B)."

FIELD: regression_type
VALUE: "spontaneous regression of a metastatic melanoma pulmonary deposit"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1
SOURCE QUOTE: "Spontaneous regression of a metastatic melanoma pulmonary deposit following biopsy"

FIELD: partial_or_complete
VALUE: "partial"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 2, 2
SOURCE QUOTE: "Spontaneous regression is, by definition, disappearance of a tumor (complete regression) or decrease in size of a tumor (partial regression) in the absence of treatment." | "The left lower lobe nodule (A) has decreased to 17 × 14 mm in size."

FIELD: treatment_before_regression
VALUE: "ipilimumab; timing relative to the initially documented regression is not explicitly stated"
STATUS: UNCERTAIN
CONFIDENCE: N/A field-level; case candidate=0.92
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: treatment_status
VALUE: "unknown"
STATUS: UNCERTAIN
CONFIDENCE: N/A field-level; case candidate=0.92
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: preceding_event
VALUE: ["CT-guided biopsy of the left lower lobe nodule"]
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 1
SOURCE QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."

FIELD: outcome
VALUE: "Melanoma recurred with lung, brain, and spinal cord metastases resistant to ipilimumab; the biopsied lesion continued to decrease in size."
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 3, 3
SOURCE QUOTE: "Unfortunately, as is common with this form of treatment, melanoma recurred with lung, brain, and spinal cord metastases, this time resistant to ipilimumab." | "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."

FIELD: follow_up_duration
VALUE: "19 months that followed after initial diagnosis"
STATUS: REPORTED
CONFIDENCE: 0.92
SOURCE PAGE: 3
SOURCE QUOTE: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."

# 2. FULL TIMELINE

ORDER: UNCERTAIN (source extraction order 1)
EVENT TYPE: other
DESCRIPTION: A 55-year-old woman presented with night sweats, cough, and hemoptysis.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.9
SOURCE PAGE: 1
SOURCE QUOTE: "A 55-year-old woman presented with night sweats, cough, and hemoptysis."

ORDER: UNCERTAIN (source extraction order 2)
EVENT TYPE: other
DESCRIPTION: Chest x-ray showed a well-defined round opacity in the left lower lobe; it was not seen on a previous chest x-ray and was considered suspicious for malignancy.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.9
SOURCE PAGE: 1
SOURCE QUOTE: "While the complete blood count was normal, the chest x-ray showed a well deﬁned round opacity in the left lower lobe (Fig. 1). This was not seen on a previous chest x-ray and was considered unlikely to represent tuberculosis, but highly suspicious for malignancy."

ORDER: RELATIVE (BEFORE): 10 days later
EVENT TYPE: other
DESCRIPTION: Chest CT identified a left lower lobe pulmonary nodule and smaller cavitary lesions in the bilateral upper lungs.
DATE: NONE
RELATIVE TIME: 10 days later
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1
SOURCE QUOTE: "Computed Tomography (CT) scan of the chest was performed 10 days later for further characterization. In addition to the left lower lobe pulmonary nodule, smaller cavitary lesions were seen in the bilateral upper lungs (Fig. 2)."

ORDER: UNCERTAIN (source extraction order 4)
EVENT TYPE: biopsy
DESCRIPTION: CT-guided biopsy of the left lower lobe nodule was performed and was positive for metastatic melanoma.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.9
SOURCE PAGE: 1
SOURCE QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."

ORDER: UNCERTAIN (source extraction order 5)
EVENT TYPE: diagnosis
DESCRIPTION: Metastatic melanoma was diagnosed; the patient had no history of melanoma and clinical examination did not reveal a primary lesion.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.85
SOURCE PAGE: 1, 1
SOURCE QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma." | "Patient had no history of melanoma and clinical examination did not reveal a primary lesion."

ORDER: RELATIVE (DURING): The time interval between the baseline CT and PET-CT was 43 days.
EVENT TYPE: tumor_progression
DESCRIPTION: At PET-CT, bilateral upper lobe cavitary lesions had increased in size and number and were markedly hypermetabolic (maximum SUV 15.2).
DATE: NONE
RELATIVE TIME: The time interval between the baseline CT and PET-CT was 43 days.
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: DURING
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1, 1
SOURCE QUOTE: "The time interval between the baseline CT and PET-CT was 43 days." | "On F-18 FDG PET-CT, bilateral upper lobe cavitary lesions had increased in size and number and were markedly hypermetabolic with maximum standardized uptake value (max SUV) of 15.2 (Fig. 3C and D)."

ORDER: RELATIVE (DURING): The time interval between the baseline CT and PET-CT was 43 days.
EVENT TYPE: tumor_regression
DESCRIPTION: The previously biopsied left lung nodule had decreased in size and showed minimal FDG uptake (maximum SUV 2.5).
DATE: NONE
RELATIVE TIME: The time interval between the baseline CT and PET-CT was 43 days.
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: DURING
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1, 1
SOURCE QUOTE: "The time interval between the baseline CT and PET-CT was 43 days." | "On the other hand, the previously biopsied left lung nodule has decreased in size and showed very minimal FDG uptake with max SUV of 2.5 (Fig. 3A and B)."

ORDER: UNCERTAIN (source extraction order 8)
EVENT TYPE: treatment
DESCRIPTION: The patient underwent immune therapy with ipilimumab and had a favorable initial response. Timing relative to the initially documented lesion regression is not explicitly stated.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: UNKNOWN
TEMPORAL CONFIDENCE: 0.4
SOURCE PAGE: 3
SOURCE QUOTE: "Our patient underwent immune therapy with ipilimumab with a favorable initial response."

ORDER: UNCERTAIN (source extraction order 9)
EVENT TYPE: metastasis
DESCRIPTION: Melanoma recurred with lung, brain, and spinal cord metastases and was resistant to ipilimumab.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: UNKNOWN
TEMPORAL CONFIDENCE: 0.55
SOURCE PAGE: 3
SOURCE QUOTE: "Unfortunately, as is common with this form of treatment, melanoma recurred with lung, brain, and spinal cord metastases, this time resistant to ipilimumab."

ORDER: RELATIVE (AFTER): throughout the 19 months that followed after initial diagnosis
EVENT TYPE: tumor_regression
DESCRIPTION: Despite recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months following initial diagnosis.
DATE: NONE
RELATIVE TIME: throughout the 19 months that followed after initial diagnosis
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: AFTER
TEMPORAL CONFIDENCE: 0.85
SOURCE PAGE: 3
SOURCE QUOTE: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."

# 3. OBSERVED FACTS

CLAIM: paper.title: Spontaneous regression of a metastatic melanoma pulmonary deposit following biopsy
PAGE: 1
QUOTE: "Spontaneous regression of a metastatic melanoma\npulmonary deposit following biopsy"
CONFIDENCE: 1.00

CLAIM: paper.authors: ['Fatemeh Behnia', 'Megan Zare', 'Saeed Elojeimy']
PAGE: 1
QUOTE: "Fatemeh Behnia MDa,*, Megan Zare MDa, Saeed Elojeimy MD, PhDb"
CONFIDENCE: 1.00

CLAIM: paper.year: 2018
PAGE: 1
QUOTE: "© 2018 the Authors. Published by Elsevier Inc. under copyright license from the University\nof Washington."
CONFIDENCE: 1.00

CLAIM: paper.journal: Radiology Case Reports
PAGE: 1
QUOTE: "R a d i o l o g y C a s e R e p o r t s 1 3 ( 2 0 1 8 ) 5 8 0 – 5 8 2"
CONFIDENCE: 1.00

CLAIM: paper.doi: 10.1016/j.radcr.2018.02.012
PAGE: 1
QUOTE: "https://doi.org/10.1016/j.radcr.2018.02.012"
CONFIDENCE: 1.00

CLAIM: paper.paper_type: PaperType.CASE_REPORT
PAGE: 1
QUOTE: "Case Report"
CONFIDENCE: 1.00

CLAIM: paper.case_existence: YES
PAGE: 1
QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."
CONFIDENCE: 0.99

CLAIM: paper.case_existence: YES
PAGE: 1
QUOTE: "On the other hand, the previously biopsied left lung nodule has decreased in size and showed very minimal FDG uptake with max SUV of 2.5 (Fig. 3A and B)."
CONFIDENCE: 0.99

CLAIM: case.age: 55
PAGE: 1
QUOTE: "A 55-year-old woman presented with night sweats, cough, and hemoptysis."
CONFIDENCE: 0.92

CLAIM: case.sex: woman
PAGE: 1
QUOTE: "A 55-year-old woman presented with night sweats, cough, and hemoptysis."
CONFIDENCE: 0.92

CLAIM: case.melanoma_subtype: metastatic melanoma
PAGE: 1
QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."
CONFIDENCE: 0.92

CLAIM: case.primary_site: No primary lesion identified on clinical examination
PAGE: 1
QUOTE: "Patient had no history of melanoma and clinical examination did not reveal a primary lesion."
CONFIDENCE: 0.92

CLAIM: case.metastatic_sites: ['lungs (left lower lobe and bilateral upper lungs)', 'left hilar node', 'brain', 'spinal cord']
PAGE: 1
QUOTE: "In addition to the left lower lobe pulmonary nodule, smaller cavitary lesions were seen in the bilateral upper lungs (Fig. 2)."
CONFIDENCE: 0.92

CLAIM: case.regression_confirmed_date: 43 days after the baseline CT
PAGE: 1
QUOTE: "The time interval between the baseline CT and PET-CT was 43 days."
CONFIDENCE: 0.92

CLAIM: case.regression_confirmed_date: 43 days after the baseline CT
PAGE: 1
QUOTE: "On the other hand, the previously biopsied left lung nodule has decreased in size and showed very minimal FDG uptake with max SUV of 2.5 (Fig. 3A and B)."
CONFIDENCE: 0.92

CLAIM: case.regression_type: spontaneous regression of a metastatic melanoma pulmonary deposit
PAGE: 1
QUOTE: "Spontaneous regression of a metastatic melanoma pulmonary deposit following biopsy"
CONFIDENCE: 0.92

CLAIM: case.preceding_events: ['CT-guided biopsy of the left lower lobe nodule']
PAGE: 1
QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."
CONFIDENCE: 0.92

CLAIM: event.description: A 55-year-old woman presented with night sweats, cough, and hemoptysis.
PAGE: 1
QUOTE: "A 55-year-old woman presented with night sweats, cough, and hemoptysis."
CONFIDENCE: 0.90

CLAIM: event.description: Chest x-ray showed a well-defined round opacity in the left lower lobe; it was not seen on a previous chest x-ray and was considered suspicious for malignancy.
PAGE: 1
QUOTE: "While the complete blood count was normal, the chest x-ray showed a well deﬁned round opacity in the left lower lobe (Fig. 1). This was not seen on a previous chest x-ray and was considered unlikely to represent tuberculosis, but highly suspicious for malignancy."
CONFIDENCE: 0.90

CLAIM: event.description: Chest CT identified a left lower lobe pulmonary nodule and smaller cavitary lesions in the bilateral upper lungs.
PAGE: 1
QUOTE: "Computed Tomography (CT) scan of the chest was performed 10 days later for further characterization. In addition to the left lower lobe pulmonary nodule, smaller cavitary lesions were seen in the bilateral upper lungs (Fig. 2)."
CONFIDENCE: 0.95

CLAIM: event.description: CT-guided biopsy of the left lower lobe nodule was performed and was positive for metastatic melanoma.
PAGE: 1
QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."
CONFIDENCE: 0.90

CLAIM: event.description: Metastatic melanoma was diagnosed; the patient had no history of melanoma and clinical examination did not reveal a primary lesion.
PAGE: 1
QUOTE: "A CT-guided biopsy of the left lower lobe nodule was positive for metastatic melanoma."
CONFIDENCE: 0.85

CLAIM: event.description: Metastatic melanoma was diagnosed; the patient had no history of melanoma and clinical examination did not reveal a primary lesion.
PAGE: 1
QUOTE: "Patient had no history of melanoma and clinical examination did not reveal a primary lesion."
CONFIDENCE: 0.85

CLAIM: event.description: At PET-CT, bilateral upper lobe cavitary lesions had increased in size and number and were markedly hypermetabolic (maximum SUV 15.2).
PAGE: 1
QUOTE: "The time interval between the baseline CT and PET-CT was 43 days."
CONFIDENCE: 0.95

CLAIM: event.description: At PET-CT, bilateral upper lobe cavitary lesions had increased in size and number and were markedly hypermetabolic (maximum SUV 15.2).
PAGE: 1
QUOTE: "On F-18 FDG PET-CT, bilateral upper lobe cavitary lesions had increased in size and number and were markedly hypermetabolic with maximum standardized uptake value (max SUV) of 15.2 (Fig. 3C and D)."
CONFIDENCE: 0.95

CLAIM: event.description: The previously biopsied left lung nodule had decreased in size and showed minimal FDG uptake (maximum SUV 2.5).
PAGE: 1
QUOTE: "The time interval between the baseline CT and PET-CT was 43 days."
CONFIDENCE: 0.95

CLAIM: event.description: The previously biopsied left lung nodule had decreased in size and showed minimal FDG uptake (maximum SUV 2.5).
PAGE: 1
QUOTE: "On the other hand, the previously biopsied left lung nodule has decreased in size and showed very minimal FDG uptake with max SUV of 2.5 (Fig. 3A and B)."
CONFIDENCE: 0.95

CLAIM: paper.case_existence: YES
PAGE: 2
QUOTE: "The left lower lobe nodule (A) has decreased to 17 × 14 mm in size."
CONFIDENCE: 0.99

CLAIM: case.metastatic_sites: ['lungs (left lower lobe and bilateral upper lungs)', 'left hilar node', 'brain', 'spinal cord']
PAGE: 2
QUOTE: "Note left hilar nodal spread (arrowhead)."
CONFIDENCE: 0.92

CLAIM: case.partial_or_complete: partial
PAGE: 2
QUOTE: "The left lower lobe nodule (A) has decreased to 17 × 14 mm in size."
CONFIDENCE: 0.92

CLAIM: paper.case_existence: YES
PAGE: 3
QUOTE: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."
CONFIDENCE: 0.99

CLAIM: case.metastatic_sites: ['lungs (left lower lobe and bilateral upper lungs)', 'left hilar node', 'brain', 'spinal cord']
PAGE: 3
QUOTE: "Unfortunately, as is common with this form of treatment, melanoma recurred with lung, brain, and spinal cord metastases, this time resistant to ipilimumab."
CONFIDENCE: 0.92

CLAIM: case.outcome: Melanoma recurred with lung, brain, and spinal cord metastases resistant to ipilimumab; the biopsied lesion continued to decrease in size.
PAGE: 3
QUOTE: "Unfortunately, as is common with this form of treatment, melanoma recurred with lung, brain, and spinal cord metastases, this time resistant to ipilimumab."
CONFIDENCE: 0.92

CLAIM: case.outcome: Melanoma recurred with lung, brain, and spinal cord metastases resistant to ipilimumab; the biopsied lesion continued to decrease in size.
PAGE: 3
QUOTE: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."
CONFIDENCE: 0.92

CLAIM: case.follow_up_duration: 19 months that followed after initial diagnosis
PAGE: 3
QUOTE: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."
CONFIDENCE: 0.92

CLAIM: event.description: The patient underwent immune therapy with ipilimumab and had a favorable initial response. Timing relative to the initially documented lesion regression is not explicitly stated.
PAGE: 3
QUOTE: "Our patient underwent immune therapy with ipilimumab with a favorable initial response."
CONFIDENCE: 0.40

CLAIM: event.description: Melanoma recurred with lung, brain, and spinal cord metastases and was resistant to ipilimumab.
PAGE: 3
QUOTE: "Unfortunately, as is common with this form of treatment, melanoma recurred with lung, brain, and spinal cord metastases, this time resistant to ipilimumab."
CONFIDENCE: 0.55

CLAIM: event.description: Despite recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months following initial diagnosis.
PAGE: 3
QUOTE: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."
CONFIDENCE: 0.85

# 4. AUTHOR INTERPRETATIONS

CLAIM: paper.abstract: Spontaneous complete and partial regression of metastatic melanoma is poorly under-
stood, and is a rare phenomenon with less than 80 cases reported since 1866. Several
correlations have been noted such as systemic or local infections, operative trauma, hor-
monal inﬂuences, nutrition and immunologic factors. We present FDG PET and CT ﬁndings
in a patient with multiple pulmonary metastases of melanoma, one of which underwent
regression following biopsy. We suggest immune system modulation, triggered by biopsy,
could have played a role, although the precise mechanism remains unknown.
PAGE: 1
QUOTE: "Spontaneous complete and partial regression of metastatic melanoma is poorly under-\nstood, and is a rare phenomenon with less than 80 cases reported since 1866. Several\ncorrelations have been noted such as systemic or local infections, operative trauma, hor-\nmonal inﬂuences, nutrition and immunologic factors. We present FDG PET and CT ﬁndings\nin a patient with multiple pulmonary metastases of melanoma, one of which underwent\nregression following biopsy. We suggest immune system modulation, triggered by biopsy,\ncould have played a role, although the precise mechanism remains unknown."
CONFIDENCE: 1.00

CLAIM: case.partial_or_complete: partial
PAGE: 2
QUOTE: "Spontaneous regression is, by definition, disappearance of a tumor (complete regression) or decrease in size of a tumor (partial regression) in the absence of treatment."
CONFIDENCE: 0.92

# 5. UNCERTAIN / NOT_REPORTED

FIELD: stage
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: diagnosis_date
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: regression_start_date
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: treatment_before_regression
VALUE: "ipilimumab; timing relative to the initially documented regression is not explicitly stated"
STATUS: UNCERTAIN

FIELD: treatment_status
VALUE: "unknown"
STATUS: UNCERTAIN

EVENT: other — A 55-year-old woman presented with night sweats, cough, and hemoptysis.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: other — Chest x-ray showed a well-defined round opacity in the left lower lobe; it was not seen on a previous chest x-ray and was considered suspicious for malignancy.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: other — Chest CT identified a left lower lobe pulmonary nodule and smaller cavitary lesions in the bilateral upper lungs.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: 10 days later
RELATION TO REGRESSION: BEFORE

EVENT: biopsy — CT-guided biopsy of the left lower lobe nodule was performed and was positive for metastatic melanoma.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: diagnosis — Metastatic melanoma was diagnosed; the patient had no history of melanoma and clinical examination did not reveal a primary lesion.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: tumor_progression — At PET-CT, bilateral upper lobe cavitary lesions had increased in size and number and were markedly hypermetabolic (maximum SUV 15.2).
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: The time interval between the baseline CT and PET-CT was 43 days.
RELATION TO REGRESSION: DURING

EVENT: tumor_regression — The previously biopsied left lung nodule had decreased in size and showed minimal FDG uptake (maximum SUV 2.5).
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: The time interval between the baseline CT and PET-CT was 43 days.
RELATION TO REGRESSION: DURING

EVENT: treatment — The patient underwent immune therapy with ipilimumab and had a favorable initial response. Timing relative to the initially documented lesion regression is not explicitly stated.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: UNKNOWN

EVENT: metastasis — Melanoma recurred with lung, brain, and spinal cord metastases and was resistant to ipilimumab.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: UNKNOWN

EVENT: tumor_regression — Despite recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months following initial diagnosis.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: throughout the 19 months that followed after initial diagnosis
RELATION TO REGRESSION: AFTER

# 6. POSSIBLE MISSED INFORMATION

REVIEW_REQUIRED: YES
CODE: REVIEW_REQUIRED_EXPLICIT_STATEMENT_FOR_NOT_REPORTED
TARGET: regression_start_date
SOURCE PAGE: 3
SOURCE TEXT: "Interestingly, despite the recurrence of disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis."
REASON: Source text in Discussion matches a field-specific cue, but the extracted field is NOT_REPORTED.

# 7. FINAL SUMMARY

Confirmed fields: 11
Uncertain fields: 2
Not reported fields: 3
Timeline events: 10
Observed facts: 38
Author interpretations: 2
Review-required items: 1
