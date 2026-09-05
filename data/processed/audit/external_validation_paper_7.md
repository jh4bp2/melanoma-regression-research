# External Validation Audit

- Paper ID: 7
- Title: Case Report: Shadows of disappearance: the enigma of completely regressed cutaneous melanoma revealed by lymph node metastasis
- DOI / PMID: 10.3389/fonc.2025.1671450 / 41103958
- PHASE 2 run: 55 (phase2.2.2 / phase2.2-adjudication-v4)
- PHASE 3 runs: 56 case 10, 57 case 11
- Stable versions: schema phase2.2.2 / rule phase2.2-adjudication-v4; schema phase3.2 / rule phase3.2-ontology-v1 / prompt biological_observation_extraction:v3
- Validation-set rule: record mismatches without adapting ontology, schema, rule, or prompts. Selection rationale is research metadata only and was not preloaded into Case / Evidence / BiologicalObservation.
- PHASE 4 / Pattern Discovery / Public Hypothesis / Evidence Graph were not started.

# Case Summary — Case 10

- Case ID: 10
- Patient identifier: Patient A
- Age / sex: 71 / male
- Melanoma subtype: NOT STORED
- Primary site: NOT STORED
- Stage: NOT STORED
- Metastatic sites: right inguinal lymph nodes
- First observed reduction: recently considered to be in a “recovery” phase
- Regression confirmation: NOT STORED
- Regression extent: COMPLETE
- Treatment before regression: NOT STORED
- Preceding events: Treatment for onychomycosis of one toe for approximately two years
- Outcome: Metastatic malignant melanoma within lymph nodes was diagnosed

## Case Field Statuses

- patient_identifier: REPORTED | raw value: Patient A
- age: REPORTED | raw value: 71
- sex: REPORTED | raw value: male
- melanoma_subtype: UNCERTAIN | raw value: subungual melanoma
- primary_site: UNCERTAIN | raw value: one toe (suspected subungual lesion)
- stage: NOT_REPORTED | raw value: None
- metastatic_sites: REPORTED | raw value: ['right inguinal lymph nodes']
- diagnosis_date: NOT_REPORTED | raw value: None
- regression_start_date: NOT_REPORTED | raw value: None
- first_observed_reduction: REPORTED | raw value: recently considered to be in a “recovery” phase
- regression_confirmed_date: NOT_REPORTED | raw value: None
- regression_duration: NOT_REPORTED | raw value: None
- regression_type: REPORTED | raw value: complete regression of primary cutaneous melanoma
- regression_extent_clinical: REPORTED | raw value: COMPLETE
- viable_tumor_at_pathology: REPORTED | raw value: PRESENT
- treatment_before_regression: UNCERTAIN | raw value: No prior immunotherapy or other biologic treatments before the diagnosis of melanoma
- treatment_status: UNCERTAIN | raw value: unknown
- preceding_events: REPORTED | raw value: ['Treatment for onychomycosis of one toe for approximately two years']
- outcome: REPORTED | raw value: Metastatic malignant melanoma within lymph nodes was diagnosed
- follow_up_duration: NOT_REPORTED | raw value: None

# Timeline

## Event 300: treatment
- Description: Patient A had been treated for onychomycosis of one toe for approximately two years; the condition was recently considered to be in a “recovery” phase.
- Event date: NONE
- Relative time: for approximately two years; recently considered to be in a “recovery” phase
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1483: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient A had been treated for onychomycosis of one toe for approximately two years, and the condition was recently considered to be in a “recovery” phase."

## Event 301: tumor_progression
- Description: Patient A presented with a one-month history of a progressively enlarging, painless right inguinal mass.
- Event date: NONE
- Relative time: one-month history
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1484: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient A, a 71-year-old male, presented with a one-month history of a progressively enlarging, painless mass in the right inguinal region."

## Event 302: metastasis
- Description: Right groin ultrasonography showed multiple enlarged lymph nodes; the largest measured 4.4 cm × 3.2 cm × 2.3 cm and had hypoechoic features, ill-defined margins, internal heterogeneity, and focal cystic degeneration.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1485: page 2, section Title, type OBSERVED_FACT
  - Quote: "Ultrasonography of the groin demonstrated multiple enlarged lymph nodes, the largest measuring 4.4 cm× 3.2 cm × 2.3 cm. This dominant node exhibited hypoechoic features with ill-deﬁned margins, internal heterogeneity, and focal cystic degeneration."

## Event 303: fever
- Description: Patient A had isolated, localized lymphadenopathy without accompanying fever.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1486: page 2, section Title, type OBSERVED_FACT
  - Quote: "Both patients presented with isolated, localized lymphadenopathy without accompanying fever."

## Event 304: tumor_regression
- Description: The affected toenail was dystrophic and irregular, with surrounding marked hypopigmentation measuring approximately 0.8 cm × 0.5 cm and scattered perilesional freckles; dermatologic assessment clinically supported completely regressed primary melanoma, without biopsy of the regressed cutaneous lesion.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: DURING
  - Evidence 1487: page 2, section Title, type OBSERVED_FACT
  - Quote: "The affected toenail appeared dystrophic and irregular, with surrounding skin exhibiting marked hypopigmentation, measuring approximately 0.8 cm × 0.5 cm while multiple scattered freckles were observed in the perilesional area (Figure 1)."
  - Evidence 1488: page 4, section Discussion, type OBSERVED_FACT
  - Quote: "Although neither patient underwent biopsy of the regressed cutaneous lesions, the dermatologic assessment - performed by an experienced specialist - clinically supported the diagnosis of completely regressed primary melanoma."

## Event 305: biopsy
- Description: Fine needle aspiration of the affected lymph nodes was requested to determine the etiology of lymphadenopathy.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1489: page 2, section Title, type OBSERVED_FACT
  - Quote: "To elucidate the etiology of lymphadenopathy, clinicians requested ﬁne needle aspiration (FNA) of the affected lymph nodes."

## Event 306: diagnosis
- Description: Cell-block immunohistochemistry showed strong positivity for Vimentin, Melan-A, HMB45, and SOX10, with negative LCA, CgA, Syn, PLAP, and CK; molecular testing showed BRAF V600E wild type. These findings established metastatic malignant melanoma within the lymph nodes.
- Event date: NONE
- Relative time: following fine needle aspiration
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1490: page 3, section Title, type OBSERVED_FACT
  - Quote: "Immunohistochemical (IHC) analysis (Figures 3, 4) demonstrated strong positivity for Vimentin, Melan-A, HMB45, and SOX10, conﬁrming melanocytic differentiation. Conversely, markers including leukocyte common antigen (LCA), chromogranin A (CgA), synaptophysin (Syn), placental alkaline phosphatase (PLAP), and cytokeratin (CK) were negative, effectively excluding lymphoid, neuroendocrine, germ cell, and epithelial neoplasms. Molecular testing for the BRAF V600E mutation yielded wild type. Collectively, these ﬁndings established the diagnosis of metastatic malignant melanoma within the lymph nodes of both patients."

# Lesion Map

## Lesion 24: skin lesion
- Identity key: UNK|SKIN|UNK|LESION|NONE|NONE|SINGLE
- Type: LESION
- Laterality: NONE
- Organ / location: SKIN / NONE
- Aliases: affected toe cutaneous lesion [CONFIRMED_ALIAS]
- Observation 409: onychomycosis treatment | CLINICAL_CONTEXT | REPORTED/UNKNOWN | treated for onychomycosis of one toe for approximately two years

# Biological States

None.

# Disease Phenotypes

None.

# Diagnostic Evidence

None.

# Clinical Context

## Observation 409: onychomycosis treatment
- Category: OTHER
- Value: treated for onychomycosis of one toe for approximately two years
- Status / direction: REPORTED / UNKNOWN
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LESION / affected toe cutaneous lesion
- Lesion ID / collection ID: 24 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1525: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient A had been treated for onychomycosis of one toe for approximately two years"

# Treatment Response

None.

# Genotype Observations

None.

# Explanatory Alternatives

None.

# Author Interpretations

None.

# Case Summary — Case 11

- Case ID: 11
- Patient identifier: Patient B
- Age / sex: 73 / female
- Melanoma subtype: NOT STORED
- Primary site: tip of the right fifth digit
- Stage: NOT STORED
- Metastatic sites: right axillary lymph nodes
- First observed reduction: Recently, the lesion underwent an abrupt and near-complete resolution.
- Regression confirmation: NOT STORED
- Regression extent: NOT STORED
- Treatment before regression: NOT STORED
- Preceding events: Long-standing recurrent fluid-filled lesions at the tip of the right fifth digit
- Outcome: Metastatic malignant melanoma within lymph nodes was diagnosed

## Case Field Statuses

- patient_identifier: REPORTED | raw value: Patient B
- age: REPORTED | raw value: 73
- sex: REPORTED | raw value: female
- melanoma_subtype: NOT_REPORTED | raw value: None
- primary_site: REPORTED | raw value: tip of the right fifth digit
- stage: NOT_REPORTED | raw value: None
- metastatic_sites: REPORTED | raw value: ['right axillary lymph nodes']
- diagnosis_date: NOT_REPORTED | raw value: None
- regression_start_date: NOT_REPORTED | raw value: None
- first_observed_reduction: REPORTED | raw value: Recently, the lesion underwent an abrupt and near-complete resolution.
- regression_confirmed_date: NOT_REPORTED | raw value: None
- regression_duration: NOT_REPORTED | raw value: None
- regression_type: REPORTED | raw value: spontaneous regression
- regression_extent_clinical: CONFLICTING | raw value: None
- viable_tumor_at_pathology: REPORTED | raw value: PRESENT
- treatment_before_regression: UNCERTAIN | raw value: No prior immunotherapy or other biologic treatments before the diagnosis of melanoma
- treatment_status: UNCERTAIN | raw value: unknown
- preceding_events: REPORTED | raw value: ['Long-standing recurrent fluid-filled lesions at the tip of the right fifth digit']
- outcome: REPORTED | raw value: Metastatic malignant melanoma within lymph nodes was diagnosed
- follow_up_duration: NOT_REPORTED | raw value: None

# Timeline

## Event 307: other
- Description: Patient B reported a long-standing history of recurrent fluid-filled lesions at the tip of the right fifth digit.
- Event date: NONE
- Relative time: long-standing history
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 1510: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient B reported a long-standing history of recurrent ﬂuid-ﬁlled lesions at the tip of the right ﬁfth digit."

## Event 308: other
- Description: The affected right fifth fingertip area had previously appeared blackened, resembling a crush injury; the lesion had no nail involvement.
- Event date: NONE
- Relative time: previously
- Stored/source precision: unknown / RELATIVE
- Relation to regression: BEFORE
  - Evidence 1511: page 2, section Title, type OBSERVED_FACT
  - Quote: "The patient recalled that the affected area previously appeared blackened, resembling a crush injury."
  - Evidence 1512: page 4, section Discussion, type OBSERVED_FACT
  - Quote: "In patient B, the lesion at the tip of the digit appeared blackened, resembling a crush injury, without nail involvement."

## Event 309: tumor_regression
- Description: The lesion at the right fifth fingertip underwent abrupt and near-complete resolution; currently the skin was abnormally hypopigmented and regenerated in texture, measuring approximately 0.7 cm × 0.6 cm.
- Event date: NONE
- Relative time: Recently
- Stored/source precision: unknown / RELATIVE
- Relation to regression: DURING
  - Evidence 1513: page 2, section Title, type OBSERVED_FACT
  - Quote: "Recently, the lesion underwent an abrupt and near-complete resolution."
  - Evidence 1514: page 2, section Title, type OBSERVED_FACT
  - Quote: "Currently, the skin over the right ﬁfth ﬁngertip appears abnormally hypopigmented and regenerated in texture, resembling newly formed skin, with an area measuring approximately 0.7 cm × 0.6 cm."

## Event 310: diagnosis
- Description: Dermatologic assessment by an experienced specialist clinically supported the diagnosis of completely regressed primary melanoma; the regressed cutaneous lesion was not biopsied.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: DURING
  - Evidence 1515: page 4, section Discussion, type OBSERVED_FACT
  - Quote: "Although neither patient underwent biopsy of the regressed cutaneous lesions, the dermatologic assessment - performed by an experienced specialist - clinically supported the diagnosis of completely regressed primary melanoma."

## Event 311: other
- Description: Patient B presented with unexplained right axillary lymphadenopathy; ultrasonography showed multiple hypoechoic right axillary nodules, with the largest measuring 4.2 cm × 3.4 cm × 3.0 cm and having an irregular contour and heterogeneous internal echotexture.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1516: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient B, a 73-year-old elderly female, presented with unexplained lymphadenopathy in the right axillary region. Ultrasonographic examination revealed multiple hypoechoic nodules within the right axilla. The largest measured 4.2 cm × 3.4 cm × 3.0 cm and demonstrated an irregular contour with heterogeneous internal echotexture."
  - Evidence 1517: page 4, section Discussion, type OBSERVED_FACT
  - Quote: "Subsequent enlargement of regional lymph nodes prompted medical evaluation, but initial presentation to non-dermatologic specialties highlighted limitations in melanoma recognition, particularly in regressed forms."

## Event 312: biopsy
- Description: Fine needle aspiration of the right axillary lymph node yielded a small amount of dark, turbid fluid.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1518: page 2, section Title, type OBSERVED_FACT
  - Quote: "To elucidate the etiology of lymphadenopathy, clinicians requested ﬁne needle aspiration (FNA) of the affected lymph nodes."
  - Evidence 1519: page 2, section Title, type OBSERVED_FACT
  - Quote: "In patient B (Figure 2B), aspiration of the right axillary lymph node yielded a small amount of dark, turbid ﬂuid."

## Event 313: metastasis
- Description: Metastatic malignant melanoma was established within the lymph nodes, supported by cytology showing malignant tumor cells with melanin pigment and by melanocytic immunohistochemical marker positivity.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1520: page 3, section Title, type OBSERVED_FACT
  - Quote: "The cytoplasmic volume ranged from scant to abundant and contained variable amounts of coarse melanin pigment granules. Mitotic ﬁgures, including atypical forms, were evident."
  - Evidence 1521: page 3, section Title, type OBSERVED_FACT
  - Quote: "Immunohistochemical (IHC) analysis (Figures 3, 4) demonstrated strong positivity for Vimentin, Melan-A, HMB45, and SOX10, conﬁrming melanocytic differentiation."
  - Evidence 1522: page 3, section Title, type OBSERVED_FACT
  - Quote: "Collectively, these ﬁndings established the diagnosis of metastatic malignant melanoma within the lymph nodes of both patients."

## Event 314: diagnosis
- Description: Metastatic malignant melanoma within the lymph nodes was diagnosed.
- Event date: NONE
- Relative time: NONE
- Stored/source precision: unknown / UNKNOWN
- Relation to regression: UNKNOWN
  - Evidence 1523: page 3, section Title, type OBSERVED_FACT
  - Quote: "Collectively, these ﬁndings established the diagnosis of metastatic malignant melanoma within the lymph nodes of both patients."

## Event 315: treatment
- Description: Before the diagnosis of melanoma, the patient had not received prior immunotherapy or other biologic treatments.
- Event date: NONE
- Relative time: before the diagnosis of melanoma
- Stored/source precision: unknown / RELATIVE
- Relation to regression: UNKNOWN
  - Evidence 1524: page 3, section Title, type OBSERVED_FACT
  - Quote: "In both cases, the patients had not received prior immunotherapy or other biologic treatments before the diagnosis of melanoma."

# Lesion Map

## Lesion 25: right axilla lymph node lymph node
- Identity key: RIGHT|LYMPH_NODE|AXILLA|LYMPH_NODE|NONE|NONE|SINGLE
- Type: LYMPH_NODE
- Laterality: RIGHT
- Organ / location: LYMPH_NODE / AXILLA
- Aliases: right axillary lymph nodes [CONFIRMED_ALIAS]; right axillary lymph nodes [CONFIRMED_ALIAS]
- Observation 410: right axillary lymphadenopathy | CLINICAL_CONTEXT | REPORTED/PRESENT | unexplained lymphadenopathy in the right axillary region
- Observation 411: right axillary nodules on ultrasonography | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | multiple hypoechoic nodules within the right axilla
- Observation 420: aspirated right axillary lymph node fluid | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | a small amount of dark, turbid fluid
- Observation 421: right axillary lymph node cytology background | BIOLOGICAL_STATE | REPORTED/PRESENT | a markedly diminished lymphocytic component amidst a necrotic and necroinflammatory background
- Observation 422: right axillary lymph node malignant tumor cells | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | malignant tumor cells were observed either as isolated single cells or loosely cohesive small clusters, characterized by a high nuclear-to-cytoplasmic ratio
- Observation 423: melanin pigment in right axillary lymph node tumor cells | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | variable amounts of coarse melanin pigment granules
- Observation 424: right axillary lymph node immunohistochemistry | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | strong positivity for Vimentin, Melan-A, HMB45, and SOX10
- Observation 425: right axillary lymph node negative immunohistochemical markers | DIAGNOSTIC_EVIDENCE | REPORTED_ABSENT/ABSENT | leukocyte common antigen (LCA), chromogranin A (CgA), synaptophysin (Syn), placental alkaline phosphatase (PLAP), and cytokeratin (CK) were negative
- Observation 426: BRAF V600E mutation status | DIAGNOSTIC_EVIDENCE | REPORTED/UNKNOWN | wild type
- Observation 427: lymph node diagnosis | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | metastatic malignant melanoma within the lymph nodes

## Lesion 26: right axilla lymph node nodule
- Identity key: RIGHT|LYMPH_NODE|AXILLA|NODULE|NONE|NONE|SINGLE
- Type: NODULE
- Laterality: RIGHT
- Organ / location: LYMPH_NODE / AXILLA
- Aliases: largest right axillary nodule [POSSIBLE_SAME_LESION]
- Observation 412: largest right axillary nodule size and morphology | DISEASE_PHENOTYPE | REPORTED/UNKNOWN | 4.2 cm × 3.4 cm × 3.0 cm; irregular contour with heterogeneous internal echotexture

## Lesion 27: right skin lesion
- Identity key: RIGHT|SKIN|UNK|LESION|NONE|NONE|SINGLE
- Type: LESION
- Laterality: RIGHT
- Organ / location: SKIN / NONE
- Aliases: right fifth fingertip cutaneous lesion [CONFIRMED_ALIAS]; right fifth fingertip cutaneous lesion [CONFIRMED_ALIAS]
- Observation 415: recurrent fluid-filled lesions | CLINICAL_CONTEXT | REPORTED/PRESENT | long-standing history of recurrent fluid-filled lesions at the tip of the right fifth digit
- Observation 416: right fifth fingertip lesion resolution | DISEASE_PHENOTYPE | REPORTED/DECREASED | abrupt and near-complete resolution
- Observation 417: previous appearance of right fifth fingertip area | DISEASE_PHENOTYPE | REPORTED/PRESENT | appeared blackened, resembling a crush injury
- Observation 418: right fifth fingertip skin appearance and size | DISEASE_PHENOTYPE | REPORTED/PRESENT | abnormally hypopigmented and regenerated in texture, resembling newly formed skin, with an area measuring approximately 0.7 cm × 0.6 cm
- Observation 419: nail involvement | DISEASE_PHENOTYPE | REPORTED_ABSENT/ABSENT | without nail involvement
- Observation 428: dermatologic clinical assessment of regressed cutaneous lesion | DIAGNOSTIC_EVIDENCE | REPORTED/PRESENT | clinically supported the diagnosis of completely regressed primary melanoma

# Biological States

## Observation 421: right axillary lymph node cytology background
- Category: INFLAMMATORY
- Value: a markedly diminished lymphocytic component amidst a necrotic and necroinflammatory background
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: DIAGNOSTIC_EVIDENCE
  - Evidence 1539: page 2, section Title, type OBSERVED_FACT
  - Quote: "Cytological examination of the smear revealed a markedly diminished lymphocytic component amidst a necrotic and necroinflammatory background."

# Disease Phenotypes

## Observation 412: largest right axillary nodule size and morphology
- Category: PATHOLOGIC
- Value: 4.2 cm × 3.4 cm × 3.0 cm; irregular contour with heterogeneous internal echotexture
- Status / direction: REPORTED / UNKNOWN
- Semantics: MORPHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / largest right axillary nodule
- Lesion ID / collection ID: 26 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1530: page 2, section Title, type OBSERVED_FACT
  - Quote: "The largest measured 4.2 cm × 3.4 cm × 3.0 cm and demonstrated an irregular contour with heterogeneous internal echotexture."

## Observation 416: right fifth fingertip lesion resolution
- Category: PATHOLOGIC
- Value: abrupt and near-complete resolution
- Status / direction: REPORTED / DECREASED
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right fifth fingertip cutaneous lesion
- Lesion ID / collection ID: 27 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1534: page 2, section Title, type OBSERVED_FACT
  - Quote: "Recently, the lesion underwent an abrupt and near-complete resolution."

## Observation 417: previous appearance of right fifth fingertip area
- Category: PATHOLOGIC
- Value: appeared blackened, resembling a crush injury
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right fifth fingertip cutaneous lesion
- Lesion ID / collection ID: 27 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1535: page 2, section Title, type OBSERVED_FACT
  - Quote: "The patient recalled that the affected area previously appeared blackened, resembling a crush injury."

## Observation 418: right fifth fingertip skin appearance and size
- Category: PATHOLOGIC
- Value: abnormally hypopigmented and regenerated in texture, resembling newly formed skin, with an area measuring approximately 0.7 cm × 0.6 cm
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right fifth fingertip cutaneous lesion
- Lesion ID / collection ID: 27 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1536: page 2, section Title, type OBSERVED_FACT
  - Quote: "Currently, the skin over the right fifth fingertip appears abnormally hypopigmented and regenerated in texture, resembling newly formed skin, with an area measuring approximately 0.7 cm × 0.6 cm."

## Observation 419: nail involvement
- Category: PATHOLOGIC
- Value: without nail involvement
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right fifth fingertip cutaneous lesion
- Lesion ID / collection ID: 27 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1537: page 4, section Discussion, type OBSERVED_FACT
  - Quote: "In patient B, the lesion at the tip of the digit appeared blackened, resembling a crush injury, without nail involvement."

# Diagnostic Evidence

## Observation 411: right axillary nodules on ultrasonography
- Category: PATHOLOGIC
- Value: multiple hypoechoic nodules within the right axilla
- Status / direction: REPORTED / PRESENT
- Semantics: IMAGING_PROXY
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1529: page 2, section Title, type OBSERVED_FACT
  - Quote: "Ultrasonographic examination revealed multiple hypoechoic nodules within the right axilla."

## Observation 420: aspirated right axillary lymph node fluid
- Category: PATHOLOGIC
- Value: a small amount of dark, turbid fluid
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1538: page 2, section Title, type OBSERVED_FACT
  - Quote: "In patient B (Figure 2B), aspiration of the right axillary lymph node yielded a small amount of dark, turbid fluid."

## Observation 422: right axillary lymph node malignant tumor cells
- Category: PATHOLOGIC
- Value: malignant tumor cells were observed either as isolated single cells or loosely cohesive small clusters, characterized by a high nuclear-to-cytoplasmic ratio
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1540: page 2, section Title, type OBSERVED_FACT
  - Quote: "the malignant tumor cells were observed either as isolated single cells or loosely cohesive small clusters, characterized by a high nuclear-to-cytoplasmic ratio."

## Observation 423: melanin pigment in right axillary lymph node tumor cells
- Category: PATHOLOGIC
- Value: variable amounts of coarse melanin pigment granules
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1541: page 3, section Title, type OBSERVED_FACT
  - Quote: "The cytoplasmic volume ranged from scant to abundant and contained variable amounts of coarse melanin pigment granules."

## Observation 424: right axillary lymph node immunohistochemistry
- Category: PATHOLOGIC
- Value: strong positivity for Vimentin, Melan-A, HMB45, and SOX10
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1542: page 3, section Title, type OBSERVED_FACT
  - Quote: "Immunohistochemical (IHC) analysis (Figures 3, 4) demonstrated strong positivity for Vimentin, Melan-A, HMB45, and SOX10, confirming melanocytic differentiation."
  - Evidence 1543: page 6, section Discussion, type OBSERVED_FACT
  - Quote: "Tumor cells show strong positivity for melanocytic markers Vimentin, Melan-A, HMB45, and SOX10, confirming melanocytic differentiation. Negative staining for CK."

## Observation 425: right axillary lymph node negative immunohistochemical markers
- Category: PATHOLOGIC
- Value: leukocyte common antigen (LCA), chromogranin A (CgA), synaptophysin (Syn), placental alkaline phosphatase (PLAP), and cytokeratin (CK) were negative
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1544: page 3, section Title, type OBSERVED_FACT
  - Quote: "Conversely, markers including leukocyte common antigen (LCA), chromogranin A (CgA), synaptophysin (Syn), placental alkaline phosphatase (PLAP), and cytokeratin (CK) were negative, effectively excluding lymphoid, neuroendocrine, germ cell, and epithelial neoplasms."

## Observation 426: BRAF V600E mutation status
- Category: GENETIC
- Value: wild type
- Status / direction: REPORTED / UNKNOWN
- Semantics: DIRECT_MEASUREMENT
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: DIAGNOSTIC_EVIDENCE
  - Evidence 1545: page 3, section Title, type OBSERVED_FACT
  - Quote: "Molecular testing for the BRAF V600E mutation yielded wild type."

## Observation 427: lymph node diagnosis
- Category: PATHOLOGIC
- Value: metastatic malignant melanoma within the lymph nodes
- Status / direction: REPORTED / PRESENT
- Semantics: PATHOLOGIC_FINDING
- Time relation: AT_CONFIRMATION
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1546: page 3, section Title, type OBSERVED_FACT
  - Quote: "Collectively, these findings established the diagnosis of metastatic malignant melanoma within the lymph nodes of both patients."

## Observation 428: dermatologic clinical assessment of regressed cutaneous lesion
- Category: PATHOLOGIC
- Value: clinically supported the diagnosis of completely regressed primary melanoma
- Status / direction: REPORTED / PRESENT
- Semantics: MORPHOLOGIC_FINDING
- Time relation: DURING_REGRESSION
- Scope / lesion: LESION / right fifth fingertip cutaneous lesion
- Lesion ID / collection ID: 27 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1547: page 4, section Discussion, type OBSERVED_FACT
  - Quote: "Although neither patient underwent biopsy of the regressed cutaneous lesions, the dermatologic assessment - performed by an experienced specialist - clinically supported the diagnosis of completely regressed primary melanoma."

# Clinical Context

## Observation 410: right axillary lymphadenopathy
- Category: OTHER
- Value: unexplained lymphadenopathy in the right axillary region
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: LYMPH_NODE / right axillary lymph nodes
- Lesion ID / collection ID: 25 / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1528: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient B, a 73-year-old elderly female, presented with unexplained lymphadenopathy in the right axillary region."

## Observation 413: infectious diseases
- Category: OTHER
- Value: nor evidence of infectious diseases, including acquired immune deficiency syndrome (AIDS)
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: CLINICAL_FINDING
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1531: page 2, section Title, type OBSERVED_FACT
  - Quote: "Neither patient had a history of malignancy, immunosuppressive disorders, use of immunosuppressive agents, nor evidence of infectious diseases, including acquired immune deficiency syndrome (AIDS)."

## Observation 414: fever
- Category: OTHER
- Value: without accompanying fever
- Status / direction: REPORTED_ABSENT / ABSENT
- Semantics: SYMPTOM
- Time relation: UNKNOWN
- Scope / lesion: PATIENT / NONE
- Lesion ID / collection ID: NONE / NONE
- Regression role: UNKNOWN
- Domain secondary: NONE
  - Evidence 1532: page 2, section Title, type OBSERVED_FACT
  - Quote: "Both patients presented with isolated, localized lymphadenopathy without accompanying fever."

## Observation 415: recurrent fluid-filled lesions
- Category: OTHER
- Value: long-standing history of recurrent fluid-filled lesions at the tip of the right fifth digit
- Status / direction: REPORTED / PRESENT
- Semantics: CLINICAL_FINDING
- Time relation: BEFORE_REGRESSION
- Scope / lesion: LESION / right fifth fingertip cutaneous lesion
- Lesion ID / collection ID: 27 / NONE
- Regression role: REGRESSING_TARGET
- Domain secondary: NONE
  - Evidence 1533: page 2, section Title, type OBSERVED_FACT
  - Quote: "Patient B reported a long-standing history of recurrent fluid-filled lesions at the tip of the right fifth digit."

# Treatment Response

None.

# Genotype Observations

## Genotype 2: BRAF
- Variant: V600E
- State: MUTATED
- Linked observation: 426

# Explanatory Alternatives

None.

# Author Interpretations

## Interpretation 1
- Statement: Repeated external stimulation may have contributed to tumor progression, despite apparent clinical improvement reflecting spontaneous regression.
- Rejection reason: Author interpretation using "may have contributed" rather than a directly observed finding.
- Page / section: 4 / Discussion
- Quote: "Repeated external stimulation may have contributed to tumor progression, despite apparent clinical improvement reflecting spontaneous regression."

## Interpretation 2
- Statement: The presence of metastatic melanoma within a regional lymph node may serve as a catalyst for a systemic immune response, potentially resulting in the immunologic targeting and subsequent regression of the primary cutaneous lesion.
- Rejection reason: Mechanistic hypothesis using "may" and "potentially," not a direct observation in Patient B.
- Page / section: 7 / Discussion
- Quote: "The presence of metastatic melanoma within a regional lymph node may serve as a catalyst for a systemic immune response, potentially resulting in the immunologic targeting and subsequent regression of the primary cutaneous lesion."

# Rejected Claims

No quote-verification failures.

# Special Validation — Paper C

- Two patients were kept as separate Cases (Case 10 = Patient A, 71 male, toe / right inguinal nodes; Case 11 = Patient B, 73 female, right fifth fingertip / right axillary nodes). PHASE 2 events do not mix the two primaries or nodal basins.
- Case 10 PHASE 3 almost failed: only onychomycosis treatment was persisted (observation 409). Primary-toe hypopigmentation, inguinal nodal disease, FNAC/IHC, and BRAF testing were left on the timeline/case layer.
- Case 11 PHASE 3 kept fingertip resolution and axillary metastatic pathology in the same case without copying Patient A’s toe or inguinal findings.
- Primary disappearance versus persistent lymph-node metastasis was not treated as a logical contradiction inside PHASE 3 observations for Patient B: fingertip near-complete resolution (416, 418, 428) coexists with axillary metastatic melanoma (422–427).
- Case-level `viable_tumor_at_pathology` is PRESENT for both patients because nodal tumor is present. That case-level field cannot express “primary absent / node present.”
- Independent lesion disease states: Patient B has a fingertip lesion (27) and axillary node/nodule identities (25, 26). Patient A PHASE 3 has only “skin lesion” (24) and no nodal lesion object.
- Shared methods sentences (both patients isolated lymphadenopathy without fever; combined IHC / BRAF wild-type wording) are a mixing risk. Fever absence and BRAF wild-type were attached to Patient B observations (414, 426); Patient A’s Event 306 also claims BRAF V600E wild-type.

# Validation Failures

- Patient A biological extraction is effectively empty (1 observation, 0 verified PHASE 3 evidence, 40 not-reported targets). This is an external-validation failure of multi-case extraction, not a reason to change the ontology.
- PHASE 2 is partial for temporal uncertainty only; no quote failures.
- Observation 426 value is “wild type,” but the persisted GenotypeObservation (id 2) is BRAF V600E MUTATED. Wild-type was inverted to MUTATED.
- Patient A BRAF wild-type exists only as Event text; no GenotypeObservation was created for Case 10.
- Patient A primary-versus-metastasis lesion map was not built in PHASE 3, so ontology checks for that patient cannot be completed from observations alone.
- `regression_extent_clinical` is CONFLICTING for Patient B (near-complete clinical resolution vs persistent nodal disease) even though those states belong to different lesions.
- Schema, rule, and prompt were not changed.

# New Ontology Pressure Points

- A two-patient interleaved case report needs case-scoped passage assignment before observation extraction; otherwise one patient is timeline-only and the other absorbs shared methods sentences.
- Completely regressed primary plus viable nodal metastasis is two lesion-level disease states, not one case-level viable_tumor or regression_extent value.
- BRAF “V600E mutation … wild type” still collapses to MUTATED when variant-token and state-token coexist; wild-type must win and remain a positive genotype state.
- FNAC / cell-block IHC is diagnostic evidence for the node, not proof that the cutaneous remnant still contains melanoma.
- Clinical diagnosis of a completely regressed primary without biopsy (Patient B) is a different evidence grade than pathology-confirmed nodal metastasis.
- No ontology patch was implemented.

# Validation Summary

- Case count: 2
- Event count: 16
- Observation count: 20
- Biological State: 1
- Disease Phenotype: 5
- Diagnostic Evidence: 9
- Clinical Context: 5
- Treatment Response: 0
- Genotype observations: 1
- Verified Evidence: 91
- Rejected Evidence: 2
- Quote failures: 0
