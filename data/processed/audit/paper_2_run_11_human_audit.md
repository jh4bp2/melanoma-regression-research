# 1. CORE CASE FIELDS

FIELD: age
VALUE: 83
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1
SOURCE QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."

FIELD: sex
VALUE: "male"
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1
SOURCE QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."

FIELD: melanoma_subtype
VALUE: "pulmonary metastatic melanoma"
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1
SOURCE QUOTE: "The final diagnosis was spontaneous regression of pulmonary metastatic melanoma confirmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."

FIELD: primary_site
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: stage
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: metastatic_sites
VALUE: ["left upper lobe lingula segment lung nodule"]
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1, 1
SOURCE QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy." | "No cutaneous melanoma or other sites of metastasis were identified."

FIELD: diagnosis_date
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: regression_start_date
VALUE: NONE
STATUS: UNCERTAIN
CONFIDENCE: N/A field-level; case candidate=0.96
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: regression_confirmed_date
VALUE: "8 months after initial diagnosis"
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1, 1
SOURCE QUOTE: "Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis." | "Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."

FIELD: regression_type
VALUE: "spontaneous regression of pulmonary metastatic melanoma"
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1
SOURCE QUOTE: "The final diagnosis was spontaneous regression of pulmonary metastatic melanoma confirmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."

FIELD: partial_or_complete
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: treatment_before_regression
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: treatment_status
VALUE: NONE
STATUS: UNCERTAIN
CONFIDENCE: N/A field-level; case candidate=0.96
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

FIELD: preceding_event
VALUE: ["Computed-tomography-guided biopsy of the lung nodule demonstrated malignant melanoma.", "Serial PET/CT scans were performed at 3 and 6 months; at 6 months the nodule SUV had reduced to 0.9."]
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1, 1
SOURCE QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)." | "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which confirmed no progression of disease, but the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months (Fig. 2B)."

FIELD: outcome
VALUE: "The left upper lobe nodule was completely resected with no new pulmonary nodules on postoperative CT chest."
STATUS: REPORTED
CONFIDENCE: 0.96
SOURCE PAGE: 1
SOURCE QUOTE: "Post-operative CT chest confirmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."

FIELD: follow_up_duration
VALUE: NONE
STATUS: NOT_REPORTED
CONFIDENCE: N/A
SOURCE PAGE: NONE — NO VERIFIED EVIDENCE LINK
SOURCE QUOTE: NONE — NO VERIFIED EVIDENCE LINK

# 2. FULL TIMELINE

ORDER: UNCERTAIN (source extraction order 1)
EVENT TYPE: other
DESCRIPTION: An incidental 15 mm left upper lobe lingula segment lung nodule was found during investigation of peripheral neuropathy.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.9
SOURCE PAGE: 1
SOURCE QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."

ORDER: UNCERTAIN (source extraction order 2)
EVENT TYPE: biopsy
DESCRIPTION: Computed-tomography-guided biopsy of the lung lesion demonstrated malignant melanoma, with S-100 and Melan-A positivity on immunohistochemistry.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1
SOURCE QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)."

ORDER: UNCERTAIN (source extraction order 3)
EVENT TYPE: diagnosis
DESCRIPTION: Malignant melanoma was diagnosed on computed-tomography-guided biopsy.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1
SOURCE QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)."

ORDER: UNCERTAIN (source extraction order 4)
EVENT TYPE: other
DESCRIPTION: Initial FDG PET/CT showed increased uptake in the left upper lobe lesion (SUV 3.4) and mild uptake in small hilar and mediastinal lymph nodes.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.9
SOURCE PAGE: 1
SOURCE QUOTE: "The initial FDG (ﬂuorodeoxyglucose) positron emission tomography/computed tomography (PET/CT) scan (Fig. 2A) showed increased uptake in the left upper lobe lesion with an SUV of 3.4, and mild uptake in the small hilar and mediastinal lymph nodes."

ORDER: UNCERTAIN (source extraction order 5)
EVENT TYPE: other
DESCRIPTION: Bronchoscopy found no endobronchial lesions, and endobronchial ultrasound-guided fine-needle aspiration of mediastinal nodes showed no malignant cells.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.8
SOURCE PAGE: 1, 1
SOURCE QUOTE: "No endobronchial lesions were seen on bronchoscopy." | "Endobronchial ultrasound-guided ﬁne-needle aspiration of the mediastinal nodes showed no malignant cells."

ORDER: UNCERTAIN (source extraction order 6)
EVENT TYPE: other
DESCRIPTION: No cutaneous melanoma or other sites of metastasis were identified.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: BEFORE
TEMPORAL CONFIDENCE: 0.8
SOURCE PAGE: 1
SOURCE QUOTE: "No cutaneous melanoma or other sites of metastasis were identified."

ORDER: RELATIVE (DURING): at 3 and 6 months
EVENT TYPE: other
DESCRIPTION: Serial PET/CT scans were performed as part of treatment-planning workup and confirmed no disease progression.
DATE: NONE
RELATIVE TIME: at 3 and 6 months
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: DURING
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1
SOURCE QUOTE: "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which conﬁrmed no progression of disease, but the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months (Fig. 2B)."

ORDER: RELATIVE (DURING): at 6 months
EVENT TYPE: tumor_regression
DESCRIPTION: The left upper lobe nodule SUV had reduced to 0.9 on PET/CT.
DATE: NONE
RELATIVE TIME: at 6 months
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: DURING
TEMPORAL CONFIDENCE: 0.98
SOURCE PAGE: 1
SOURCE QUOTE: "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which conﬁrmed no progression of disease, but the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months (Fig. 2B)."

ORDER: RELATIVE (AFTER): 8 months after initial diagnosis
EVENT TYPE: surgery
DESCRIPTION: Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed.
DATE: NONE
RELATIVE TIME: 8 months after initial diagnosis
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: AFTER
TEMPORAL CONFIDENCE: 0.99
SOURCE PAGE: 1
SOURCE QUOTE: "Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis."

ORDER: RELATIVE (AFTER): 8 months after initial diagnosis
EVENT TYPE: tumor_regression
DESCRIPTION: Histopathology of the resected nodule showed completely infarcted and necrotic ghost outlines of cells with no viable cells present.
DATE: NONE
RELATIVE TIME: 8 months after initial diagnosis
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: AFTER
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1
SOURCE QUOTE: "Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."

ORDER: UNCERTAIN (source extraction order 11)
EVENT TYPE: diagnosis
DESCRIPTION: The final diagnosis was spontaneous regression of pulmonary metastatic melanoma, confirmed on histopathology and accompanied by reduced FDG activity on serial PET scan.
DATE: NONE
RELATIVE TIME: NONE
DATE PRECISION: UNKNOWN
RELATION TO REGRESSION: DURING
TEMPORAL CONFIDENCE: 0.95
SOURCE PAGE: 1
SOURCE QUOTE: "The ﬁnal diagnosis was spontaneous regression of pulmonary metastatic melanoma conﬁrmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."

ORDER: RELATIVE (AFTER): Post-operative
EVENT TYPE: other
DESCRIPTION: Post-operative CT chest confirmed complete resection of the left upper lobe nodule and no new pulmonary nodules.
DATE: NONE
RELATIVE TIME: Post-operative
DATE PRECISION: RELATIVE
RELATION TO REGRESSION: AFTER
TEMPORAL CONFIDENCE: 0.99
SOURCE PAGE: 1
SOURCE QUOTE: "Post-operative CT chest conﬁrmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."

# 3. OBSERVED FACTS

CLAIM: paper.title: Spontaneous regression of pulmonary metastatic melanoma
PAGE: 1
QUOTE: "Spontaneous regression of pulmonary\nmetastatic melanoma"
CONFIDENCE: 1.00

CLAIM: paper.authors: ['Sook Fen Ong', 'Michael Harden', 'Shabnam Irandoust', 'Richard Wai Wing Lee']
PAGE: 1
QUOTE: "Sook Fen Ong1, Michael Harden2, Shabnam Irandoust3 & Richard Wai Wing Lee1"
CONFIDENCE: 1.00

CLAIM: paper.year: 2016
PAGE: 1
QUOTE: "Respirology Case Reports 2016; 4(1):\n7–9"
CONFIDENCE: 1.00

CLAIM: paper.journal: Respirology Case Reports
PAGE: 1
QUOTE: "Respirology Case Reports 2016; 4(1):\n7–9"
CONFIDENCE: 1.00

CLAIM: paper.doi: 10.1002/rcr2.138
PAGE: 1
QUOTE: "doi: 10.1002/rcr2.138"
CONFIDENCE: 1.00

CLAIM: paper.case_existence: YES
PAGE: 1
QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."
CONFIDENCE: 0.99

CLAIM: paper.case_existence: YES
PAGE: 1
QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)."
CONFIDENCE: 0.99

CLAIM: paper.case_existence: YES
PAGE: 1
QUOTE: "Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."
CONFIDENCE: 0.99

CLAIM: paper.case_existence: YES
PAGE: 1
QUOTE: "The final diagnosis was spontaneous regression of pulmonary metastatic melanoma confirmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."
CONFIDENCE: 0.99

CLAIM: case.age: 83
PAGE: 1
QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."
CONFIDENCE: 0.96

CLAIM: case.sex: male
PAGE: 1
QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."
CONFIDENCE: 0.96

CLAIM: case.melanoma_subtype: pulmonary metastatic melanoma
PAGE: 1
QUOTE: "The final diagnosis was spontaneous regression of pulmonary metastatic melanoma confirmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."
CONFIDENCE: 0.96

CLAIM: case.metastatic_sites: ['left upper lobe lingula segment lung nodule']
PAGE: 1
QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."
CONFIDENCE: 0.96

CLAIM: case.metastatic_sites: ['left upper lobe lingula segment lung nodule']
PAGE: 1
QUOTE: "No cutaneous melanoma or other sites of metastasis were identified."
CONFIDENCE: 0.96

CLAIM: case.regression_confirmed_date: 8 months after initial diagnosis
PAGE: 1
QUOTE: "Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis."
CONFIDENCE: 0.96

CLAIM: case.regression_confirmed_date: 8 months after initial diagnosis
PAGE: 1
QUOTE: "Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."
CONFIDENCE: 0.96

CLAIM: case.regression_type: spontaneous regression of pulmonary metastatic melanoma
PAGE: 1
QUOTE: "The final diagnosis was spontaneous regression of pulmonary metastatic melanoma confirmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."
CONFIDENCE: 0.96

CLAIM: case.preceding_events: ['Computed-tomography-guided biopsy of the lung nodule demonstrated malignant melanoma.', 'Serial PET/CT scans were performed at 3 and 6 months; at 6 months the nodule SUV had reduced to 0.9.']
PAGE: 1
QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)."
CONFIDENCE: 0.96

CLAIM: case.preceding_events: ['Computed-tomography-guided biopsy of the lung nodule demonstrated malignant melanoma.', 'Serial PET/CT scans were performed at 3 and 6 months; at 6 months the nodule SUV had reduced to 0.9.']
PAGE: 1
QUOTE: "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which confirmed no progression of disease, but the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months (Fig. 2B)."
CONFIDENCE: 0.96

CLAIM: case.outcome: The left upper lobe nodule was completely resected with no new pulmonary nodules on postoperative CT chest.
PAGE: 1
QUOTE: "Post-operative CT chest confirmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
CONFIDENCE: 0.96

CLAIM: event.description: An incidental 15 mm left upper lobe lingula segment lung nodule was found during investigation of peripheral neuropathy.
PAGE: 1
QUOTE: "A healthy 83-year-old male, a lifelong non-smoker, was found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."
CONFIDENCE: 0.90

CLAIM: event.description: Computed-tomography-guided biopsy of the lung lesion demonstrated malignant melanoma, with S-100 and Melan-A positivity on immunohistochemistry.
PAGE: 1
QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)."
CONFIDENCE: 0.95

CLAIM: event.description: Malignant melanoma was diagnosed on computed-tomography-guided biopsy.
PAGE: 1
QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma, immunohistochemistry was positive for S-100 and Melan-A (Fig. 1A)."
CONFIDENCE: 0.95

CLAIM: event.description: Initial FDG PET/CT showed increased uptake in the left upper lobe lesion (SUV 3.4) and mild uptake in small hilar and mediastinal lymph nodes.
PAGE: 1
QUOTE: "The initial FDG (ﬂuorodeoxyglucose) positron emission tomography/computed tomography (PET/CT) scan (Fig. 2A) showed increased uptake in the left upper lobe lesion with an SUV of 3.4, and mild uptake in the small hilar and mediastinal lymph nodes."
CONFIDENCE: 0.90

CLAIM: event.description: Bronchoscopy found no endobronchial lesions, and endobronchial ultrasound-guided fine-needle aspiration of mediastinal nodes showed no malignant cells.
PAGE: 1
QUOTE: "No endobronchial lesions were seen on bronchoscopy."
CONFIDENCE: 0.80

CLAIM: event.description: Bronchoscopy found no endobronchial lesions, and endobronchial ultrasound-guided fine-needle aspiration of mediastinal nodes showed no malignant cells.
PAGE: 1
QUOTE: "Endobronchial ultrasound-guided ﬁne-needle aspiration of the mediastinal nodes showed no malignant cells."
CONFIDENCE: 0.80

CLAIM: event.description: No cutaneous melanoma or other sites of metastasis were identified.
PAGE: 1
QUOTE: "No cutaneous melanoma or other sites of metastasis were identified."
CONFIDENCE: 0.80

CLAIM: event.description: Serial PET/CT scans were performed as part of treatment-planning workup and confirmed no disease progression.
PAGE: 1
QUOTE: "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which conﬁrmed no progression of disease, but the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months (Fig. 2B)."
CONFIDENCE: 0.95

CLAIM: event.description: The left upper lobe nodule SUV had reduced to 0.9 on PET/CT.
PAGE: 1
QUOTE: "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which conﬁrmed no progression of disease, but the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months (Fig. 2B)."
CONFIDENCE: 0.98

CLAIM: event.description: Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed.
PAGE: 1
QUOTE: "Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis."
CONFIDENCE: 0.99

CLAIM: event.description: Histopathology of the resected nodule showed completely infarcted and necrotic ghost outlines of cells with no viable cells present.
PAGE: 1
QUOTE: "Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."
CONFIDENCE: 0.95

CLAIM: event.description: The final diagnosis was spontaneous regression of pulmonary metastatic melanoma, confirmed on histopathology and accompanied by reduced FDG activity on serial PET scan.
PAGE: 1
QUOTE: "The ﬁnal diagnosis was spontaneous regression of pulmonary metastatic melanoma conﬁrmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."
CONFIDENCE: 0.95

CLAIM: event.description: Post-operative CT chest confirmed complete resection of the left upper lobe nodule and no new pulmonary nodules.
PAGE: 1
QUOTE: "Post-operative CT chest conﬁrmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."
CONFIDENCE: 0.99

# 4. AUTHOR INTERPRETATIONS

CLAIM: paper.abstract: Spontaneous regression of metastatic melanoma is a rare event with only 76 cases
having been reported since 1866. The precise mechanism of regression remains
unknown. We present a case of a man with spontaneous regression of pulmonary
metastatic melanoma conﬁrmed on histopathology accompanied by reduction in
ﬂuorodeoxyglucose-activity on serial positron emission tomography/computed
tomography scan.
PAGE: 1
QUOTE: "Spontaneous regression of metastatic melanoma is a rare event with only 76 cases\nhaving been reported since 1866. The precise mechanism of regression remains\nunknown. We present a case of a man with spontaneous regression of pulmonary\nmetastatic melanoma conﬁrmed on histopathology accompanied by reduction in\nﬂuorodeoxyglucose-activity on serial positron emission tomography/computed\ntomography scan."
CONFIDENCE: 1.00

CLAIM: paper.paper_type: PaperType.CASE_REPORT
PAGE: 3
QUOTE: "To our knowledge, this is the only case report of sponta-\nneous regression of melanoma with evidence of serial\nreduction in FDG-avidity on PET/CT imaging, and con-\nﬁrmed on histopathology."
CONFIDENCE: 1.00

# 5. UNCERTAIN / NOT_REPORTED

FIELD: primary_site
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: stage
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: diagnosis_date
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: regression_start_date
VALUE: NONE
STATUS: UNCERTAIN

FIELD: partial_or_complete
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: treatment_before_regression
VALUE: NONE
STATUS: NOT_REPORTED

FIELD: treatment_status
VALUE: NONE
STATUS: UNCERTAIN

FIELD: follow_up_duration
VALUE: NONE
STATUS: NOT_REPORTED

EVENT: other — An incidental 15 mm left upper lobe lingula segment lung nodule was found during investigation of peripheral neuropathy.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: biopsy — Computed-tomography-guided biopsy of the lung lesion demonstrated malignant melanoma, with S-100 and Melan-A positivity on immunohistochemistry.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: diagnosis — Malignant melanoma was diagnosed on computed-tomography-guided biopsy.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: other — Initial FDG PET/CT showed increased uptake in the left upper lobe lesion (SUV 3.4) and mild uptake in small hilar and mediastinal lymph nodes.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: other — Bronchoscopy found no endobronchial lesions, and endobronchial ultrasound-guided fine-needle aspiration of mediastinal nodes showed no malignant cells.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: other — No cutaneous melanoma or other sites of metastasis were identified.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: BEFORE

EVENT: other — Serial PET/CT scans were performed as part of treatment-planning workup and confirmed no disease progression.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: at 3 and 6 months
RELATION TO REGRESSION: DURING

EVENT: tumor_regression — The left upper lobe nodule SUV had reduced to 0.9 on PET/CT.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: at 6 months
RELATION TO REGRESSION: DURING

EVENT: diagnosis — The final diagnosis was spontaneous regression of pulmonary metastatic melanoma, confirmed on histopathology and accompanied by reduced FDG activity on serial PET scan.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: NONE
RELATION TO REGRESSION: DURING

EVENT: other — Post-operative CT chest confirmed complete resection of the left upper lobe nodule and no new pulmonary nodules.
STATUS: UNCERTAIN TEMPORAL ORDER
RELATIVE TIME: Post-operative
RELATION TO REGRESSION: AFTER

FIELD REVIEW: partial_or_complete
STATUS: NOT_REPORTED
SOURCE EVIDENCE LINK: NONE
JUDGMENT REASON: The paper does not explicitly label the case as 'complete regression'. It reports spontaneous regression and histopathology with completely infarcted cells/no viable cells. Mapping those observations to 'complete' would require a human classification decision, so run 11 retained NOT_REPORTED.
RELATED SOURCE PAGE: 1
RELATED SOURCE TEXT: "We present a case of a man with spontaneous regression of pulmonary metastatic melanoma conﬁrmed on histopathology accompanied by reduction in ﬂuorodeoxyglucose-activity on serial positron emission tomography/computed tomography scan."
RELATED SOURCE PAGE: 1
RELATED SOURCE TEXT: "2B).Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis.Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."
RELATED SOURCE PAGE: 1
RELATED SOURCE TEXT: "The ﬁnal diagnosis was spontaneous regression of pulmonary metastatic melanoma conﬁrmed on histopathology accompanied by reduction in FDG-activity on serial PET scan.s © 2015 The Authors."
RELATED SOURCE PAGE: 3
RELATED SOURCE TEXT: "To our knowledge, this is the only case report of spontaneous regression of melanoma with evidence of serial reduction in FDG-avidity on PET/CT imaging, and conﬁrmed on histopathology."
REVIEW_REQUIRED: YES

# 6. POSSIBLE MISSED INFORMATION

REVIEW_REQUIRED: YES
CODE: REVIEW_REQUIRED_EXPLICIT_STATEMENT_FOR_NOT_REPORTED
TARGET: primary_site
SOURCE PAGE: 1
SOURCE TEXT: "No cutaneous melanoma or other sites of metastasis were identiﬁed."
REASON: Source text in Case Report matches a field-specific cue, but the extracted field is NOT_REPORTED.

REVIEW_REQUIRED: YES
CODE: REVIEW_REQUIRED_EXPLICIT_STATEMENT_FOR_NOT_REPORTED
TARGET: partial_or_complete
SOURCE PAGE: 1
SOURCE TEXT: "2B).Video-assisted thoracoscopic surgery wedge resection of the left upper lobe lesion was performed 8 months after initial diagnosis.Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule with no viable cells present."
REASON: Source text in Case Report matches a field-specific cue, but the extracted field is NOT_REPORTED.

REVIEW_REQUIRED: YES
CODE: REVIEW_REQUIRED_REGRESSION_DESCRIPTION_NOT_LINKED
TARGET: regression
SOURCE PAGE: 1
SOURCE TEXT: "We present a case of a man with spontaneous regression of pulmonary metastatic melanoma conﬁrmed on histopathology accompanied by reduction in ﬂuorodeoxyglucose-activity on serial positron emission tomography/computed tomography scan."
REASON: Patient-specific regression cue in Abstract is not linked to a regression field or Event.

REVIEW_REQUIRED: YES
CODE: REVIEW_REQUIRED_REGRESSION_DESCRIPTION_NOT_LINKED
TARGET: regression
SOURCE PAGE: 2
SOURCE TEXT: "(B) Progress 6 month scan showing the lesion with a reduced SUV of 0.9."
REASON: Patient-specific regression cue in Discussion is not linked to a regression field or Event.

REVIEW_REQUIRED: YES
CODE: REVIEW_REQUIRED_REGRESSION_DESCRIPTION_NOT_LINKED
TARGET: regression
SOURCE PAGE: 3
SOURCE TEXT: "To our knowledge, this is the only case report of spontaneous regression of melanoma with evidence of serial reduction in FDG-avidity on PET/CT imaging, and conﬁrmed on histopathology."
REASON: Patient-specific regression cue in Discussion is not linked to a regression field or Event.

# 7. FINAL SUMMARY

Confirmed fields: 8
Uncertain fields: 2
Not reported fields: 6
Timeline events: 12
Observed facts: 33
Author interpretations: 2
Review-required items: 5
