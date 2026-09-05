# External Validation Audit

- Paper ID: 5
- Title: Identification of a Germline Pyrin Variant in a Metastatic Melanoma Patient With Multiple Spontaneous Regressions and Immune-related Adverse Events
- DOI / PMID: 10.1097/CJI.0000000000000425 / 35621992
- PHASE 2 run: 51 (phase2.2.2 / phase2.2-adjudication-v4)
- PHASE 3 runs: 52 case 8
- Stable versions: schema phase2.2.2 / rule phase2.2-adjudication-v4; schema phase3.2 / rule phase3.2-ontology-v1 / prompt biological_observation_extraction:v3
- Validation-set rule: record mismatches without adapting ontology, schema, rule, or prompts. Selection rationale is research metadata only and was not preloaded into Case / Evidence / BiologicalObservation.
- PHASE 4 / Pattern Discovery / Public Hypothesis / Evidence Graph were not started.

# Case Summary — Case 8

- Case ID: 8
- Patient identifier: paper-5-case-1
- Age / sex: UNKNOWN / woman
- Melanoma subtype: metastatic melanoma
- Primary site: NOT STORED
- Stage: NOT STORED
- Metastatic sites: left axillary lymph node; liver; lung; left vaginal cuff; left inferior rectus muscle
- First observed reduction: During her evaluation (left axillary lymph node); October 2018 (hepatic lesions)
- Regression confirmation: NOT STORED
- Regression extent: UNCERTAIN
- Treatment before regression: NOT STORED
- Preceding events: June 2017 presentation with left axillary lymphadenopathy; left axillary lymph node biopsy and lymph node dissection; August 2018 CT-guided liver biopsy
- Outcome: Clinical status deteriorated with bleeding from hepatic metastases and Gram-negative bacteremia; transitioned to comfort care and discharged to inpatient hospice in April 2020.

## Case Field Statuses

- patient_identifier: NOT_REPORTED | raw value: None
- age: UNCERTAIN | raw value: None
- sex: REPORTED | raw value: woman
- melanoma_subtype: REPORTED | raw value: metastatic melanoma
- primary_site: NOT_REPORTED | raw value: None
- stage: NOT_REPORTED | raw value: None
- metastatic_sites: REPORTED | raw value: ['left axillary lymph node', 'liver', 'lung', 'left vaginal cuff', 'left inferior rectus muscle']
- diagnosis_date: REPORTED | raw value: August 2018
- regression_start_date: NOT_REPORTED | raw value: None
- first_observed_reduction: REPORTED | raw value: During her evaluation (left axillary lymph node); October 2018 (hepatic lesions)
- regression_confirmed_date: REPORTED | raw value: September 2018 (left axillary lymph node pathology); October 2018 (hepatic imaging)
- regression_duration: NOT_REPORTED | raw value: None
- regression_type: REPORTED | raw value: spontaneous regression of metastatic melanoma involving the left axillary lymph node and liver
- regression_extent_clinical: UNCERTAIN | raw value: UNCERTAIN
- viable_tumor_at_pathology: CONFLICTING | raw value: None
- treatment_before_regression: NOT_REPORTED | raw value: None
- treatment_status: REPORTED | raw value: no_treatment
- preceding_events: REPORTED | raw value: ['June 2017 presentation with left axillary lymphadenopathy', 'left axillary lymph node biopsy and lymph node dissection', 'August 2018 CT-guided liver biopsy']
- outcome: REPORTED | raw value: Clinical status deteriorated with bleeding from hepatic metastases and Gram-negative bacteremia; transitioned to comfort care and discharged to inpatient hospice in April 2020.
- follow_up_duration: NOT_REPORTED | raw value: None

# Timeline

## Event 257: diagnosis
- Description: Reported history of polymyalgia rheumatica and giant cell arteritis.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: BEFORE
  - Evidence 1349: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A woman in her 60s with a reported history of polymyalgia rheumatica (PMR) and giant cell arteritis (GCA) presented in June 2017 with left axillary lymphadenopathy."

## Event 258: other
- Description: Presented with left axillary lymphadenopathy; mammogram detected a large left axillary mass confirmed by ultrasound to be an enlarged lymph node.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: BEFORE
  - Evidence 1350: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A woman in her 60s with a reported history of polymyalgia rheumatica (PMR) and giant cell arteritis (GCA) presented in June 2017 with left axillary lymphadenopathy. A mammogram detected a large mass in the left axilla that was confirmed to be an enlarged lymph node (LN) by ultrasound."

## Event 259: biopsy
- Description: Initial left axillary lymph-node biopsy showed fibroadipose tissue with hemorrhage and acute inflammation, suggestive of a necrotic neoplasm; pigment deposition raised concern for metastatic melanoma.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: BEFORE
  - Evidence 1351: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "Biopsy of the LN initially revealed fragments of fibroadipose tissue with hemorrhage and acute inflammation, suggestive of a necrotic neoplasm. While the patient had no prior history of melanoma, concerns were raised by the pathologist for metastatic melanoma given the identification of pigment deposition."

## Event 260: other
- Description: Follow-up PET showed rim uptake in an enlarged 4 cm × 3 cm left axillary lymph node.
- Event date: NONE
- Relative time: Follow-up
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 1352: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A follow-up positron emission tomography (PET) scan showed rim uptake of an enlarged 4 cm×3 cm left axillary LN"

## Event 261: surgery
- Description: Left axillary lymph-node dissection revealed organizing hemorrhage, pigment-laden macrophages, and fat necrosis; no malignancy was identified in the 14 sampled lymph nodes.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: BEFORE
  - Evidence 1353: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "prompting a LN dissection procedure which revealed organizing hemorrhage, pigment-laden macrophages, and fat necrosis (Fig. 1). Immunohistochemical (IHC) stains for pancytokeratin (AE1/AE3) and SOX10 were negative, and no features of malignancy were identified in any of the 14 LNs sampled."

## Event 262: tumor_regression
- Description: The patient noted diminution in the size of the left axillary lymph node during her evaluation.
- Event date: NONE
- Relative time: during the course of her evaluation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 1354: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "Notably, during the course of her evaluation, the patient noted a diminishment in the size of the noted left axillary LN."

## Event 263: other
- Description: Developed upper abdominal and lower chest discomfort.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: BEFORE
  - Evidence 1355: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "In August 2018, she developed upper abdominal and lower chest discomfort."

## Event 264: metastasis
- Description: CT angiogram identified multiple hepatic lesions not present on prior PET imaging; abdominal and pelvic CT confirmed multiple hypodensities in both hepatic lobes highly suspicious for metastatic disease.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: BEFORE
  - Evidence 1356: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A computerized tomography (CT) angiogram of the chest to rule out pulmonary embolism incidentally discovered multiple hepatic lesions not present on prior PET imaging. Dedicated CT of the abdomen and pelvis confirmed multiple hypodensities within the right and left hepatic lobes, highly suspicious for metastatic disease (Fig. 2A)."

## Event 265: biopsy
- Description: CT-guided liver needle biopsy showed pathology consistent with metastatic melanoma.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: BEFORE
  - Evidence 1357: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A CT-guided needle biopsy of the liver was performed revealing pathology consistent with metastatic melanoma."

## Event 266: diagnosis
- Description: Metastatic melanoma was identified by liver biopsy, with diffusely positive SOX10, Mart-1, and HMB45 staining and weakly positive S100 staining.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: BEFORE
  - Evidence 1358: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A CT-guided needle biopsy of the liver was performed revealing pathology consistent with metastatic melanoma. IHC findings were diffusely positive for SOX10, Mart-1, and HMB45, while S100 staining was weakly positive."

## Event 267: tumor_regression
- Description: Outside pathology review identified pathologic evidence of spontaneous melanoma regression involving a left axillary lymph node.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: DURING
  - Evidence 1359: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "The patient was seen as an initial consult in September 2018 in the Skin Cancer Clinic at the Duke Cancer Institute. Outside tissue biopsy specimens were reviewed by the Duke dermatopathology team revealing pathologic evidence of spontaneous melanoma regression involving a left axillary LN (Fig. 1B)."

## Event 268: other
- Description: Brain MRI showed no evidence of intracranial metastases.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: DURING
  - Evidence 1360: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "Additional imaging studies were performed in October 2018, including magnetic resonance imaging of the brain showing no evidence of intracranial metastases."

## Event 269: tumor_regression
- Description: PET-CT showed 2 of 3 hepatic lesions were smaller than on the August 2018 CT.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: DURING
  - Evidence 1361: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A PET-CT confirmed evidence of multiple hepatic metastases, and 2 of 3 lesions were notably of smaller size relative to the prior CT imaging study in August 2018: hepatic segment VIII/IV lesion 3.2×2.2–1.3×1.2 cm, left hepatic lobe lesion 2.1×1.4–1.1×0.9 cm (Fig. 2B)."
  - Evidence 1362: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "Computed tomography imaging of the abdomen/pelvis in October 2018 showing decreased size of hepatic lesions without any form of therapy (red arrows)."

## Event 270: biopsy
- Description: Repeat liver biopsy confirmed metastatic melanoma; BRAF analysis detected a V600E mutation.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1363: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A repeat liver biopsy in November 2018 confirmed metastatic melanoma with IHC stains positive for S100 and MART45. BRAF mutation analysis was positive and detected a V600E mutation (p.Val600Glu;c.1799T>A)."

## Event 271: treatment
- Description: Pembrolizumab 200 mg intravenously every 3 weeks was initiated; she underwent 7 cycles from November 2018 to March 2019.
- Event date: NONE
- Relative time: from November 2018 to March 2019
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1364: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "This prompted the initiation of pembrolizumab (anti-PD-1 antibody, 200 mg intravenously every 3 wk), and she underwent 7 cycles of treatment from November 2018 to March 2019."

## Event 272: tumor_progression
- Description: PET-CT showed increased hepatic lesion size and new lesions in the left lower-lobe lung, left vaginal cuff, and left inferior rectus muscle, consistent with disease progression.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1365: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "PET-CT imaging in April 2019 showed an increase in the size of hepatic lesions along with a new left lower lobe lung nodule, a new soft tissue density along the left vaginal cuff, and asymmetric thickening of the left inferior rectus muscle, all consistent with disease progression."

## Event 273: tumor_regression
- Description: Repeat PET-CT showed improvement in hepatic and pulmonary metastases; soft-tissue nodules adjacent to the vaginal cuff and left inferior rectus muscle thickening had resolved.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1366: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "Repeat PET-CT imaging in July of 2019 showed improvement of hepatic and pulmonary metastases, suggestive of response. The soft tissue nodules adjacent to the vaginal cuff and the thickening of the left inferior rectus muscle had resolved."

## Event 274: other
- Description: Developed persistent diarrhea and gastrointestinal bleeding while receiving dabrafenib/trametinib.
- Event date: NONE
- Relative time: on dabrafenib/trametinib
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1367: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "The patient developed persistent diarrhea and a gastrointestinal bleed on dabrafenib/trametinib."

## Event 275: treatment
- Description: Transitioned to encorafenib/binimetinib, 450 mg daily/45 mg twice per day.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1368: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "She was subsequently transitioned to encorafenib/binimetinib (450 mg daily/45 mg twice per day) in September of 2019"

## Event 276: fever
- Description: Experienced low-grade fevers, nausea, vomiting, and loose stools despite several encorafenib/binimetinib dose reductions.
- Event date: NONE
- Relative time: despite several dose reductions
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1369: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "but continued to have nausea, vomiting, low-grade fevers, and loose stools despite several dose reductions."

## Event 277: tumor_regression
- Description: Follow-up PET-CT showed continued tumor response with decreased hepatic lesion size.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1370: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "Follow-up PET-CT imaging in October of 2019 showed continued tumor response with a decreased size in the hepatic lesions."

## Event 278: other
- Description: Developed grade 3 hepatotoxicity after the first ipilimumab/nivolumab cycle and was treated with high-dose prednisone, with improvement in AST and ALT.
- Event date: NONE
- Relative time: after the first cycle
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1371: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "On follow-up, she was found to have developed grade 3 hepatotoxicity after the first cycle and was treated with high-dose steroids (prednisone 1 mg/kg daily) with improvement in aspartate transaminase from 514 to 46 U/L (normal: 15–41 U/L) and alanine transaminase from 286 to 68 U/L (normal: 14–54 U/L)."

## Event 279: treatment
- Description: Transitioned back to encorafenib monotherapy at 225 mg daily.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1372: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "In light of these findings, the patient was transitioned back to encorafenib monotherapy (225 mg daily) in February of 2020."

## Event 280: hospitalization
- Description: Hospitalized from February to March 2020 for back pain, malaise, lower-extremity weakness, worsening dysphonia, and dysphagia.
- Event date: NONE
- Relative time: from February to March of 2020
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1373: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "She then began to report back pain, malaise, and lower extremity weakness, which required hospitalization from February to March of 2020, during which she exhibited worsening dysphonia and dysphagia."

## Event 281: diagnosis
- Description: Diagnosed with progressive polymyositis; strength gradually improved with high-dose steroids, and CT during that admission showed stable disease.
- Event date: NONE
- Relative time: during the February to March 2020 hospitalization
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1374: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "She was ultimately diagnosed with progressive polymyositis associated with an elevated aldolase of 12.9 U/L (normal: <7.7 U/L), normal creatine kinase of 107 U/L (normal: 30–220 U/L), a normal estimated sedimentation rate of 13 mm/h (normal: 0–15 mm/h), and an elevated C-reactive protein of 1.47 mg/dL (normal: ≤0.60 mg/dL). Ultimately, her strength gradually improved with high-dose steroids, and a CT scan from that admission showed stable disease."

## Event 282: hospitalization
- Description: Readmitted later in March for suspected myasthenia gravis with polymyositis due to bulbar weakness, gaze difficulty, and nasal dysarthria.
- Event date: NONE
- Relative time: later in March
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1375: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "During the course of her prednisone taper, she experienced worsening dysphagia and dysarthria. She was re-admitted later in March for suspicion of myasthenia gravis with polymyositis, given symptoms of bulbar weakness, gaze difficulty, and nasal dysarthria."

## Event 283: diagnosis
- Description: She was presumed to have a neuromuscular junction disorder overlapping with polymyositis in the setting of checkpoint inhibitor toxicity and was treated with 4 days of intravenous immunoglobulin.
- Event date: NONE
- Relative time: during the later March readmission
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1376: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "She was ultimately presumed to have a neuromuscular junction disorder overlapping with polymyositis in the setting of checkpoint inhibitor toxicity. She was subsequently treated with 4 days of intravenous immunoglobulin (0.5 g/kg daily)."

## Event 284: infection
- Description: Developed Gram-negative bacteremia during rapid clinical deterioration, along with bleeding from hepatic metastases.
- Event date: NONE
- Relative time: thereafter
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 1377: page 3, section Case Presentation, type AUTHOR_INTERPRETATION
  - Quote: "Unfortunately, her clinical status deteriorated rapidly thereafter with bleeding from hepatic metastases and Gram-negative bacteremia before additional therapeutic measures could be taken."

## Event 285: hospitalization
- Description: Transitioned to comfort care and was discharged to inpatient hospice.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / APPROXIMATE
- Relation to regression: AFTER
  - Evidence 1378: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "She was transitioned to comfort care and discharged to inpatient hospice in April 2020."

# Lesion Map

## Lesion 18: liver lesion
- Identity key: UNK|LIVER|UNK|LESION|BIOPSY|NONE|SINGLE
- Type: LESION
- Laterality: NONE
- Organ / location: LIVER / NONE
- Aliases: biopsied liver lesion [CONFIRMED_ALIAS]
- Observation 384: Liver biopsy diagnosis | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | pathology consistent with metastatic melanoma
- Observation 385: Liver metastasis immunohistochemistry | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | SOX10, Mart-1, and HMB45 diffusely positive; S100 weakly positive

## Lesion 19: left lower lobe lung lesion
- Identity key: LEFT|LUNG|LOWER_LOBE|LESION|BIOPSY|NONE|SINGLE
- Type: LESION
- Laterality: LEFT
- Organ / location: LUNG / LOWER_LOBE
- Aliases: left lower lobe biopsied lesion [CONFIRMED_ALIAS]
- Observation 387: Disease progression during pembrolizumab treatment | DISEASE_PHENOTYPE | REPORTED/INCREASED | increase in the size of hepatic lesions with new left lower lobe lung nodule, left vaginal cuff soft tissue density, and left inferior rectus muscle thickening

## Collections

### Collection 3: liver lesions
- Type: LESION_COLLECTION
- Members: NONE
- Observation 383: Hepatic lesions on CT | BIOLOGICAL_STATE | multiple hypodensities within the right and left hepatic lobes

# Biological States

## Observation 383: Hepatic lesions on CT
- Category: PATHOLOGIC
- Value: multiple hypodensities within the right and left hepatic lobes
- Status / direction: REPORTED / PRESENT
- Semantics: IMAGING_PROXY
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / multiple hepatic lesions
- Lesion ID / collection ID: NONE / 3
- Regression role: REGRESSING_TARGET
- Domain secondary: DIAGNOSTIC_EVIDENCE
  - Evidence 1379: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "Dedicated CT of the abdomen and pelvis confirmed multiple hypodensities within the right and left hepatic lobes"

# Disease Phenotypes

## Observation 386: Hepatic metastasis sizes
- Category: PATHOLOGIC
- Value: hepatic segment VIII/IV lesion 3.2×2.2–1.3×1.2 cm, left hepatic lobe lesion 2.1×1.4–1.1×0.9 cm
- Status / direction: REPORTED / DECREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1383: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "2 of 3 lesions were notably of smaller size relative to the prior CT imaging study in August 2018: hepatic segment VIII/IV lesion 3.2×2.2–1.3×1.2 cm, left hepatic lobe lesion 2.1×1.4–1.1×0.9 cm"

## Observation 387: Disease progression during pembrolizumab treatment
- Category: PATHOLOGIC
- Value: increase in the size of hepatic lesions with new left lower lobe lung nodule, left vaginal cuff soft tissue density, and left inferior rectus muscle thickening
- Status / direction: REPORTED / INCREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: AFTER_REGRESSION
- Scope / lesion: LESION / left lower lobe biopsied lesion
- Lesion ID / collection ID: 19 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1384: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "PET-CT imaging in April 2019 showed an increase in the size of hepatic lesions along with a new left lower lobe lung nodule, a new soft tissue density along the left vaginal cuff, and asymmetric thickening of the left inferior rectus muscle, all consistent with disease progression."

# Diagnostic Evidence

## Observation 384: Liver biopsy diagnosis
- Category: PATHOLOGIC
- Value: pathology consistent with metastatic melanoma
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / biopsied liver lesion
- Lesion ID / collection ID: 18 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1380: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A CT-guided needle biopsy of the liver was performed revealing pathology consistent with metastatic melanoma."
  - Evidence 1381: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "A repeat liver biopsy in November 2018 confirmed metastatic melanoma"

## Observation 385: Liver metastasis immunohistochemistry
- Category: PATHOLOGIC
- Value: SOX10, Mart-1, and HMB45 diffusely positive; S100 weakly positive
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / biopsied liver lesion
- Lesion ID / collection ID: 18 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1382: page 2, section Case Presentation, type OBSERVED_FACT
  - Quote: "IHC findings were diffusely positive for SOX10, Mart-1, and HMB45, while S100 staining was weakly positive."

## Observation 388: Disease status on CT during hospitalization
- Category: PATHOLOGIC
- Value: stable disease
- Status / direction: REPORTED / UNCHANGED
- Semantics: IMAGING_PROXY
- Time relation: AFTER_REGRESSION
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1385: page 3, section Case Presentation, type OBSERVED_FACT
  - Quote: "a CT scan from that admission showed stable disease."

# Clinical Context

## Observation 389: infection
- Category: MICROBIOME
- Value: Developed Gram-negative bacteremia during rapid clinical deterioration, along with bleeding from hepatic metastases.
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1377: page 3, section Case Presentation, type AUTHOR_INTERPRETATION
  - Quote: "Unfortunately, her clinical status deteriorated rapidly thereafter with bleeding from hepatic metastases and Gram-negative bacteremia before additional therapeutic measures could be taken."

# Treatment Response

None.

# Genotype Observations

None.

# Explanatory Alternatives

None.

# Author Interpretations

None.

# Rejected Claims

## Rejected claim 1
- Phase: PHASE 2
- Field: event.description
- Reason: Quote was not found in normalized paper text
- Page: 2
- Quote: "The patient was started on dabrafenib/trametinib (100 mg every 12 h/2.0 mg daily) in June of 2019."

## Rejected claim 2
- Phase: PHASE 2
- Field: event.description
- Reason: Quote was not found in normalized paper text
- Page: 2
- Quote: "Given the patient’s persistent inability to tolerate BRAF/MEK inhibitor therapy, she was transitioned to ipilimumab (1 mg/kg) and nivolumab (3 mg/kg) in November of 2019 (intravenously every 3 wk)."

## Rejected claim 3
- Phase: PHASE 2
- Field: event.description
- Reason: Quote was not found in normalized paper text
- Page: 3
- Quote: "PET-CT in January of 2020 showed a dramatic increase in the size and number of hepatic metastases including a right hepatic lobe lesion that increased from 2.2×1.8 to 11.8×10.4 cm."

## Rejected claim 4
- Phase: PHASE 3.2
- Field: biological_observation.Hepatic lesions on CT
- Reason: Quote was not found in normalized paper text
- Page: 2
- Quote: "CT angiogram of the chest to rule out pulmonary embolism incidentally discovered multiple hepatic lesions not present on prior PET imaging."

# Special Validation — Paper A

- Multiple spontaneous-regression episodes: PHASE 2 stored separate tumor_regression events for the left axillary node (events 262, 267) and pre-treatment hepatic shrinkage (event 269). PHASE 3 persisted only one hepatic size-change phenotype (observation 386) and did not persist the axillary complete-regression episode as a Disease Phenotype.
- Immunotherapy Event/history: PHASE 2 kept pembrolizumab, BRAF/MEK inhibitors, and ipilimumab/nivolumab as treatment Events after the spontaneous episodes. Those later on-treatment changes were not written as spontaneous regression.
- Spontaneous regression vs treatment response: no TREATMENT_RESPONSE observations were created. Later PET improvements after targeted therapy remain timeline Events (273, 277), which avoids calling them spontaneous, but they are also not typed as Treatment Response.
- Immune-related adverse events: diarrhea/GI bleeding, grade 3 hepatotoxicity, polymyositis, and suspected myasthenia were stored as Events (274, 278, 281–283), not as Clinical Context observations. The only Clinical Context observation is Gram-negative bacteremia.
- Genetic finding as GenotypeObservation: MEFV/pyrin germline P369S/R408Q is present in the PDF and is absent from GenotypeObservation. Somatic BRAF V600E on repeat liver biopsy is present as Event 270 and is also absent from GenotypeObservation.
- Germline variant not collapsed to ABSENT/PRESENT: the variant was omitted rather than coerced to a simple presence flag.
- Systemic vs lesion-level: imaging of multiple hepatic lesions was stored as BIOLOGICAL_STATE with secondary DIAGNOSTIC_EVIDENCE (observation 383). irAEs remained unscoped systemic Events. No patient-level genotype/systemic-immune observation was created.

# Validation Failures

- PHASE 2 status is partial with three quote failures on BRAF/MEK, ipilimumab/nivolumab, and January 2020 PET-CT sentences (PDF line-wrap / hyphenation).
- PHASE 3 status is partial with one quote failure on the incidental hepatic-lesion CT sentence.
- Age is UNCERTAIN; the paper reports only “a woman in her 60s,” which the case layer did not persist as an approximate value.
- PHASE 3 produced only 7 observations and 0 genotype records, so the paper’s core external-validation targets (two spontaneous-regression sites, checkpoint-inhibitor history, irAEs, WES/pyrin) are mostly missing from the observation layer.
- Observation 383 classifies static CT hypodensities as BIOLOGICAL_STATE rather than Diagnostic Evidence alone.
- Observation 387 records pembrolizumab-era progression as DISEASE_PHENOTYPE on “left lower lobe biopsied lesion,” collapsing new lung / vaginal-cuff / rectus sites into one lesion identifier.
- No ExplanatoryAlternative was created for later treatment, delayed response, or the author’s inflammasome hypothesis.
- Schema, rule, and prompt were not changed.

# New Ontology Pressure Points

- A germline inflammasome variant needs a genotype object that can carry gene, protein, two coding changes, rs IDs, and germline origin without being reduced to mutation ABSENT/PRESENT or to the BRAF-only persist path.
- Multiple spontaneous-regression episodes at different organs and times need durable episode identity, not a single case-level regression_type string.
- irAEs are timed Events and systemic Clinical Context at once; one layer currently captures them only as Events.
- Approximate age (“in her 60s”) has no first-class case-age precision.
- Shared imaging sentences that both discover new lesions and later document shrinkage need lesion-set identity plus a time-indexed disease state.
- PDF hyphenation continues to drop legally present quotes.
- No ontology patch was implemented.

# Validation Summary

- Case count: 1
- Event count: 29
- Observation count: 7
- Biological State: 1
- Disease Phenotype: 2
- Diagnostic Evidence: 3
- Clinical Context: 1
- Treatment Response: 0
- Genotype observations: 0
- Verified Evidence: 69
- Rejected Evidence: 0
- Quote failures: 4
