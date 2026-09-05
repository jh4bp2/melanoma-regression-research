# PHASE 3.3 External Validation–Driven Ontology Revision

PHASE 4 was not started. Pattern Discovery, Hypothesis Generator, and Evidence Graph were not started.

## Versions

- PHASE 2 schema/rule: phase2.3 / phase2.3-case-scope-v1
- PHASE 3 schema/rule: phase3.3 / phase3.3-ontology-v1
- biological observation prompt: biological_observation_extraction:v4

### Ong (paper 2)

- PHASE 2 run: 67 / partial
- PHASE 3.3 runs: 68 case 16
- cases: 1
- events: 12
- observations: 22 {'DISEASE_PHENOTYPE': 4, 'CLINICAL_CONTEXT': 1, 'DIAGNOSTIC_EVIDENCE': 12, 'BIOLOGICAL_STATE': 5}
- lesions: 2
- collections: 0
- unresolved lesion identities: 0
- regression episodes: 1
- genotypes: 0 (germline 0, somatic 0)
- irAE records: 0
- leukoderma/immune phenotype: 0
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 31/30/1
- explanatory alternatives: 0

- episode 1 SPONTANEOUS UNCERTAIN: Serial PET/CT scans at 3 and 6 months showed no disease progression, and the left upper lobe nodule SUV had reduced to 0.9 at 6 months. | Spontaneous regression

### Behnia (paper 1)

- PHASE 2 run: 69 / partial
- PHASE 3.3 runs: 70 case 17
- cases: 1
- events: 15
- observations: 16 {'CLINICAL_CONTEXT': 3, 'BIOLOGICAL_STATE': 3, 'DISEASE_PHENOTYPE': 4, 'DIAGNOSTIC_EVIDENCE': 3, 'TREATMENT_RESPONSE': 3}
- lesions: 2
- collections: 1
- unresolved lesion identities: 0
- regression episodes: 2
- genotypes: 0 (germline 0, somatic 0)
- irAE records: 0
- leukoderma/immune phenotype: 0
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 49/22/2
- explanatory alternatives: 1

- episode 1 SPONTANEOUS PARTIAL: The previously biopsied left lower lobe nodule decreased in size, to 17 × 14 mm, and had very minimal/no increased FDG uptake (maximum SUV 2.5) on PET-CT. This 
- episode 2 SPONTANEOUS UNCERTAIN: Despite recurrent disease, the biopsied lesion continued to decrease in size throughout the 19 months that followed after initial diagnosis.

### Moreira (paper 3)

- PHASE 2 run: 71 / partial
- PHASE 3.3 runs: 72 case 18
- cases: 1
- events: 22
- observations: 8 {'DISEASE_PHENOTYPE': 7, 'CLINICAL_CONTEXT': 1}
- lesions: 2
- collections: 2
- unresolved lesion identities: 1
- regression episodes: 5
- genotypes: 0 (germline 0, somatic 0)
- irAE records: 0
- leukoderma/immune phenotype: 0
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 47/16/0
- explanatory alternatives: 0

- episode 1 SPONTANEOUS UNCERTAIN: The patient noted shrinkage of several skin nodules.
- episode 2 SPONTANEOUS UNCERTAIN: Restaging PET/CT showed a mixed response.
- episode 3 SPONTANEOUS COMPLETE: All non-resected in-transit metastases had completely disappeared clinically.
- episode 4 SPONTANEOUS UNCERTAIN: Radiographically, there was a continued mixed response, with most lesions reduced in size.
- episode 5 SPONTANEOUS COMPLETE: All in-transit metastases had resolved clinically and radiographically, and the patient remained in a complete clinical and radiographic response.

### Tran (paper 4)

- PHASE 2 run: 73 / partial
- PHASE 3.3 runs: 74 case 19
- cases: 1
- events: 22
- observations: 22 {'DISEASE_PHENOTYPE': 13, 'DIAGNOSTIC_EVIDENCE': 7, 'CLINICAL_CONTEXT': 1, 'BIOLOGICAL_STATE': 1}
- lesions: 9
- collections: 1
- unresolved lesion identities: 0
- regression episodes: 4
- genotypes: 0 (germline 0, somatic 0)
- irAE records: 0
- leukoderma/immune phenotype: 2
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 54/24/3
- explanatory alternatives: 1

- episode 1 SPONTANEOUS UNCERTAIN: Dramatic improvement in all aforementioned nodules was observed clinically.
- episode 2 SPONTANEOUS UNCERTAIN: Biopsy of a resolved back nodule showed fibrosis but no disease.
- episode 3 SPONTANEOUS UNCERTAIN: Repeat imaging showed progressive reduction in nodule size.
- episode 4 SPONTANEOUS COMPLETE: All nodules had vanished except for an enlarged left axillary nodule; because of the remission, the patient was not enrolled in the study.

### Oswalt (paper 5)

- PHASE 2 run: 75 / partial
- PHASE 3.3 runs: 76 case 20
- cases: 1
- events: 30
- observations: 5 {'DISEASE_PHENOTYPE': 2, 'CLINICAL_CONTEXT': 3}
- lesions: 0
- collections: 0
- unresolved lesion identities: 0
- regression episodes: 2
- genotypes: 0 (germline 0, somatic 0)
- irAE records: 4
- leukoderma/immune phenotype: 0
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 54/10/0
- explanatory alternatives: 0

- episode 1 SPONTANEOUS PARTIAL: The patient reported diminution in the size of the left axillary lymph node during her evaluation.
- episode 2 UNCERTAIN PARTIAL: PET-CT showed multiple hepatic metastases, with 2 of 3 lesions smaller than on the August 2018 CT; the October CT figure states that hepatic lesions had decreas

### Spring (paper 6)

- PHASE 2 run: 77 / partial
- PHASE 3.3 runs: 78 case 21
- cases: 1
- events: 15
- observations: 21 {'DISEASE_PHENOTYPE': 5, 'CLINICAL_CONTEXT': 7, 'DIAGNOSTIC_EVIDENCE': 7, 'BIOLOGICAL_STATE': 2}
- lesions: 4
- collections: 0
- unresolved lesion identities: 0
- regression episodes: 1
- genotypes: 0 (germline 0, somatic 0)
- irAE records: 0
- leukoderma/immune phenotype: 3
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 48/18/3
- explanatory alternatives: 0

- episode 1 SPONTANEOUS COMPLETE: Right-heel biopsy findings were consistent with stage III melanoma regression, namely complete regression with absence of neoplastic cells. | A repeat large inc

### Wang (paper 7)

- PHASE 2 run: 79 / partial
- PHASE 3.3 runs: 80 case 22, 81 case 23
- cases: 2
- events: 20
- observations: 43 {'CLINICAL_CONTEXT': 7, 'DISEASE_PHENOTYPE': 10, 'DIAGNOSTIC_EVIDENCE': 25, 'BIOLOGICAL_STATE': 1}
- lesions: 4
- collections: 0
- unresolved lesion identities: 0
- regression episodes: 3
- genotypes: 2 (germline 0, somatic 0)
- irAE records: 0
- leukoderma/immune phenotype: 6
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 114/0/3
- explanatory alternatives: 0

- genotype BRAF V600E WILD_TYPE origin=UNKNOWN protein=V600E
- genotype BRAF V600E WILD_TYPE origin=UNKNOWN protein=V600E

- episode 1 SPONTANEOUS UNCERTAIN: On retrospective dermatologic evaluation, the affected toenail was dystrophic and irregular, with marked surrounding hypopigmentation measuring approximately 0.
- episode 2 TREATMENT_ASSOCIATED COMPLETE: Clinicians diagnosed completely regressed primary melanoma with nodal metastasis after retrospective investigation of dermatologic history identified cutaneous 
- episode 1 SPONTANEOUS UNCERTAIN: The right fifth-digit lesion underwent abrupt and near-complete resolution; the patient recalled that the area had previously appeared blackened, and the curren

## Totals

- cases: 8
- events: 136
- observations: 137
- lesions: 23
- collections: 4
- unresolved lesion identities: 1
- regression episodes: 18
- genotype observations: 2
- germline/somatic: 0/0
- irAE records: 4
- leukoderma/immune phenotype: 11
- case-scope uncertain: 0
- quotes exact/normalized/unverified: 397/120/12
- explanatory alternatives: 2

## Validation targets

- Oswalt: two regression episodes (axilla vs hepatic) and irAE Clinical Context were created. MEFV germline P369S/R408Q and liver-biopsy BRAF V600E were not persisted as GenotypeObservation (BRAF V600E remains a PHASE 2 Event). Observation count stayed thin (5).
- Spring: acral heel, in-transit thigh, and inguinal node identities are separate; leukoderma is an independent DERMATOLOGIC_PHENOTYPE; fibrosis / melanophages / viable-cell absence were split. No LN collection object was created. One diagnosis sentence that mentions leukoderma was also labeled DERMATOLOGIC_PHENOTYPE.
- Wang: Case 22 = Patient A and Case 23 = Patient B. Primaries and nodal basins were not mixed. BRAF V600E is WILD_TYPE on both cases, not MUTATED. Primary disappearance and nodal persistence coexist.
- Moreira: infection Clinical Context is present. CD3/CD8 dual-domain, BRAF wild-type genotype, and delayed-ipilimumab ExplanatoryAlternative were not recovered in this run.
- Tran: vaccine/fever Clinical Context and a vaccination ExplanatoryAlternative were kept; the alternative was not promoted to an observation.
- Ong/Behnia: lesion counts remain small and stable (2 and 2). No new identity collapse was seen.

## Remaining ontology pressure points

- Genotype persist still depends on the LLM emitting a genetic observation; Event-only BRAF/MEFV findings are not backfilled.
- Germline origin is not inferred unless the word germline appears in the observation text.
- RegressionEpisode grouping by organ can over-split mixed-response imaging and can mislabel a diagnosis sentence as TREATMENT_ASSOCIATED.
- irAE recovery from Events can duplicate the same syndrome (polymyositis x3).
- A diagnosis sentence that also mentions leukoderma can inherit DERMATOLOGIC_PHENOTYPE.
- Multi-station lymph-node sets still often remain unbound identifiers rather than COLLECTION_ONLY objects.
- PHASE 3 observation recall is run-dependent (Moreira 8 vs prior 22); quote/normalization helps provenance more than recall.
- Case-level viable_tumor / regression_extent fields still exist and can still look conflicting; lesion-state is the intended source of truth going forward.

PHASE 4 was not started.
