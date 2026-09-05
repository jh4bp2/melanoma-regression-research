# External Validation Audit

- Paper ID: 4
- Title: Spontaneous regression of metastatic melanoma after inoculation with tetanus-diphtheria-pertussis vaccine
- Validation-set rule: record mismatches without adapting ontology, schema, rule, or prompts.

# Case Summary

- Patient identifier: paper-4-case-1
- Age / sex: 44 / male
- Melanoma subtype: NOT STORED
- Primary site: right anterior tibial area
- Stage: stage IV disease (previously stage IIIB)
- Metastatic sites: upper right thigh in-transit metastases; chest lesion above the left nipple; left axillary nodule; right-middle-lobe lung nodules; right external iliac lymph node
- First observed reduction: One week after Adacel vaccination
- Regression confirmation: NOT STORED
- Regression extent: UNCERTAIN
- Treatment before regression: Excision of the primary lesion; adjuvant high-dose interferon alfa followed by maintenance interferon; palliative radiotherapy to upper-right-thigh in-transit metastases
- Preceding events: Adacel tetanus-diphtheria-acellular pertussis vaccination; local and systemic febrile reaction lasting 2 days
- Outcome: All nodules vanished except an enlarged left axillary nodule; after left axillary-node resection, follow-up continued to demonstrate a disease-free state.

## Case Field Statuses

- patient_identifier: NOT_REPORTED | raw value: None
- age: REPORTED | raw value: 44
- sex: REPORTED | raw value: male
- melanoma_subtype: UNCERTAIN | raw value: malignant melanoma
- primary_site: REPORTED | raw value: right anterior tibial area
- stage: REPORTED | raw value: stage IV disease (previously stage IIIB)
- metastatic_sites: REPORTED | raw value: ['upper right thigh in-transit metastases', 'chest lesion above the left nipple', 'left axillary nodule', 'right-middle-lobe lung nodules', 'right external iliac lymph node']
- diagnosis_date: NOT_REPORTED | raw value: None
- regression_start_date: NOT_REPORTED | raw value: None
- first_observed_reduction: REPORTED | raw value: One week after Adacel vaccination
- regression_confirmed_date: REPORTED | raw value: Two months after repeat imaging performed 3 months before planned study enrollment
- regression_duration: NOT_REPORTED | raw value: None
- regression_type: REPORTED | raw value: spontaneous regression of metastatic melanoma
- regression_extent_clinical: UNCERTAIN | raw value: UNCERTAIN
- viable_tumor_at_pathology: CONFLICTING | raw value: None
- treatment_before_regression: REPORTED | raw value: Excision of the primary lesion; adjuvant high-dose interferon alfa followed by maintenance interferon; palliative radiotherapy to upper-right-thigh in-transit metastases
- treatment_status: REPORTED | raw value: treatment_completed
- preceding_events: REPORTED | raw value: ['Adacel tetanus-diphtheria-acellular pertussis vaccination', 'local and systemic febrile reaction lasting 2 days']
- outcome: REPORTED | raw value: All nodules vanished except an enlarged left axillary nodule; after left axillary-node resection, follow-up continued to demonstrate a disease-free state.
- follow_up_duration: NOT_REPORTED | raw value: None

# Timeline

## Event 144: other
- Description: The patient developed local irritation of a longstanding nevus on the right anterior tibial area, progressing to ulceration and bleeding over several months.
- Event date: NONE
- Relative time: over several months
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 865: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "A 44-year-old white man with no past medical history developed local irritation of a longstanding nevus on the right anterior tibial area, which progressed to ulceration and bleeding over several months."

## Event 145: surgery
- Description: Sentinel node biopsy and repeat resection of the primary site with 1 cm margins were performed; the primary site was free of melanoma and the sentinel node contained a 1-mm focus of disease.
- Event date: NONE
- Relative time: Five months from initial presentation
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 866: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "Five months from initial presentation, a sentinel node biopsy and repeat resection of the primary site, with 1 cm margins, was performed. The site of the primary lesion was free of melanoma. However, the sentinel node biopsy showed a 1-mm focus of disease."

## Event 146: surgery
- Description: A right inguinal lymph node dissection showed involvement in 1 of 6 lymph nodes.
- Event date: NONE
- Relative time: After 3 months
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 867: page 1, section Title, type OBSERVED_FACT
  - Quote: "After 3 months, a right inguinal lymph node dissection revealed involvement in 1 of 6 lymph nodes."

## Event 147: diagnosis
- Description: The patient was considered to have T2bN1aM0 stage IIIB disease; clinical examination and CT showed no distant metastasis.
- Event date: NONE
- Relative time: After 3 months
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 868: page 1, section Title, type OBSERVED_FACT
  - Quote: "Clinical examination and computed tomography imaging showed no evidence of distant metastasis. The patient was considered to have T2bN1aM0 stage iiib disease."

## Event 148: treatment
- Description: Adjuvant high-dose interferon alfa was started as a 4-week intravenous induction course followed by an 11-month subcutaneous maintenance course.
- Event date: NONE
- Relative time: One month later
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 869: page 1, section Title, type OBSERVED_FACT
  - Quote: "One month later, the patient started a 4-week induction course of adjuvant high-dose interferon alfa at a daily dose of 36×106 U intravenously 5 days per week, followed by an 11-month course of 18×106 U interferon alfa 3 times weekly subcutaneously for maintenance."

## Event 149: fever
- Description: During interferon alfa treatment, the patient experienced fever among treatment-associated symptoms.
- Event date: NONE
- Relative time: during the interferon regimen
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 870: page 1, section Title, type OBSERVED_FACT
  - Quote: "He tolerated this regimen well, with some symptoms of muscle pain, diarrhea, fever, and occasional headaches in addition to a slight elevation of liver enzymes."

## Event 150: tumor_progression
- Description: The patient developed approximately 15 in-transit metastases in the upper right thigh, with two additional similar subcutaneous nodules on the upper lateral right thigh.
- Event date: NONE
- Relative time: Eleven months into therapy
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 871: page 1, section Title, type OBSERVED_FACT
  - Quote: "Eleven months into therapy, the patient developed multiple (approximately 15) in-transit metastases in the upper right thigh. These erythematous lesions ranged in size from 1 mm to 10 mm. Two other similar subcutaneous nodules were also seen on the upper lateral aspect of the right thigh (Figure 1)."

## Event 151: treatment
- Description: Palliative radiotherapy was delivered to the thigh nodules and intervening skin, with good response.
- Event date: NONE
- Relative time: after development of in-transit metastases
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 872: page 1, section Title, type OBSERVED_FACT
  - Quote: "The patient underwent palliative radiotherapy of 40 Gy in 10 fractions to each nodule and 30 Gy in 10 fractions to the intervening skin, with good response."

## Event 152: treatment
- Description: The patient completed his 1-year course of interferon.
- Event date: NONE
- Relative time: after follow-up imaging showed no other recurrence
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 873: page 1, section Title, type OBSERVED_FACT
  - Quote: "Follow-up imaging showed no other recurrence. The patient completed his 1-year course of interferon."

## Event 153: tumor_progression
- Description: The patient developed nodules above the left nipple, in the axilla, under the chin, and on the central back.
- Event date: NONE
- Relative time: Six months after the course of interferon
- Stored/source precision: relative / RELATIVE
- Relation to regression: BEFORE
  - Evidence 874: page 1, section Title, type OBSERVED_FACT
  - Quote: "Six months after the course of interferon, the patient developed a tender 5-mm nodule above the left nipple, a 5-mm axillary nodule, and a small nodule under the chin and on the central back."

## Event 154: biopsy
- Description: The chest lesion was excised and proved to be melanoma; punch biopsy of the left axillary nodule showed a malignant non-melanin tumour with melanoma immunohistochemistry suggesting metastatic disease.
- Event date: NONE
- Relative time: Six months after the course of interferon
- Stored/source precision: relative / RELATIVE
- Relation to regression: BEFORE
  - Evidence 875: page 1, section Title, type AUTHOR_INTERPRETATION
  - Quote: "The chest lesion was excised and proved to be melanoma. A punch biopsy of the left axillary nodule revealed a malignant non-melanin tumour. Immunohistochemistry for melanoma was positive for S100, mart-1, and tyrosinase, and negative for HMB45, suggesting metastatic disease1."

## Event 155: metastasis
- Description: Imaging showed new right-middle-lobe lung nodules up to 3.5 mm and an enlarged right external iliac lymph node measuring 15×13 mm.
- Event date: NONE
- Relative time: Six months after the course of interferon
- Stored/source precision: relative / RELATIVE
- Relation to regression: BEFORE
  - Evidence 876: page 1, section Title, type OBSERVED_FACT
  - Quote: "In addition, imaging showed new right-middle-lobe lung nodules measuring up to 3.5 mm in diameter, and an enlarged 15×13-mm right external iliac lymph node."

## Event 156: diagnosis
- Description: Investigations for trial enrollment were initiated for what was now stage IV disease.
- Event date: NONE
- Relative time: after detection of new nodules and imaging findings
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 877: page 1, section Title, type OBSERVED_FACT
  - Quote: "Investigations were initiated for enrollment in a trial for what was now stage iv disease."

## Event 157: vaccination
- Description: The patient received Adacel vaccine as a routine preventive measure.
- Event date: NONE
- Relative time: Three months later
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 878: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Three months later, the patient received Adacel vaccine (Sanofi Pasteur, Lyon, France) as a routine preventive measure."

## Event 158: fever
- Description: The patient developed a local and systemic febrile reaction lasting 2 days after Adacel vaccination.
- Event date: NONE
- Relative time: after Adacel vaccination; lasted 2 days
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 879: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "The patient developed a local and systemic febrile reaction that lasted 2 days."

## Event 159: tumor_regression
- Description: Dramatic improvement in all aforementioned nodules was noted on clinical examination.
- Event date: NONE
- Relative time: One week later
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 880: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "One week later, dramatic improvement in all of the aforementioned nodules was noted on clinical examination."

## Event 160: tumor_progression
- Description: CT showed a new 20-mm aortopulmonary-window lymph node and several new nodules in the right middle lobe, over the right pectoral muscle, in the left axilla, over the left rectus abdominis, and in subcutaneous fat overlying the T3 spinous process.
- Event date: NONE
- Relative time: One week later
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 881: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Computed tomography imaging showed a new 20-mm lymph node in the aortopulmonary window and also several new nodules measuring 3–11 mm in the right middle lobe, over the right pectoral muscle, in the left axilla, over the left rectus abdominis, and in the subcutaneous fat overlying the T3 spinous process."

## Event 161: biopsy
- Description: Biopsy of a resolved back nodule showed fibrosis and no disease.
- Event date: NONE
- Relative time: after clinical improvement and CT imaging
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 882: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "A biopsy of a resolved nodule on the patient’s back showed fibrosis, but no disease."

## Event 162: tumor_regression
- Description: Repeat imaging showed progressive reduction in the size of the nodules.
- Event date: NONE
- Relative time: after another 3 months
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 883: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Repeat imaging before study enrollment after another 3 months showed progressive reduction in the size of the nodules."

## Event 163: tumor_regression
- Description: All nodules had vanished except for an enlarged left axillary nodule; because of remission, the patient was not enrolled in the trial.
- Event date: NONE
- Relative time: Two months later
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 884: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Two months later, all of the nodules had vanished, except for an enlarged nodule in the left axilla. Because of this remission, the patient was not enrolled."

## Event 164: surgery
- Description: The 10-mm left axillary lymph node was resected.
- Event date: NONE
- Relative time: One month later
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 885: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "One month later, the 10-mm lymph node in the left axilla was resected."

## Event 165: biopsy
- Description: The resected left axillary lymph node contained melanoma, staining positive for S100, mart-1, and tyrosinase and negative for HMB45.
- Event date: NONE
- Relative time: at left axillary lymph-node resection
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 886: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "The surgical specimen showed melanoma, which again stained positive for S100, mart-1, and tyrosinase, and negative for HMB45."

## Event 166: other
- Description: Regular clinic and imaging follow-up continued to demonstrate a disease-free state.
- Event date: NONE
- Relative time: since left axillary-node resection
- Stored/source precision: unknown / RELATIVE
- Relation to regression: AFTER
  - Evidence 887: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "This patient has since been regularly followed with clinic visits and imaging that continues to demonstrate a disease-free state."

# Lesion Map

## aortopulmonary-window lymph node
- Scope: LYMPH_NODE
- Roles: UNKNOWN
- Observation 260: Aortopulmonary window lymph node | REPORTED/PRESENT | new 20-mm lymph node in the aortopulmonary window

## left axillary lymph node
- Scope: LYMPH_NODE
- Roles: PROGRESSING_NON_TARGET
- Observation 268: Left axillary lymph node size | REPORTED/UNKNOWN | 10-mm lymph node
- Observation 269: Resected left axillary lymph node diagnosis | REPORTED/PRESENT | melanoma
- Observation 270: Resected left axillary lymph node melanoma immunohistochemistry | REPORTED/MIXED | positive for S100, mart-1, and tyrosinase, and negative for HMB45

## left axillary nodule
- Scope: LESION
- Roles: PROGRESSING_NON_TARGET
- Observation 250: Left axillary nodule size | REPORTED/PRESENT | 5-mm axillary nodule
- Observation 253: Left axillary nodule pathology | REPORTED/PRESENT | malignant non-melanin tumour
- Observation 254: Left axillary nodule melanoma immunohistochemistry | REPORTED/MIXED | positive for S100, mart-1, and tyrosinase, and negative for HMB45
- Observation 267: Left axillary nodule enlargement | REPORTED/INCREASED | enlarged nodule in the left axilla

## nodule above left nipple
- Scope: LESION
- Roles: UNKNOWN
- Observation 249: Tender chest nodule | REPORTED/PRESENT | tender 5-mm nodule above the left nipple

## nodule above left nipple chest lesion
- Scope: LESION
- Roles: UNKNOWN
- Observation 252: Chest lesion diagnosis | REPORTED/PRESENT | melanoma

## primary lesion resection site
- Scope: LESION
- Roles: UNKNOWN
- Observation 237: Melanoma at primary resection site | REPORTED_ABSENT/ABSENT | free of melanoma

## resolved back nodule
- Scope: LESION
- Roles: REGRESSING_TARGET
- Observation 262: Fibrosis in resolved back nodule | REPORTED/PRESENT | fibrosis
- Observation 263: Disease in resolved back nodule biopsy | REPORTED_ABSENT/ABSENT | no disease

## right anterior tibial area longstanding nevus
- Scope: LESION
- Roles: UNKNOWN
- Observation 233: Primary nevus local irritation, ulceration, and bleeding | REPORTED/PRESENT | local irritation ... progressed to ulceration and bleeding over several months

## right anterior tibial area primary lesion
- Scope: LESION
- Roles: UNKNOWN
- Observation 234: Primary lesion diagnosis | REPORTED/PRESENT | malignant melanoma
- Observation 235: Primary melanoma depth | REPORTED/PRESENT | 2 mm

## right external iliac lymph node
- Scope: LYMPH_NODE
- Roles: UNKNOWN
- Observation 256: Right external iliac lymph node enlargement | REPORTED/PRESENT | enlarged 15×13-mm right external iliac lymph node

## right inguinal lymph nodes
- Scope: LYMPH_NODE
- Roles: UNKNOWN
- Observation 239: Right inguinal lymph node involvement | REPORTED/PRESENT | involvement in 1 of 6 lymph nodes

## right-middle-lobe lung nodules
- Scope: LESION
- Roles: UNKNOWN
- Observation 255: Right middle lobe lung nodules | REPORTED/PRESENT | new right-middle-lobe lung nodules measuring up to 3.5 mm in diameter

## sentinel node
- Scope: LYMPH_NODE
- Roles: UNKNOWN
- Observation 238: Sentinel lymph node focus of disease | REPORTED/PRESENT | 1-mm focus of disease

## upper lateral right thigh subcutaneous nodules
- Scope: LESION
- Roles: UNKNOWN
- Observation 246: Additional upper lateral right thigh subcutaneous nodules | REPORTED/PRESENT | Two other similar subcutaneous nodules

## upper right thigh in-transit metastases
- Scope: LESION
- Roles: UNKNOWN
- Observation 244: Upper right thigh in-transit metastases | REPORTED/PRESENT | multiple (approximately 15) in-transit metastases
- Observation 245: Upper right thigh in-transit metastasis morphology and size | REPORTED/DECREASED | erythematous lesions ranged in size from 1 mm to 10 mm

## upper right thigh in-transit metastases and upper lateral right thigh subcutaneous nodules
- Scope: LESION
- Roles: UNKNOWN
- Observation 247: Response of thigh lesions to palliative radiotherapy | REPORTED/DECREASED | good response

# Biological States

## Observation 243: Liver enzymes
- Category: OTHER
- Value: a slight elevation of liver enzymes
- Status / direction: REPORTED / INCREASED
- Semantics: LAB_MEASUREMENT
- Time relation: BEFORE_REGRESSION
- Scope / lesion: SYSTEMIC / NONE
- Regression role: UNKNOWN
  - Evidence 901: page 1, section Title, type OBSERVED_FACT
  - Quote: "a slight elevation of liver enzymes."

## Observation 262: Fibrosis in resolved back nodule
- Category: PATHOLOGIC
- Value: fibrosis
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / resolved back nodule
- Regression role: REGRESSING_TARGET
  - Evidence 920: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "A biopsy of a resolved nodule on the patient’s back showed fibrosis, but no disease."

## Observation 263: Disease in resolved back nodule biopsy
- Category: PATHOLOGIC
- Value: no disease
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / resolved back nodule
- Regression role: REGRESSING_TARGET
  - Evidence 921: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "A biopsy of a resolved nodule on the patient’s back showed fibrosis, but no disease."

# Disease Phenotypes

## Observation 236: Clinical signs of disease or metastases
- Category: OTHER
- Value: No other clinical signs of disease or metastases were evident
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 894: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "No other clinical signs of disease or metastases were evident."

## Observation 238: Sentinel lymph node focus of disease
- Category: PATHOLOGIC
- Value: 1-mm focus of disease
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LYMPH_NODE / sentinel node
- Regression role: UNKNOWN
  - Evidence 896: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "the sentinel node biopsy showed a 1-mm focus of disease."

## Observation 240: Distant metastasis on clinical examination and CT
- Category: OTHER
- Value: no evidence of distant metastasis
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 898: page 1, section Title, type OBSERVED_FACT
  - Quote: "Clinical examination and computed tomography imaging showed no evidence of distant metastasis."

## Observation 244: Upper right thigh in-transit metastases
- Category: OTHER
- Value: multiple (approximately 15) in-transit metastases
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / upper right thigh in-transit metastases
- Regression role: UNKNOWN
  - Evidence 902: page 1, section Title, type OBSERVED_FACT
  - Quote: "the patient developed multiple (approximately 15) in-transit metastases in the upper right thigh."

## Observation 245: Upper right thigh in-transit metastasis morphology and size
- Category: OTHER
- Value: erythematous lesions ranged in size from 1 mm to 10 mm
- Status / direction: REPORTED / DECREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / upper right thigh in-transit metastases
- Regression role: UNKNOWN
  - Evidence 903: page 1, section Title, type OBSERVED_FACT
  - Quote: "These erythematous lesions ranged in size from 1 mm to 10 mm."

## Observation 246: Additional upper lateral right thigh subcutaneous nodules
- Category: OTHER
- Value: Two other similar subcutaneous nodules
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / upper lateral right thigh subcutaneous nodules
- Regression role: UNKNOWN
  - Evidence 904: page 1, section Title, type OBSERVED_FACT
  - Quote: "Two other similar subcutaneous nodules were also seen on the upper lateral aspect of the right thigh"

## Observation 250: Left axillary nodule size
- Category: OTHER
- Value: 5-mm axillary nodule
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / left axillary nodule
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 908: page 1, section Title, type OBSERVED_FACT
  - Quote: "a 5-mm axillary nodule"

## Observation 251: Additional cutaneous nodules
- Category: OTHER
- Value: a small nodule under the chin and on the central back
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: OTHER / under-chin nodule and central back nodule
- Regression role: UNKNOWN
  - Evidence 909: page 1, section Title, type OBSERVED_FACT
  - Quote: "a small nodule under the chin and on the central back."

## Observation 255: Right middle lobe lung nodules
- Category: OTHER
- Value: new right-middle-lobe lung nodules measuring up to 3.5 mm in diameter
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right-middle-lobe lung nodules
- Regression role: UNKNOWN
  - Evidence 913: page 1, section Title, type OBSERVED_FACT
  - Quote: "imaging showed new right-middle-lobe lung nodules measuring up to 3.5 mm in diameter"

## Observation 256: Right external iliac lymph node enlargement
- Category: OTHER
- Value: enlarged 15×13-mm right external iliac lymph node
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LYMPH_NODE / right external iliac lymph node
- Regression role: UNKNOWN
  - Evidence 914: page 1, section Title, type OBSERVED_FACT
  - Quote: "an enlarged 15×13-mm right external iliac lymph node."

## Observation 259: Clinical status of aforementioned nodules
- Category: OTHER
- Value: dramatic improvement in all of the aforementioned nodules
- Status / direction: REPORTED / DECREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 917: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "One week later, dramatic improvement in all of the aforementioned nodules was noted on clinical examination."

## Observation 260: Aortopulmonary window lymph node
- Category: OTHER
- Value: new 20-mm lymph node in the aortopulmonary window
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LYMPH_NODE / aortopulmonary-window lymph node
- Regression role: UNKNOWN
  - Evidence 918: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Computed tomography imaging showed a new 20-mm lymph node in the aortopulmonary window"

## Observation 261: New nodules on computed tomography
- Category: OTHER
- Value: several new nodules measuring 3–11 mm
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: OTHER / right middle lobe, right pectoral muscle, left axilla, left rectus abdominis, and subcutaneous fat overlying T3 spinous process nodules
- Regression role: UNKNOWN
  - Evidence 919: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "several new nodules measuring 3–11 mm in the right middle lobe, over the right pectoral muscle, in the left axilla, over the left rectus abdominis, and in the subcutaneous fat overlying the T3 spinous process."

## Observation 265: Size of nodules on repeat imaging
- Category: OTHER
- Value: progressive reduction in the size of the nodules
- Status / direction: REPORTED / DECREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 923: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Repeat imaging before study enrollment after another 3 months showed progressive reduction in the size of the nodules."

## Observation 266: Nodule status
- Category: OTHER
- Value: all of the nodules had vanished
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 924: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Two months later, all of the nodules had vanished, except for an enlarged nodule in the left axilla."

## Observation 267: Left axillary nodule enlargement
- Category: OTHER
- Value: enlarged nodule in the left axilla
- Status / direction: REPORTED / INCREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / left axillary nodule
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 925: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "all of the nodules had vanished, except for an enlarged nodule in the left axilla."

## Observation 268: Left axillary lymph node size
- Category: OTHER
- Value: 10-mm lymph node
- Status / direction: REPORTED / UNKNOWN
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LYMPH_NODE / left axillary lymph node
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 926: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "One month later, the 10-mm lymph node in the left axilla was resected."

# Diagnostic Evidence

## Observation 234: Primary lesion diagnosis
- Category: PATHOLOGIC
- Value: malignant melanoma
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right anterior tibial area primary lesion
- Regression role: UNKNOWN
  - Evidence 892: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "subsequent analysis showed malignant melanoma"

## Observation 235: Primary melanoma depth
- Category: PATHOLOGIC
- Value: 2 mm
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right anterior tibial area primary lesion
- Regression role: UNKNOWN
  - Evidence 893: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "malignant melanoma characterized by a depth of 2 mm"

## Observation 237: Melanoma at primary resection site
- Category: PATHOLOGIC
- Value: free of melanoma
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / primary lesion resection site
- Regression role: UNKNOWN
  - Evidence 895: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "The site of the primary lesion was free of melanoma."

## Observation 239: Right inguinal lymph node involvement
- Category: PATHOLOGIC
- Value: involvement in 1 of 6 lymph nodes
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LYMPH_NODE / right inguinal lymph nodes
- Regression role: UNKNOWN
  - Evidence 897: page 1, section Title, type OBSERVED_FACT
  - Quote: "a right inguinal lymph node dissection revealed involvement in 1 of 6 lymph nodes."

## Observation 241: Disease stage
- Category: OTHER
- Value: T2bN1aM0 stage iiib disease
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 899: page 1, section Title, type OBSERVED_FACT
  - Quote: "The patient was considered to have T2bN1aM0 stage iiib disease."

## Observation 248: Recurrence on follow-up imaging
- Category: OTHER
- Value: no other recurrence
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: IMAGING_PROXY
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 906: page 1, section Title, type OBSERVED_FACT
  - Quote: "Follow-up imaging showed no other recurrence."

## Observation 252: Chest lesion diagnosis
- Category: PATHOLOGIC
- Value: melanoma
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / nodule above left nipple chest lesion
- Regression role: UNKNOWN
  - Evidence 910: page 1, section Title, type OBSERVED_FACT
  - Quote: "The chest lesion was excised and proved to be melanoma."

## Observation 253: Left axillary nodule pathology
- Category: PATHOLOGIC
- Value: malignant non-melanin tumour
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / left axillary nodule
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 911: page 1, section Title, type OBSERVED_FACT
  - Quote: "A punch biopsy of the left axillary nodule revealed a malignant non-melanin tumour."

## Observation 254: Left axillary nodule melanoma immunohistochemistry
- Category: PATHOLOGIC
- Value: positive for S100, mart-1, and tyrosinase, and negative for HMB45
- Status / direction: REPORTED / MIXED
- Semantics: PATHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / left axillary nodule
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 912: page 1, section Title, type OBSERVED_FACT
  - Quote: "Immunohistochemistry for melanoma was positive for S100, mart-1, and tyrosinase, and negative for HMB45"

## Observation 257: Disease stage
- Category: OTHER
- Value: stage iv disease
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 915: page 1, section Title, type OBSERVED_FACT
  - Quote: "Investigations were initiated for enrollment in a trial for what was now stage iv disease."

## Observation 264: Human leukocyte antigen typing
- Category: GENETIC
- Value: hla-A2, -A29, -B8, -B44, and -CW7
- Status / direction: REPORTED / PRESENT
- Semantics: DIRECT_MEASUREMENT
- Time relation: DURING_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 922: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "The patient underwent human leukocyte antigen (hla) typing in anticipation of being enrolled in a trial for MDX-10 (currently known as ipilimumab), which yielded hla-A2, -A29, -B8, -B44, and -CW7."

## Observation 269: Resected left axillary lymph node diagnosis
- Category: PATHOLOGIC
- Value: melanoma
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LYMPH_NODE / left axillary lymph node
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 927: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "The surgical specimen showed melanoma"

## Observation 270: Resected left axillary lymph node melanoma immunohistochemistry
- Category: PATHOLOGIC
- Value: positive for S100, mart-1, and tyrosinase, and negative for HMB45
- Status / direction: REPORTED / MIXED
- Semantics: PATHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LYMPH_NODE / left axillary lymph node
- Regression role: PROGRESSING_NON_TARGET
  - Evidence 928: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "which again stained positive for S100, mart-1, and tyrosinase, and negative for HMB45."

## Observation 271: Disease status on regular clinic visits and imaging
- Category: OTHER
- Value: disease-free state
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: IMAGING_PROXY
- Time relation: AFTER_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 929: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "This patient has since been regularly followed with clinic visits and imaging that continues to demonstrate a disease-free state."

# Clinical Context

## Observation 233: Primary nevus local irritation, ulceration, and bleeding
- Category: PATHOLOGIC
- Value: local irritation ... progressed to ulceration and bleeding over several months
- Status / direction: REPORTED / PRESENT
- Semantics: SYMPTOM
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right anterior tibial area longstanding nevus
- Regression role: UNKNOWN
  - Evidence 891: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "developed local irritation of a longstanding nevus on the right anterior tibial area, which progressed to ulceration and bleeding over several months."

## Observation 242: Symptoms during interferon alfa regimen
- Category: OTHER
- Value: muscle pain, diarrhea, fever, and occasional headaches
- Status / direction: REPORTED / PRESENT
- Semantics: SYMPTOM
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 900: page 1, section Title, type OBSERVED_FACT
  - Quote: "some symptoms of muscle pain, diarrhea, fever, and occasional headaches"

## Observation 249: Tender chest nodule
- Category: OTHER
- Value: tender 5-mm nodule above the left nipple
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / nodule above left nipple
- Regression role: UNKNOWN
  - Evidence 907: page 1, section Title, type OBSERVED_FACT
  - Quote: "the patient developed a tender 5-mm nodule above the left nipple"

## Observation 258: Post-Adacel reaction
- Category: OTHER
- Value: local and systemic febrile reaction that lasted 2 days
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: PATIENT / NONE
- Regression role: UNKNOWN
  - Evidence 916: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "The patient developed a local and systemic febrile reaction that lasted 2 days."

# Treatment Response

## Observation 247: Response of thigh lesions to palliative radiotherapy
- Category: OTHER
- Value: good response
- Status / direction: REPORTED / DECREASED
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / upper right thigh in-transit metastases and upper lateral right thigh subcutaneous nodules
- Regression role: UNKNOWN
  - Evidence 905: page 1, section Title, type OBSERVED_FACT
  - Quote: "The patient underwent palliative radiotherapy of 40 Gy in 10 fractions to each nodule and 30 Gy in 10 fractions to the intervening skin, with good response."

# Confounder Register

Presence records temporal co-occurrence only and is not a causal assignment.

## prior immunotherapy
- Status: PRESENT
- Temporal relation: BEFORE; One month later
  - Evidence 869: page 1, section Title, type OBSERVED_FACT
  - Quote: "One month later, the patient started a 4-week induction course of adjuvant high-dose interferon alfa at a daily dose of 36×106 U intravenously 5 days per week, followed by an 11-month course of 18×106 U interferon alfa 3 times weekly subcutaneously for maintenance."
- Temporal relation: BEFORE; during the interferon regimen
  - Evidence 870: page 1, section Title, type OBSERVED_FACT
  - Quote: "He tolerated this regimen well, with some symptoms of muscle pain, diarrhea, fever, and occasional headaches in addition to a slight elevation of liver enzymes."
- Temporal relation: BEFORE; after follow-up imaging showed no other recurrence
  - Evidence 873: page 1, section Title, type OBSERVED_FACT
  - Quote: "Follow-up imaging showed no other recurrence. The patient completed his 1-year course of interferon."

## recent surgery
- Status: PRESENT
- Temporal relation: BEFORE; Five months from initial presentation
  - Evidence 866: page 1, section Abstract, type OBSERVED_FACT
  - Quote: "Five months from initial presentation, a sentinel node biopsy and repeat resection of the primary site, with 1 cm margins, was performed. The site of the primary lesion was free of melanoma. However, the sentinel node biopsy showed a 1-mm focus of disease."
- Temporal relation: BEFORE; After 3 months
  - Evidence 867: page 1, section Title, type OBSERVED_FACT
  - Quote: "After 3 months, a right inguinal lymph node dissection revealed involvement in 1 of 6 lymph nodes."
- Temporal relation: DURING; One month later
  - Evidence 885: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "One month later, the 10-mm lymph node in the left axilla was resected."

## biopsy
- Status: PRESENT
- Temporal relation: BEFORE; Six months after the course of interferon
  - Evidence 875: page 1, section Title, type AUTHOR_INTERPRETATION
  - Quote: "The chest lesion was excised and proved to be melanoma. A punch biopsy of the left axillary nodule revealed a malignant non-melanin tumour. Immunohistochemistry for melanoma was positive for S100, mart-1, and tyrosinase, and negative for HMB45, suggesting metastatic disease1."
- Temporal relation: DURING; after clinical improvement and CT imaging
  - Evidence 882: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "A biopsy of a resolved nodule on the patient’s back showed fibrosis, but no disease."
- Temporal relation: DURING; at left axillary lymph-node resection
  - Evidence 886: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "The surgical specimen showed melanoma, which again stained positive for S100, mart-1, and tyrosinase, and negative for HMB45."

## infection
- Status: NOT_REPORTED
- Temporal relation: UNKNOWN
- Evidence: NONE

## vaccination
- Status: PRESENT
- Temporal relation: BEFORE; Three months later
  - Evidence 878: page 2, section Abstract, type OBSERVED_FACT
  - Quote: "Three months later, the patient received Adacel vaccine (Sanofi Pasteur, Lyon, France) as a routine preventive measure."

## radiotherapy
- Status: PRESENT
- Temporal relation: BEFORE; after development of in-transit metastases
  - Evidence 872: page 1, section Title, type OBSERVED_FACT
  - Quote: "The patient underwent palliative radiotherapy of 40 Gy in 10 fractions to each nodule and 30 Gy in 10 fractions to the intervening skin, with good response."

## systemic therapy
- Status: PRESENT
- Temporal relation: BEFORE; One month later
  - Evidence 869: page 1, section Title, type OBSERVED_FACT
  - Quote: "One month later, the patient started a 4-week induction course of adjuvant high-dose interferon alfa at a daily dose of 36×106 U intravenously 5 days per week, followed by an 11-month course of 18×106 U interferon alfa 3 times weekly subcutaneously for maintenance."
- Temporal relation: BEFORE; during the interferon regimen
  - Evidence 870: page 1, section Title, type OBSERVED_FACT
  - Quote: "He tolerated this regimen well, with some symptoms of muscle pain, diarrhea, fever, and occasional headaches in addition to a slight elevation of liver enzymes."
- Temporal relation: BEFORE; after follow-up imaging showed no other recurrence
  - Evidence 873: page 1, section Title, type OBSERVED_FACT
  - Quote: "Follow-up imaging showed no other recurrence. The patient completed his 1-year course of interferon."

## alternative treatment
- Status: NOT_REPORTED
- Temporal relation: UNKNOWN
- Evidence: NONE

## other major clinical intervention
- Status: NOT_REPORTED
- Temporal relation: UNKNOWN
- Evidence: NONE

# Author Interpretations

## Interpretation 1
- Statement: Immunohistochemistry for melanoma was positive for S100, mart-1, and tyrosinase, and negative for HMB45, suggesting metastatic disease1.
- Rejection reason: The phrase "suggesting metastatic disease" is an author interpretation rather than a directly observed finding.
- Page / section: 1 / Title
- Quote: "Immunohistochemistry for melanoma was positive for S100, mart-1, and tyrosinase, and negative for HMB45, suggesting metastatic disease1."

## Interpretation 2
- Statement: Although a second primary tumor cannot be ruled out, it is highly unlikely.
- Rejection reason: This is an explicitly uncertain author interpretation regarding the origin of the tumor.
- Page / section: 2 / Abstract
- Quote: "Although a second primary tumor cannot be ruled out, it is highly unlikely."

## Interpretation 3
- Statement: Of particular interest in this case is the preceding fever, which we attribute to the patient’s dtap inoculation.
- Rejection reason: Attribution of fever to vaccination is a causal interpretation.
- Page / section: 2 / Abstract
- Quote: "Of particular interest in this case is the preceding fever, which we attribute to the patient’s dtap inoculation."

# Rejected Claims

## Rejected claim 1
- Phase: PHASE 2
- Field: case.melanoma_subtype
- Reason: Quote was not found in normalized paper text
- Page: 1
- Quote: "The lesion was excised by the patient’s family physician, and subsequent analysis showed malignant melanoma characterized by a depth of 2 mm and extension into the reticular dermis, consistent with a Clark level iii/iv."

## Rejected claim 2
- Phase: PHASE 2
- Field: event.description
- Reason: Quote was not found in normalized paper text
- Page: 1
- Quote: "The lesion was excised by the patient’s family physician, and subsequent analysis showed malignant melanoma characterized by a depth of 2 mm and extension into the reticular dermis, consistent with a Clark level iii/iv."

## Rejected claim 3
- Phase: PHASE 2
- Field: event.description
- Reason: Quote was not found in normalized paper text
- Page: 1
- Quote: "The lesion was excised by the patient’s family physician, and subsequent analysis showed malignant melanoma characterized by a depth of 2 mm and extension into the reticular dermis, consistent with a Clark level iii/iv."

## Rejected claim 4
- Phase: PHASE 3.1
- Field: biological_observation.Primary melanoma extension and Clark level
- Reason: Quote was not found in normalized paper text
- Page: 1
- Quote: "extension into the reticular dermis, consistent with a Clark level iii/iv."

# Validation Failures

- Four source quotes were rejected (three in PHASE 2 and one in PHASE 3.1), including a line-wrap/typography-sensitive primary-pathology sentence.
- A static 1-10 mm lesion-size range was assigned direction DECREASED even though it does not describe longitudinal change (observation 245).
- The reported relative regression-confirmation expression remained in field_statuses but could not be persisted in the date column.
- Patient-scoped phrases such as 'all aforementioned nodules' and 'all nodules had vanished' could not be mapped back to every lesion while new or persistent lesions coexisted.
- Equivalent entities were split across aliases (for example left axillary nodule versus left axillary lymph node, and chest-nodule variants), so the exact lesion-identifier count overstates distinct lesions.
- Biopsy findings 'fibrosis' and 'no disease' were represented with MORPHOLOGIC_FINDING semantics rather than PATHOLOGIC_FINDING.

# New Ontology Pressure Points

- Approximate or relative case dates need representation outside exact date columns without losing the reported value.
- Cross-sentence references such as 'aforementioned nodules' need explicit lesion-set identity and membership.
- A stable lesion identity is needed across nodule, lymph-node, biopsy, and resection wording variants.
- A static numeric range must be distinguishable from a temporal direction.
- Pathology provenance and pathology measurement semantics can diverge for generic terms such as fibrosis and no disease.
- A combined local-and-systemic reaction does not fit one unambiguous scope.

# Validation Summary

- PHASE 2 status/run: partial / 36
- PHASE 3.1 status/run: partial / 37
- Stable versions: phase2.2.2 / phase2.2-adjudication-v4 / case v5 / timeline v3; phase3.1 / phase3.1-ontology-v4 / biological v2
- Case count: 1
- Event count: 23
- Exact lesion identifier count: 16
- Biological State count: 3
- Disease Phenotype count: 17
- Clinical Context count: 4
- Diagnostic Evidence count: 14
- Treatment Response count: 1
- Verified Evidence count: 97
- Rejected Evidence count: 3
- Quote failure count: 4
- Case UNCERTAIN/CONFLICTING count: 3
- Observation UNCERTAIN/CONFLICTING count: 0
- UNKNOWN direction count: 1
- UNKNOWN regression-role count: 30
- Ontology pressure point count: 6
