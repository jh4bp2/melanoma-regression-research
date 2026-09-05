# PHASE 3 Biological Observation Audit

- RUN ID: 50
- CASE ID: 7
- SOURCE PHASE 2 RUN: 48
- STATUS: partial
- SCHEMA: phase3.2
- RULE: phase3.2-ontology-v1
- PROMPT: biological_observation_extraction:v3

## Biological Observations

### Observation 1

CATEGORY: GENETIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: DIRECT_MEASUREMENT
VARIABLE: BRAFV600 status
NORMALIZED VARIABLE: BRAF_V600_GENOTYPE
VALUE: wild-type
NORMALIZED VALUE: WILD_TYPE
UNIT: NONE
DIRECTION: UNKNOWN
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: wild-type
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Presentation
QUOTE: "BRAFV600 status was found to be wild-type."

### Observation 2

CATEGORY: GENETIC
OBSERVATION DOMAIN: BIOLOGICAL_STATE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: LAB_MEASUREMENT
VARIABLE: Cytogenetic del(5q) positivity
NORMALIZED VARIABLE: DEL_5Q_CYTOGENETIC_FINDING
VALUE: 5/20 cells positive for del(5q)
NORMALIZED VALUE: 5/20 cells positive for del(5q)
UNIT: cells
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: SYSTEMIC
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: cytogenetics
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: cytogenetics
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "His cytogenetics showed 5/20 cells positive for del(5q), consistent with myelodysplastic syndrome"

### Observation 3

CATEGORY: IMMUNE
OBSERVATION DOMAIN: BIOLOGICAL_STATE
DOMAIN SECONDARY: DIAGNOSTIC_EVIDENCE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: CD3+ and CD8+ T-cell infiltration
NORMALIZED VARIABLE: INTRATUMORAL_CD3_AND_CD8_T_CELL_INFILTRATION
VALUE: brisk infiltration with CD3+ and CD8+ T cells in both surgically resected in transit metastases
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: dual immunohistochemical staining of CD3 and CD8 with SOX10
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: MARKED
CONTEXT: dual immunohistochemical staining of CD3 and CD8 with SOX10
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "Dual immunohistochemical staining of CD3 and CD8 with the melanoma marker SOX10 demonstrated brisk infiltration with CD3+ and CD8+ T cells in both surgically resected in transit metastases"

### Observation 4

CATEGORY: INFLAMMATORY
OBSERVATION DOMAIN: CLINICAL_CONTEXT
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Lateral right popliteal nodule infection
NORMALIZED VARIABLE: INFECTION
VALUE: chronically infected
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: lateral right popliteal nodule
LESION ID: 16
LESION COLLECTION ID: NONE
TEMPORAL TEXT: chronically infected
REGRESSION ROLE: PROGRESSING_NON_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "A nodule in the lateral right popliteal area enlarged to a size of ca. 4 cm over a few weeks and became ulcerated and chronically infected."

### Observation 5

CATEGORY: INFLAMMATORY
OBSERVATION DOMAIN: CLINICAL_CONTEXT
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: CLINICAL_FINDING
VARIABLE: Postoperative wound complications
NORMALIZED VARIABLE: WOUND_DEHISCENCE_AND_INFECTION
VALUE: wound dehiscence and recurring infections requiring intense wound care
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: OTHER
LESION IDENTIFIER: resection site of lateral right popliteal nodule
LESION ID: 16
LESION COLLECTION ID: NONE
TEMPORAL TEXT: over a period of 3 months
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: HIGH
CONTEXT: postoperative course
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "The patient had a complicated postoperative course with wound dehiscence and recurring infections requiring intense wound care over a period of 3 months."

### Observation 6

CATEGORY: OTHER
OBSERVATION DOMAIN: BIOLOGICAL_STATE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: LAB_MEASUREMENT
VARIABLE: Hemoglobin
NORMALIZED VARIABLE: HEMOGLOBIN
VALUE: 6.7
NORMALIZED VALUE: 6.7
UNIT: g/dl
DIRECTION: UNKNOWN
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: SYSTEMIC
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: In April 2013
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: anemia requiring transfusions
LINKED EVENT ID: 241
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "In April 2013, he developed anemia with a hemoglobin of 6.7 g/dl requiring transfusions."

### Observation 7

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: IMAGING_PROXY
VARIABLE: PET/CT distribution of right lower-extremity lesions
NORMALIZED VARIABLE: CUTANEOUS_AND_SUBCUTANEOUS_MELANOMA_METASTASES
VALUE: a dominant soft tissue mass lateral to the right fibular head with numerous additional soft tissue nodules extending from the right mid thigh anteriorly to the level of the ankle, compatible with multiple cutaneous and subcutaneous melanoma metastases
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: PET/CT of the entire body
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: PET/CT of the entire body
LINKED EVENT ID: 239
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Presentation
QUOTE: "A PET/CT of the entire body demonstrated a dominant soft tissue mass lateral to the right fibular head with numerous additional soft tissue nodules extending from the right mid thigh anteriorly to the level of the ankle, compatible with multiple cutaneous and subcutaneous melanoma metastases (Fig. 1b)."

### Observation 8

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Right-leg lesion morphology and size
NORMALIZED VARIABLE: CUTANEOUS_LESION_SIZE
VALUE: purple, tender, 2.7 × 2.5 × 1.5 cm in size
NORMALIZED VALUE: [2.7, 2.5, 1.5]
UNIT: cm
DIRECTION: UNKNOWN
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: right-leg excisional-biopsy lesion
LESION ID: 15
LESION COLLECTION ID: NONE
TEMPORAL TEXT: purple, tender, 2.7 × 2.5 × 1.5 cm in size
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Presentation
QUOTE: "The lesion was described as purple, tender, 2.7 × 2.5 × 1.5 cm in size."

### Observation 9

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Accelerated right lower-extremity skin-nodule progression
NORMALIZED VARIABLE: CUTANEOUS_METASTASIS_PROGRESSION
VALUE: substantial increase in the size of pre-existent right lower extremity skin nodules as well as development of new nodules
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: INCREASED
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: By January 2014
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "By January 2014 accelerated progression of disease with substantial increase in the size of pre-existent right lower extremity skin nodules as well as development of new nodules was noted."

### Observation 10

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Further skin-metastasis growth and new lesions during postoperative course
NORMALIZED VARIABLE: CUTANEOUS_METASTASIS_PROGRESSION
VALUE: further growth of multiple skin metastases with emergence of new lesions both clinically and on restaging scans
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: INCREASED
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: During the protracted postoperative course
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: 250
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "During the protracted postoperative course there was further growth of multiple skin metastases with emergence of new lesions both clinically and on restaging scans while no distant metastases were evident."

### Observation 11

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Growth of right-leg cutaneous nodules
NORMALIZED VARIABLE: CUTANEOUS_NODULE_GROWTH
VALUE: growing in size over the preceding 3 years
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: INCREASED
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: over the preceding 3 years
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: 235
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Presentation
QUOTE: "The lesions had been growing in size over the preceding 3 years (Fig. 1a)."

### Observation 12

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Shrinkage of several skin nodules
NORMALIZED VARIABLE: CUTANEOUS_NODULE_SIZE
VALUE: shrinkage of several skin nodules
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: DECREASED
STATUS: REPORTED
TIME RELATION: DURING_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: By November 2014, almost 2 years after the first treatment with ipilimumab and 9 months after the first of 2 palliative resections
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: patient noted
LINKED EVENT ID: 252
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "By November 2014, almost 2 years after the first treatment with ipilimumab and 9 months after the first of 2 palliative resections, the patient noted shrinkage of several skin nodules."

### Observation 13

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: IMAGING_PROXY
VARIABLE: Distant metastatic disease
NORMALIZED VARIABLE: DISTANT_METASTASIS
VALUE: no evidence
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: PATIENT
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: PET/CT of the entire body
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: PET/CT of the entire body
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Presentation
QUOTE: "There was no evidence for distant metastatic disease."

EVIDENCE 2 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "During the protracted postoperative course there was further growth of multiple skin metastases with emergence of new lesions both clinically and on restaging scans while no distant metastases were evident."

### Observation 14

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: CLINICAL_FINDING
VARIABLE: Clinical status of non-resected in-transit metastases
NORMALIZED VARIABLE: IN_TRANSIT_METASTASIS_CLINICAL_PRESENCE
VALUE: all non-resected in transit metastases had completely disappeared clinically
NORMALIZED VALUE: complete disappearance
UNIT: NONE
DIRECTION: DECREASED
STATUS: REPORTED
TIME RELATION: DURING_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: By March 2015 (2 years after completion of ipilimumab)
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: clinical examination
LINKED EVENT ID: 254
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "By March 2015 (2 years after completion of ipilimumab) all non-resected in transit metastases had completely disappeared clinically;"

### Observation 15

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: CLINICAL_FINDING
VARIABLE: Clinical and radiographic status of in-transit metastases
NORMALIZED VARIABLE: IN_TRANSIT_METASTASIS_RESPONSE
VALUE: all in transit metastases had resolved both clinically and radiographically
NORMALIZED VALUE: complete clinical and radiographic response
UNIT: NONE
DIRECTION: DECREASED
STATUS: REPORTED
TIME RELATION: AT_CONFIRMATION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: By August 2016
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: clinical and radiographic assessment
LINKED EVENT ID: 256
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "By August 2016, all in transit metastases had resolved both clinically and radiographically and the patient remains in a complete clinical and radiographic response (Fig. 1c, d)."

### Observation 16

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: Excisional biopsy diagnosis
NORMALIZED VARIABLE: MELANOMA_DIAGNOSIS
VALUE: malignant melanoma with focal necrosis
NORMALIZED VALUE: malignant melanoma with focal necrosis
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: right-leg excisional-biopsy lesion
LESION ID: 15
LESION COLLECTION ID: NONE
TEMPORAL TEXT: In October of 2012
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 1
SECTION: Case Presentation
QUOTE: "In October of 2012 an 84-year-old man with a history of coronary artery disease, COPD, hypertension, and venous insufficiency presented with multiple cutaneous nodules on his right leg. The lesions had been growing in size over the preceding 3 years (Fig. 1a). An excisional biopsy was performed and revealed a malignant melanoma with focal necrosis."

### Observation 17

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Right lower-extremity metastasis progression
NORMALIZED VARIABLE: METASTATIC_LESION_PROGRESSION
VALUE: continued slow growth
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: INCREASED
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: RELATIVE
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: Between December 2012 and December 2013
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: 245
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "Between December 2012 and December 2013 there was continued slow growth of the right lower extremity metastases."

### Observation 18

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: CLINICAL_CONTEXT
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Lateral right popliteal nodule size and ulceration
NORMALIZED VARIABLE: POPLITEAL_METASTATIC_NODULE_MORPHOLOGY
VALUE: enlarged to a size of ca. 4 cm over a few weeks and became ulcerated
NORMALIZED VALUE: 4
UNIT: cm
DIRECTION: INCREASED
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: APPROXIMATE
SCOPE TYPE: LESION
LESION IDENTIFIER: lateral right popliteal nodule
LESION ID: 16
LESION COLLECTION ID: NONE
TEMPORAL TEXT: over a few weeks
REGRESSION ROLE: PROGRESSING_NON_TARGET
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: 247
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "A nodule in the lateral right popliteal area enlarged to a size of ca. 4 cm over a few weeks and became ulcerated and chronically infected."

### Observation 19

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DISEASE_PHENOTYPE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: MORPHOLOGIC_FINDING
VARIABLE: Radiographic lesion size response
NORMALIZED VARIABLE: RADIOGRAPHIC_LESION_SIZE
VALUE: continued mixed response with most lesions reduced in size
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: DECREASED
STATUS: REPORTED
TIME RELATION: DURING_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: in May 2015
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: radiographically
LINKED EVENT ID: 255
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "radiographically, in May 2015 there was a continued mixed response with most lesions reduced in size."

### Observation 20

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: IMAGING_PROXY
VARIABLE: Restaging PET/CT response
NORMALIZED VARIABLE: RADIOGRAPHIC_TUMOR_RESPONSE
VALUE: mixed response
NORMALIZED VALUE: mixed response
UNIT: NONE
DIRECTION: MIXED
STATUS: REPORTED
TIME RELATION: DURING_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: NONE
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: in December 2014
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: restaging PET/CT
LINKED EVENT ID: 253
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "A restaging PET/CT performed in December 2014 showed a mixed response."

### Observation 21

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: DIAGNOSTIC_EVIDENCE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: Necrosis in August 2014 resected metastasis
NORMALIZED VARIABLE: TUMOR_NECROSIS
VALUE: no necrosis was seen
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: ABSENT
STATUS: REPORTED_ABSENT
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: August 2014 resected right medial knee metastasis
LESION ID: 17
LESION COLLECTION ID: NONE
TEMPORAL TEXT: August 2014
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: UNKNOWN
CONTEXT: NONE
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "whereas no necrosis was seen in the metastasis that was removed in August 2014."

### Observation 22

CATEGORY: PATHOLOGIC
OBSERVATION DOMAIN: BIOLOGICAL_STATE
DOMAIN SECONDARY: NONE
MEASUREMENT SEMANTICS: PATHOLOGIC_FINDING
VARIABLE: Necrosis and viable tumor in February 2014 resected metastasis
NORMALIZED VARIABLE: TUMOR_NECROSIS_AND_VIABILITY
VALUE: highly necrotic with some areas of viable tumor as evident by SOX10 staining
NORMALIZED VALUE: NONE
UNIT: NONE
DIRECTION: PRESENT
STATUS: REPORTED
TIME RELATION: BEFORE_REGRESSION
TEMPORAL PRECISION: UNKNOWN
SCOPE TYPE: LESION
LESION IDENTIFIER: February 2014 resected in-transit metastasis
LESION ID: NONE
LESION COLLECTION ID: NONE
TEMPORAL TEXT: February 2014
REGRESSION ROLE: UNKNOWN
QUALITATIVE LEVEL: HIGH
CONTEXT: SOX10 staining
LINKED EVENT ID: NONE
CONFIDENCE: 1.00

EVIDENCE 1 TYPE: OBSERVED_FACT
PAGE: 2
SECTION: Case Presentation
QUOTE: "The metastasis which was resected in February 2014 was highly necrotic with some areas of viable tumor as evident by SOX10 staining"

## Rejected As Interpretation

### Rejected Interpretation 1

STATEMENT: An extensive work up including bone marrow biopsy suggested pure red cell aplasia, which is rare however has been previously described after treatment with CTLA-4 blockade [4], as the most likely etiology.
REASON: Contains the speculative term "suggested" and identifies a "most likely etiology" rather than a directly observed finding.
PAGE: 2
SECTION: Case Presentation
QUOTE: "An extensive work up including bone marrow biopsy suggested pure red cell aplasia, which is rare however has been previously described after treatment with CTLA-4 blockade [4], as the most likely etiology."

### Rejected Interpretation 2

STATEMENT: The exact cause of our patient’s sudden onset of tumor regression remains speculative. We hypothesize that the operative trauma followed by the postoperative infections augmented an innate immune response.
REASON: Explicitly speculative hypothesis of causation and mechanism.
PAGE: 1
SECTION: Abstract
QUOTE: "The exact cause of our patient’s sudden onset of tumor regression remains speculative. We hypothesize that the operative trauma followed by the postoperative infections augmented an innate immune response."

### Rejected Interpretation 3

STATEMENT: Although the exact cause of our patient’s sudden onset of tumor regression, eventually leading to disappearance of all clinically and radiographically evident tumors, remains speculative, an immune related mechanism seems most plausible.
REASON: Explicitly states that the cause remains speculative and proposes a plausible mechanism.
PAGE: 3
SECTION: Conclusion
QUOTE: "Although the exact cause of our patient’s sudden onset of tumor regression, eventually leading to disappearance of all clinically and radiographically evident tumors, remains speculative, an immune related mechanism seems most plausible."

### Rejected Interpretation 4

STATEMENT: For our patient, it is intriguing to speculate that his exposure to ipilimumab almost 2 years prior to the onset of tumor regression also contributed to the tumor response.
REASON: Explicit speculation that prior ipilimumab contributed to regression; not a directly reported treatment response.
PAGE: 3
SECTION: Conclusion
QUOTE: "For our patient, it is intriguing to speculate that his exposure to ipilimumab almost 2 years prior to the onset of tumor regression also contributed to the tumor response."

## Lesions

- skin lesion (UNK|SKIN|UNK|LESION|RESECTION|NONE|SINGLE)
  alias: right-leg excisional-biopsy lesion [CONFIRMED_ALIAS]
- right popliteal skin nodule (RIGHT|SKIN|POPLITEAL|NODULE|NONE|NONE|SINGLE)
  alias: lateral right popliteal nodule [CONFIRMED_ALIAS]
  alias: resection site of lateral right popliteal nodule [CONFIRMED_ALIAS]
- right medial knee skin metastasis (RIGHT|SKIN|MEDIAL_KNEE|METASTASIS|RESECTION|august_2014|SINGLE)
  alias: August 2014 resected right medial knee metastasis [CONFIRMED_ALIAS]

## Lesion Collections

None.


## Genotype Observations

- BRAF WILD_TYPE

## Explanatory Alternatives

- infection_or_surgery_immune_trigger [AUTHOR_SUGGESTED]: The exact cause of our patient’s sudden onset of tumor regression remains speculative. We hypothesize that the operative trauma followed by the postoperative infections augmented an innate immune response.
- delayed_immunotherapy_effect [AUTHOR_SUGGESTED]: For our patient, it is intriguing to speculate that his exposure to ipilimumab almost 2 years prior to the onset of tumor regression also contributed to the tumor response.

## Temporal Records

None.


## Summary

- OBSERVATIONS: 22
- VERIFIED EVIDENCE: 26
- REJECTED EVIDENCE: 4
- DUPLICATE MERGES: 0
- LESION ALIAS MERGES: 3
- UNRESOLVED LESION IDENTITIES: 0
- DUAL-DOMAIN IMMUNE: 1
- GENOTYPE RECORDS: 0
- UNCERTAIN: 0
- NOT REPORTED TARGETS: 36
