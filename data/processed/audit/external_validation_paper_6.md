# External Validation Audit

- Paper ID: 6
- Title: Complete spontaneous regression of a metastatic acral melanoma with associated leukoderma
- DOI / PMID: 10.1016/j.jdcr.2017.07.001 / 29264383
- PHASE 2 run: 53 (phase2.2.2 / phase2.2-adjudication-v4)
- PHASE 3 runs: 54 case 9
- Stable versions: schema phase2.2.2 / rule phase2.2-adjudication-v4; schema phase3.2 / rule phase3.2-ontology-v1 / prompt biological_observation_extraction:v3
- Validation-set rule: record mismatches without adapting ontology, schema, rule, or prompts. Selection rationale is research metadata only and was not preloaded into Case / Evidence / BiologicalObservation.
- PHASE 4 / Pattern Discovery / Public Hypothesis / Evidence Graph were not started.

# Case Summary — Case 9

- Case ID: 9
- Patient identifier: paper-6-case-1
- Age / sex: 56 / female
- Melanoma subtype: acral melanoma (AM)
- Primary site: right heel
- Stage: stage IV disease
- Metastatic sites: right thigh (in-transit metastasis); right common iliac lymph nodes; right external iliac lymph nodes; right inguinal lymph nodes
- First observed reduction: NOT STORED
- Regression confirmation: NOT STORED
- Regression extent: COMPLETE
- Treatment before regression: No medical attention for the heel nodule
- Preceding events: NOT STORED
- Outcome: Alive; pain was well controlled

## Case Field Statuses

- patient_identifier: NOT_REPORTED | raw value: None
- age: REPORTED | raw value: 56
- sex: REPORTED | raw value: female
- melanoma_subtype: REPORTED | raw value: acral melanoma (AM)
- primary_site: REPORTED | raw value: right heel
- stage: REPORTED | raw value: stage IV disease
- metastatic_sites: REPORTED | raw value: ['right thigh (in-transit metastasis)', 'right common iliac lymph nodes', 'right external iliac lymph nodes', 'right inguinal lymph nodes']
- diagnosis_date: NOT_REPORTED | raw value: None
- regression_start_date: NOT_REPORTED | raw value: None
- first_observed_reduction: NOT_REPORTED | raw value: None
- regression_confirmed_date: NOT_REPORTED | raw value: None
- regression_duration: NOT_REPORTED | raw value: None
- regression_type: REPORTED | raw value: complete spontaneous regression
- regression_extent_clinical: REPORTED | raw value: COMPLETE
- viable_tumor_at_pathology: REPORTED | raw value: ABSENT
- treatment_before_regression: REPORTED | raw value: No medical attention for the heel nodule
- treatment_status: REPORTED | raw value: no_treatment
- preceding_events: NOT_REPORTED | raw value: None
- outcome: REPORTED | raw value: Alive; pain was well controlled
- follow_up_duration: REPORTED | raw value: 3 months after presentation

# Timeline

## Event 286: other
- Description: The patient reported that the right heel nodule had been present for 2 years, grew rapidly initially, and then stabilized in size.
- Event date: NONE
- Relative time: 2 years before presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1413: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "According to the patient, the heel nodule had been present for 2 years, growing rapidly at first and then stabilizing in size."

## Event 287: tumor_progression
- Description: A progressively enlarging tumor developed on the medial right thigh over 6 months.
- Event date: NONE
- Relative time: 6-month history before presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1414: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "A 56-year-old African woman with Fitzpatrick skin phototype VI presented with a 6-month history of a progressively enlarging tumor on the medial aspect of her right thigh."

## Event 288: other
- Description: At presentation, the patient reported significant weight loss, fatigue, and right leg pain.
- Event date: NONE
- Relative time: At presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1415: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "She reported signiﬁcant weight loss, fatigue, and right leg pain."

## Event 289: other
- Description: At presentation, examination found a 20 × 18 cm fungating medial right-thigh tumor with tissue sloughing and foul-smelling discharge, with associated right inguinal lymphadenopathy.
- Event date: NONE
- Relative time: Upon examination at presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1416: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Upon examination, she appeared cachectic and had a 20 3 18 cm fungating tumor on the medial aspect of her right thigh with tissue sloughing and foul-smelling discharge (Fig 1, A). There was associated right inguinal lymphadenopathy."

## Event 290: other
- Description: Examination identified a 5 × 5 cm grey/brown nodule on the right heel and a leukoderma patch on the medial right ankle; the leukoderma had follicular repigmentation peripherally and centrally.
- Event date: NONE
- Relative time: Further examination at presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1417: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Further examination revealed an isolated 5 3 5 cm grey/brown nodule on her right heel and a patch of leukoderma on the medial aspect of her right ankle (Fig 1, B)."
  - Evidence 1418: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "The leukoderma patch had follicular repigmentation both at the periphery of the lesion and centrally."

## Event 291: biopsy
- Description: A biopsy of the right-thigh tumor showed a malignant spindle-cell neoplasm; immunohistochemistry was HMB-45-, Melan-A-, and Sox-10-positive.
- Event date: NONE
- Relative time: At/after presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1419: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "A biopsy specimen of the right thigh tumor was obtained and revealed a malignant neoplasm with spindle cells arranged in a fascicular and storiform growth pattern, prominent necrosis, variable pleomorphism, numerous mitoses, and a pronounced lymphocytic inﬁltrate (Fig 2, C and D)."
  - Evidence 1420: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Immunohistochemical analysis showed the spindle cells to be HMB-45 (Fig 3, A), Melan-A (Fig 3, B) and Sox-10epositive, confirming the diagnosis of a malignant melanoma."

## Event 292: diagnosis
- Description: The right-thigh tumor was diagnosed as malignant melanoma.
- Event date: NONE
- Relative time: Following right-thigh biopsy
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1421: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Immunohistochemical analysis showed the spindle cells to be HMB-45 (Fig 3, A), Melan-A (Fig 3, B) and Sox-10epositive, confirming the diagnosis of a malignant melanoma."

## Event 293: biopsy
- Description: Two 5-mm punch biopsies of the right-heel nodule showed melanophages with extensive dermal fibrosis; staining was negative for Melan-A and Sox-10 and positive for CD163.
- Event date: NONE
- Relative time: At/after presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1422: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Two 5-mm punch biopsy specimens of the right heel nodule revealed numerous melanophages admixed with extensive dermal ﬁbrosis."
  - Evidence 1423: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Immunohistochemical staining was negative for Melan-A and Sox-10, but positive for CD163, a marker of macrophages."

## Event 294: tumor_regression
- Description: Right-heel pathology was consistent with stage III melanoma regression, with complete regression and absence of neoplastic cells.
- Event date: NONE
- Relative time: Following right-heel punch biopsies
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 1424: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "These ﬁndings were consistent with stage III regression of melanoma, namely complete regression with absence of neoplastic cells."
  - Evidence 1425: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "These neoplastic cells have been replaced by ﬁbrosis and inﬂammation or by densely packed melanophages (Fig 2, A and B)."

## Event 295: metastasis
- Description: Staging PET-CT showed mild fluorodeoxyglucose uptake in the right-heel mass, intense heterogeneous uptake in the right-thigh mass, and moderate uptake in right common iliac, external iliac, and inguinal lymph nodes representing metastases; no other organ involvement was identified.
- Event date: NONE
- Relative time: During staging
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1426: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Staging positron emission tomographyecomputed tomography revealed mild uptake of ﬂuorodeoxyglucose in the right heel mass and intense heterogeneous uptake in the right thigh mass."
  - Evidence 1427: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "nodes, including the right common iliac, external iliac, and inguinal nodes, representing metastases. There was no other organ involvement (Fig 4)."

## Event 296: biopsy
- Description: A repeat large incisional biopsy of the heel lesion, considered clinically representative of the tumor, confirmed absence of malignant cells.
- Event date: NONE
- Relative time: After staging; before diagnosis confirmation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 1428: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "Wide local excision of the heel lesion was not performed in view of stage IV disease, but a repeat large incisional biopsy, clinically representative of the tumor, conﬁrmed the absence of malignant cells and the diagnosis of complete regression."

## Event 297: diagnosis
- Description: Diagnosis was made of completely and spontaneously regressed acral melanoma with in-transit and distant lymph-node metastases and associated leukoderma; stage IV disease was documented.
- Event date: NONE
- Relative time: After staging and repeat heel biopsy
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 1429: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "Diagnosis was made of a completely and spontaneously regressed AM with in-transit and distant lymph node metastases plus associated leukoderma."
  - Evidence 1430: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "Wide local excision of the heel lesion was not performed in view of stage IV disease, but a repeat large incisional biopsy, clinically representative of the tumor, conﬁrmed the absence of malignant cells and the diagnosis of complete regression."

## Event 298: treatment
- Description: The patient received palliative radiation therapy for the right-thigh tumor.
- Event date: NONE
- Relative time: After diagnosis
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1431: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "The patient received palliative radia-tion therapy for the right thigh tumor."

## Event 299: other
- Description: Three months after presentation, the patient was alive and her pain was well controlled.
- Event date: NONE
- Relative time: 3 months after presentation
- Stored/source precision: relative / RELATIVE
- Relation to regression: AFTER
  - Evidence 1432: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "As of the time this article was written, 3 months after presentation, the patient was alive and her pain was well controlled."

# Lesion Map

## Lesion 20: thigh skin lesion
- Identity key: UNK|SKIN|THIGH|UNK|NONE|NONE|SINGLE
- Type: NONE
- Laterality: NONE
- Organ / location: SKIN / THIGH
- Aliases: medial right-thigh tumor [CONFIRMED_ALIAS]
- Observation 393: Medial right-thigh tumor morphology and size | DISEASE_PHENOTYPE | REPORTED/UNKNOWN | 20 3 18 cm fungating tumor
- Observation 398: Right-thigh tumor histopathology | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | malignant neoplasm with spindle cells arranged in a fascicular and storiform growth pattern, prominent necrosis, variable pleomorphism, numerous mitoses, and a pronounced lymphocytic infiltrate
- Observation 399: Right-thigh tumor immunohistochemistry | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | HMB-45, Melan-A and Sox-10 positive
- Observation 400: Right-thigh tumor diagnosis | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | malignant melanoma
- Observation 405: Fluorodeoxyglucose uptake in right thigh mass | BIOLOGICAL_STATE | REPORTED/UNKNOWN | intense heterogeneous uptake

## Lesion 21: right inguinal lymph node lymph node
- Identity key: RIGHT|LYMPH_NODE|INGUINAL|LYMPH_NODE|NONE|NONE|SINGLE
- Type: LYMPH_NODE
- Laterality: RIGHT
- Organ / location: LYMPH_NODE / INGUINAL
- Aliases: right inguinal lymph nodes [CONFIRMED_ALIAS]
- Observation 394: Right inguinal lymphadenopathy | CLINICAL_CONTEXT | REPORTED/PRESENT | associated right inguinal lymphadenopathy

## Lesion 22: right nodule
- Identity key: RIGHT|UNK|UNK|NODULE|NONE|NONE|SINGLE
- Type: NODULE
- Laterality: RIGHT
- Organ / location: NONE / NONE
- Aliases: right heel nodule [CONFIRMED_ALIAS]; right heel nodule [CONFIRMED_ALIAS]
- Observation 395: Right heel nodule morphology and size | DISEASE_PHENOTYPE | REPORTED/UNKNOWN | isolated 5 3 5 cm grey/brown nodule
- Observation 401: Right heel biopsy melanophages and dermal fibrosis | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | numerous melanophages admixed with extensive dermal fibrosis
- Observation 402: Right heel biopsy immunohistochemistry | DIAGNOSTIC_EVIDENCE | REPORTED/MIXED | negative for Melan-A and Sox-10, but positive for CD163
- Observation 403: Right heel melanoma regression | DIAGNOSTIC_EVIDENCE | REPORTED/ABSENT | stage III regression of melanoma, namely complete regression with absence of neoplastic cells
- Observation 404: Fluorodeoxyglucose uptake in right heel mass | BIOLOGICAL_STATE | REPORTED/UNKNOWN | mild uptake of fluorodeoxyglucose
- Observation 407: Final diagnosis | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | completely and spontaneously regressed AM with in-transit and distant lymph node metastases plus associated leukoderma

## Lesion 23: right lesion
- Identity key: RIGHT|UNK|UNK|UNK|NONE|NONE|SINGLE
- Type: NONE
- Laterality: RIGHT
- Organ / location: NONE / NONE
- Aliases: medial right ankle leukoderma patch [CONFIRMED_ALIAS]
- Observation 396: Leukoderma patch | DISEASE_PHENOTYPE | REPORTED/PRESENT | a patch of leukoderma on the medial aspect of her right ankle
- Observation 397: Leukoderma follicular repigmentation | DISEASE_PHENOTYPE | REPORTED/PRESENT | both at the periphery of the lesion and centrally

# Biological States

## Observation 404: Fluorodeoxyglucose uptake in right heel mass
- Category: METABOLIC
- Value: mild uptake of fluorodeoxyglucose
- Status / direction: REPORTED / UNKNOWN
- Semantics: IMAGING_PROXY
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right heel nodule
- Lesion ID / collection ID: 22 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1450: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Staging positron emission tomographyecomputed tomography revealed mild uptake of fluorodeoxyglucose in the right heel mass"

## Observation 405: Fluorodeoxyglucose uptake in right thigh mass
- Category: METABOLIC
- Value: intense heterogeneous uptake
- Status / direction: REPORTED / UNKNOWN
- Semantics: IMAGING_PROXY
- Time relation: UNKNOWN
- Scope / lesion: LESION / medial right-thigh tumor
- Lesion ID / collection ID: 20 / NONE
- Regression role: PROGRESSING_NON_TARGET
- Domain secondary: NONE
  - Evidence 1451: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "and intense heterogeneous uptake in the right thigh mass."

# Disease Phenotypes

## Observation 393: Medial right-thigh tumor morphology and size
- Category: PATHOLOGIC
- Value: 20 3 18 cm fungating tumor
- Status / direction: REPORTED / UNKNOWN
- Semantics: MORPHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LESION / medial right-thigh tumor
- Lesion ID / collection ID: 20 / NONE
- Regression role: PROGRESSING_NON_TARGET
- Domain secondary: NONE
  - Evidence 1438: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "had a 20 3 18 cm fungating tumor on the medial aspect of her right thigh with tissue sloughing and foul-smelling discharge"

## Observation 395: Right heel nodule morphology and size
- Category: PATHOLOGIC
- Value: isolated 5 3 5 cm grey/brown nodule
- Status / direction: REPORTED / UNKNOWN
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right heel nodule
- Lesion ID / collection ID: 22 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1440: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Further examination revealed an isolated 5 3 5 cm grey/brown nodule on her right heel"

## Observation 396: Leukoderma patch
- Category: PATHOLOGIC
- Value: a patch of leukoderma on the medial aspect of her right ankle
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / medial right ankle leukoderma patch
- Lesion ID / collection ID: 23 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1441: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "and a patch of leukoderma on the medial aspect of her right ankle"

## Observation 397: Leukoderma follicular repigmentation
- Category: PATHOLOGIC
- Value: both at the periphery of the lesion and centrally
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / medial right ankle leukoderma patch
- Lesion ID / collection ID: 23 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1442: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "The leukoderma patch had follicular repigmentation both at the periphery of the lesion and centrally."

# Diagnostic Evidence

## Observation 398: Right-thigh tumor histopathology
- Category: PATHOLOGIC
- Value: malignant neoplasm with spindle cells arranged in a fascicular and storiform growth pattern, prominent necrosis, variable pleomorphism, numerous mitoses, and a pronounced lymphocytic infiltrate
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LESION / medial right-thigh tumor
- Lesion ID / collection ID: 20 / NONE
- Regression role: PROGRESSING_NON_TARGET
- Domain secondary: NONE
  - Evidence 1443: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "A biopsy specimen of the right thigh tumor was obtained and revealed a malignant neoplasm with spindle cells arranged in a fascicular and storiform growth pattern, prominent necrosis, variable pleomorphism, numerous mitoses, and a pronounced lymphocytic infiltrate"

## Observation 399: Right-thigh tumor immunohistochemistry
- Category: PATHOLOGIC
- Value: HMB-45, Melan-A and Sox-10 positive
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LESION / medial right-thigh tumor
- Lesion ID / collection ID: 20 / NONE
- Regression role: PROGRESSING_NON_TARGET
- Domain secondary: NONE
  - Evidence 1444: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Immunohistochemical analysis showed the spindle cells to be HMB-45 (Fig 3, A), Melan-A (Fig 3, B) and Sox-10epositive, confirming the diagnosis of a malignant melanoma."

## Observation 400: Right-thigh tumor diagnosis
- Category: PATHOLOGIC
- Value: malignant melanoma
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LESION / medial right-thigh tumor
- Lesion ID / collection ID: 20 / NONE
- Regression role: PROGRESSING_NON_TARGET
- Domain secondary: NONE
  - Evidence 1445: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "confirming the diagnosis of a malignant melanoma."

## Observation 401: Right heel biopsy melanophages and dermal fibrosis
- Category: PATHOLOGIC
- Value: numerous melanophages admixed with extensive dermal fibrosis
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right heel nodule
- Lesion ID / collection ID: 22 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: DIAGNOSTIC_EVIDENCE
  - Evidence 1446: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Two 5-mm punch biopsy specimens of the right heel nodule revealed numerous melanophages admixed with extensive dermal fibrosis."

## Observation 402: Right heel biopsy immunohistochemistry
- Category: PATHOLOGIC
- Value: negative for Melan-A and Sox-10, but positive for CD163
- Status / direction: REPORTED / MIXED
- Semantics: PATHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right heel nodule
- Lesion ID / collection ID: 22 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1447: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Immunohistochemical staining was negative for Melan-A and Sox-10, but positive for CD163, a marker of macrophages."

## Observation 403: Right heel melanoma regression
- Category: PATHOLOGIC
- Value: stage III regression of melanoma, namely complete regression with absence of neoplastic cells
- Status / direction: REPORTED / ABSENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right heel nodule
- Lesion ID / collection ID: 22 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: DIAGNOSTIC_EVIDENCE
  - Evidence 1448: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "These findings were consistent with stage III regression of melanoma, namely complete regression with absence of neoplastic cells."
  - Evidence 1449: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "a repeat large incisional biopsy, clinically representative of the tumor, confirmed the absence of malignant cells and the diagnosis of complete regression."

## Observation 406: Other organ involvement
- Category: OTHER
- Value: no other organ involvement
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: IMAGING_PROXY
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1452: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "There was no other organ involvement (Fig 4)."

## Observation 407: Final diagnosis
- Category: PATHOLOGIC
- Value: completely and spontaneously regressed AM with in-transit and distant lymph node metastases plus associated leukoderma
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: AT_CONFIRMATION
- Scope / lesion: PATIENT / right heel nodule
- Lesion ID / collection ID: 22 / NONE
- Regression role: UNKNOWN
- Domain secondary: DIAGNOSTIC_EVIDENCE
  - Evidence 1453: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "Diagnosis was made of a completely and spontaneously regressed AM with in-transit and distant lymph node metastases plus associated leukoderma."

# Clinical Context

## Observation 390: Age
- Category: OTHER
- Value: 56-year-old
- Status / direction: REPORTED / UNKNOWN
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1435: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "A 56-year-old African woman with Fitzpatrick skin phototype VI presented"

## Observation 391: Weight loss, fatigue, and right leg pain
- Category: OTHER
- Value: significant weight loss, fatigue, and right leg pain
- Status / direction: REPORTED / PRESENT
- Semantics: SYMPTOM
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1436: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "She reported significant weight loss, fatigue, and right leg pain."

## Observation 392: Cachectic appearance
- Category: OTHER
- Value: cachectic
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1437: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "Upon examination, she appeared cachectic"

## Observation 394: Right inguinal lymphadenopathy
- Category: INFLAMMATORY
- Value: associated right inguinal lymphadenopathy
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right inguinal lymph nodes
- Lesion ID / collection ID: 21 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1439: page 1, section Case Report, type OBSERVED_FACT
  - Quote: "There was associated right inguinal lymphadenopathy."

## Observation 408: Vital status and pain control
- Category: OTHER
- Value: alive and her pain was well controlled
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: AFTER_REGRESSION
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1454: page 3, section Case Report, type OBSERVED_FACT
  - Quote: "As of the time this article was written, 3 months after presentation, the patient was alive and her pain was well controlled."

# Treatment Response

None.

# Genotype Observations

None.

# Explanatory Alternatives

None.

# Author Interpretations

## Interpretation 1
- Statement: Regression is caused by the host’s immunologic response against mutated melanocytes
- Rejection reason: Mechanistic causal assertion rather than a directly observed finding in this case.
- Page / section: 3 / Discussion
- Quote: "Regression is caused by the host’s immunologic response against mutated melanocytes"

## Interpretation 2
- Statement: the case supports the hypothesis that it may be associated with progressive metastatic disease.
- Rejection reason: Explicit hypothesis using “may”; association and causation are not directly observed mechanisms.
- Page / section: 4 / Discussion
- Quote: "the case supports the hypothesis that it may be associated with progressive metastatic disease."

# Rejected Claims

## Rejected claim 1
- Phase: PHASE 3.2
- Field: biological_observation.Lymph node metastases
- Reason: Quote was not found in normalized paper text
- Page: 3
- Quote: "There was also moderate uptake in multiple pathological lymph nodes, including the right common iliac, external iliac, and inguinal nodes, representing metastases."

# Special Validation — Paper B

- Primary acral lesion: right-heel nodule is present as a Case primary site and as Lesion 22 / observations 395, 401–404. Canonical name collapsed to “right nodule.”
- In-transit lesion: medial right-thigh fungating tumor is present as Lesion 20 and as PROGRESSING_NON_TARGET observations 393, 398–400, 405.
- Lymph-node metastases: right inguinal lymphadenopathy is a Clinical Context observation (394) and Lesion 21. Common iliac / external iliac / inguinal PET-CT metastases were rejected by quote verification and were not persisted as a collection.
- Complete regression: stored mainly as Diagnostic Evidence observation 403 (“stage III regression … complete regression with absence of neoplastic cells”) and as a patient-level final-diagnosis observation (407), not as a standalone Disease Phenotype of the primary.
- Viable malignant-cell absence: contained in the same observation 403 rather than a separate Pathologic Biological State. Repeat “absence of malignant cells” on the larger heel biopsy is a PHASE 2 Event (296) only.
- Leukoderma: observations 396–397 are DISEASE_PHENOTYPE on “medial right ankle leukoderma patch,” but persisted Lesion 23 is only “right lesion,” so leukoderma identity is unstable.
- Author immune-mechanism inference: correctly rejected as interpretation (host immunologic response; hypothesis that regression may associate with progressive metastatic disease).

# Validation Failures

- Heel / thigh / lymph-node / leukoderma scopes are not cleanly bound: four lesions were persisted as “thigh skin lesion,” “right inguinal lymph node lymph node,” “right nodule,” and “right lesion,” with no collections.
- Complete regression, absence of neoplastic cells, melanophages/fibrosis, and the clinical leukoderma phenotype were not separated into Disease Phenotype / Pathologic Biological State / Clinical phenotype.
- Age was duplicated as a CLINICAL_CONTEXT observation (390).
- Lymphocytic infiltrate in the thigh tumor remained Diagnostic Evidence only; no dual-domain immune Biological State was created.
- One PHASE 3 quote failure dropped the multi-station lymph-node metastasis sentence (PDF “tomographyecomputed” join).
- Schema, rule, and prompt were not changed.

# New Ontology Pressure Points

- Acral primary, in-transit mass, and a named lymph-node chain need collection membership plus stable canonical names; “right nodule” / “right lesion” are not identities.
- Complete regression is simultaneously a disease phenotype, a pathologic state (no viable cells), and a diagnostic conclusion.
- Leukoderma / follicular repigmentation is a cutaneous immune-associated phenotype, not a melanoma lesion, but it still needs a durable non-tumor skin-finding identity.
- Static measured sizes (20 × 18 cm; 5 × 5 cm) were kept with direction UNKNOWN, which is correct and should remain distinct from longitudinal decrease.
- No ontology patch was implemented.

# Validation Summary

- Case count: 1
- Event count: 14
- Observation count: 19
- Biological State: 2
- Disease Phenotype: 4
- Diagnostic Evidence: 8
- Clinical Context: 5
- Treatment Response: 0
- Genotype observations: 0
- Verified Evidence: 68
- Rejected Evidence: 2
- Quote failures: 1
