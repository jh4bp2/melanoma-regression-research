# PHASE 3 Biological Observation Audit

- RUN ID: 34
- CASE ID: 1
- SOURCE PHASE 2 RUN: 19
- STATUS: partial
- SCHEMA: phase3.1
- RULE: phase3.1-ontology-v4
- PROMPT: biological_observation_extraction:v2

## Biological Observations

### Observation 1

CATEGORY: METABOLIC
OBSERVATION DOMAIN: BIOLOGICAL_STATE
MEASUREMENT SEMANTICS: IMAGING_PROXY
VARIABLE: left upper lobe lesion FDG uptake standardized uptake value
NORMALIZED VARIABLE: FDG_PET_STANDARDIZED_UPTAKE_VALUE
VALUE: SUV 3.4 to 0.9 at 6 months
NORMALIZED VALUE: [3.4, 0.9]
UNIT: SUV
DIRECTION: DECREASED
STATUS: REPORTED
TIME RELATION: DURING_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Initial and serial FDG PET/CT imaging
LINKED EVENT ID: 137
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "The initial FDG (ﬂuorodeoxyglucose) positron emission tomography/computed tomography (PET/CT) scan (Fig. 2A) showed increased uptake in the left upper lobe lesion with an SUV of 3.4"

EVIDENCE 2 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "the left upper lobe nodule SUV (standardized uptake value) had reduced to 0.9 at 6 months"

EVIDENCE 3 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Discussion
QUOTE: "(A) Fluorodeoxyglucose positron emission tomography/computed tomography scan of left upper lobe lesion with standardized uptake value (SUV) of 3.4. (B) Progress 6 month scan showing the lesion with a reduced SUV of 0.9."

### Observation 2

CATEGORY: METABOLIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: IMAGING_PROXY
VARIABLE: hilar and mediastinal lymph node FDG uptake
NORMALIZED VARIABLE: FDG_UPTAKE
VALUE: mild uptake
NORMALIZED VALUE: mild
UNIT: NONE
DIRECTION: UNKNOWN
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LYMPH_NODE
LESION IDENTIFIER: hilar/mediastinal lymph nodes
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Initial FDG PET/CT
LINKED EVENT ID: 133
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "mild uptake in the small hilar and mediastinal lymph nodes."

### Observation 3

CATEGORY: OTHER
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
MEASUREMENT SEMANTICS: CLINICAL_FINDING
VARIABLE: cutaneous melanoma or other sites of metastasis
NORMALIZED VARIABLE: ADDITIONAL_MELANOMA_METASTATIC_SITES
VALUE: No cutaneous melanoma or other sites of metastasis were identified
NORMALIZED VALUE: absent
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: PATIENT
LESION IDENTIFIER: NONE
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Primary-site and metastatic-site investigation
LINKED EVENT ID: 136
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "No cutaneous melanoma or other sites of metastasis were identiﬁed."

### Observation 4

CATEGORY: OTHER
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: disease progression on serial PET/CT
NORMALIZED VARIABLE: DISEASE_PROGRESSION
VALUE: no progression of disease
NORMALIZED VALUE: absent
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: DURING_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: PATIENT
LESION IDENTIFIER: NONE
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Serial PET/CT scans at 3 and 6 months
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Serial PET/CT scans were performed at 3 and 6 months as part of the treatment planning workup, which conﬁrmed no progression of disease"

### Observation 5

CATEGORY: OTHER
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: CLINICAL_FINDING
VARIABLE: endobronchial lesions on bronchoscopy
NORMALIZED VARIABLE: ENDOBRONCHIAL_LESIONS
VALUE: no endobronchial lesions
NORMALIZED VALUE: absent
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: OTHER
LESION IDENTIFIER: NONE
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Bronchoscopy
LINKED EVENT ID: 134
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "No endobronchial lesions were seen on bronchoscopy."

### Observation 6

CATEGORY: OTHER
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: left upper lobe lingula segment lung nodule size
NORMALIZED VARIABLE: LUNG_NODULE_SIZE
VALUE: 15 mm
NORMALIZED VALUE: 15
UNIT: mm
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Incidental lung nodule
LINKED EVENT ID: 130
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "an incidental 15 mm left upper lobe lingula segment lung nodule"

### Observation 7

CATEGORY: OTHER
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: IMAGING_PROXY
VARIABLE: new pulmonary nodules on postoperative CT chest
NORMALIZED VARIABLE: NEW_PULMONARY_NODULES
VALUE: no new pulmonary nodules
NORMALIZED VALUE: absent
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: AFTER_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: PATIENT
LESION IDENTIFIER: NONE
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Post-operative CT chest
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Post-operative CT chest conﬁrmed the left upper lobe nodule had been completely resected with no new pulmonary nodules."

### Observation 8

CATEGORY: OTHER
OBSERVATION DOMAIN: CLINICAL_CONTEXT
MEASUREMENT SEMANTICS: SYMPTOM
VARIABLE: peripheral neuropathy
NORMALIZED VARIABLE: PERIPHERAL_NEUROPATHY
VALUE: peripheral neuropathy
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: UNKNOWN
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: PATIENT
LESION IDENTIFIER: NONE
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Investigation during which the lung nodule was found
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "found to have an incidental 15 mm left upper lobe lingula segment lung nodule as part of the investigation of peripheral neuropathy."

### Observation 9

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: computed-tomography-guided biopsy diagnosis
NORMALIZED VARIABLE: BIOPSY_DIAGNOSIS
VALUE: malignant melanoma
NORMALIZED VALUE: malignant melanoma
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Computed-tomography-guided biopsy
LINKED EVENT ID: 132
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Computed-tomography-guided biopsy demonstrated malignant melanoma"

### Observation 10

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: final diagnosis
NORMALIZED VARIABLE: DIAGNOSIS
VALUE: spontaneous regression of pulmonary metastatic melanoma
NORMALIZED VALUE: spontaneous regression of pulmonary metastatic melanoma
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: AT_CONFIRMATION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Confirmed on histopathology
LINKED EVENT ID: 142
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "The ﬁnal diagnosis was spontaneous regression of pulmonary metastatic melanoma conﬁrmed on histopathology accompanied by reduction in FDG-activity on serial PET scan."

### Observation 11

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: malignant cells in mediastinal node fine-needle aspiration
NORMALIZED VARIABLE: MALIGNANT_CELLS
VALUE: no malignant cells
NORMALIZED VALUE: absent
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LYMPH_NODE
LESION IDENTIFIER: mediastinal nodes
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Endobronchial ultrasound-guided fine-needle aspiration
LINKED EVENT ID: 135
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Endobronchial ultrasound-guided ﬁne-needle aspiration of the mediastinal nodes showed no malignant cells."

### Observation 12

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: melanin pigment within necrotic cells
NORMALIZED VARIABLE: MELANIN_PIGMENT
VALUE: present
NORMALIZED VALUE: present
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: AT_CONFIRMATION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Mason Fontana and Melanin bleach stains of surgical specimen
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Stains with Mason Fontana and Melanin bleach conﬁrmed the presence of melanin pigment within the necrotic cells"

### Observation 13

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: Melan-A immunohistochemistry
NORMALIZED VARIABLE: MELAN_A_IMMUNOHISTOCHEMISTRY
VALUE: positive
NORMALIZED VALUE: positive
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Computed-tomography-guided biopsy
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "immunohistochemistry was positive for S-100 and Melan-A"

### Observation 14

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: S-100 and Melan-A stains in resected nodule
NORMALIZED VARIABLE: S_100_AND_MELAN_A_STAINING
VALUE: negative
NORMALIZED VALUE: negative
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: AT_CONFIRMATION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Surgical pathology specimen
LINKED EVENT ID: 140
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Stains for S-100 and Melan-A were negative."

### Observation 15

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: S-100 immunohistochemistry
NORMALIZED VARIABLE: S_100_IMMUNOHISTOCHEMISTRY
VALUE: positive
NORMALIZED VALUE: positive
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Computed-tomography-guided biopsy
LINKED EVENT ID: 131
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "immunohistochemistry was positive for S-100 and Melan-A"

### Observation 16

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: BIOLOGICAL_STATE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: tumor infarction and necrosis
NORMALIZED VARIABLE: TUMOR_NECROSIS
VALUE: scattered completely infarcted and necrotic ghost outlines of cells
NORMALIZED VALUE: present
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: AT_CONFIRMATION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Histopathology of wedge resection specimen performed 8 months after initial diagnosis
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "Histopathology showed scattered completely infarcted and necrotic ghost outlines of cells seen within the nodule"

### Observation 17

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: BIOLOGICAL_STATE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: viable cells in resected nodule
NORMALIZED VARIABLE: VIABLE_TUMOR_CELLS
VALUE: no viable cells present
NORMALIZED VALUE: absent
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: AT_CONFIRMATION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: left upper lobe target lesion
REGRESSION ROLE: REGRESSING_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: Histopathology of wedge resection specimen performed 8 months after initial diagnosis
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Report
QUOTE: "with no viable cells present."

## Rejected As Interpretation

### Rejected Interpretation 1

STATEMENT: The mechanisms of spontaneous regression of melanoma are unknown. Possible etiologies have been postulated, including infection, operative trauma, hormonal inﬂuences or immunologic factors [1].
REASON: Author discussion of postulated mechanisms/etiologies, not a directly observed case finding.
PAGE: 2
SECTION: Discussion
QUOTE: "The mechanisms of spontaneous regression of melanoma are unknown. Possible etiologies have been postu- lated, including infection, operative trauma, hormonal inﬂuences or immunologic factors [1]."

### Rejected Interpretation 2

STATEMENT: It has been suggested that surgery and infection could be acting as mediating factors of regression by increasing the individual’s natural defenses against the tumor.
REASON: Suggested causal mechanism rather than an observed finding in this case.
PAGE: 2
SECTION: Discussion
QUOTE: "It has been sug- gested that surgery and infection could be acting as mediating factors of regression by increasing the individual’s natural defenses against the tumor."

### Rejected Interpretation 3

STATEMENT: Our case demonstrates a clear reduction in the SUV on serial imaging, which is in keeping with reduction in tumor metabolic activity, most likely through cell necrosis as seen in the resected specimen.
REASON: The SUV reduction and necrosis are extracted as observations; the asserted metabolic interpretation and likely linkage through necrosis are not directly observed mechanisms.
PAGE: 3
SECTION: Discussion
QUOTE: "Our case demonstrates a clear reduction in the SUV on serial imaging, which is in keeping with reduction in tumor metabolic activity, most likely through cell necrosis as seen in the resected specimen."

## Summary

- OBSERVATIONS: 17
- VERIFIED EVIDENCE: 21
- REJECTED EVIDENCE: 3
- DUPLICATE MERGES: 0
- UNCERTAIN: 0
- NOT REPORTED TARGETS: 36
