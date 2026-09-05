# PHASE 3.2 Ontology Hardening Report

PHASE 4 was not started. No new papers were added.

## Versions

- schema_version: phase3.2
- rule_version: phase3.2-ontology-v1
- biological observation prompt: biological_observation_extraction:v3
- PHASE 2 schema/rule unchanged: phase2.2.2 / phase2.2-adjudication-v4

## Runs

### Ong (paper 2)

- PHASE 2 run: 41
- PHASE 3.2 run: 42
- case_id: 1
- status: partial
- observations: 18
- lesions: 2
- lesion aliases: 3 (confirmed extra-name 3, possible 0)
- alias merges (run metric): 9
- unresolved lesion identities: 0
- temporal records: 10 (case/event 8, observation 2; approximate/relative/interval 3)
- dual-domain immune pathology: 0
- genotype records: 0
- explanatory alternatives: 0
- static range marked DECREASED: 0
- spontaneous regression as TREATMENT_RESPONSE: 0
- infection Event present: False
- infection Clinical Context: 0

### Behnia (paper 1)

- PHASE 2 run: 43
- PHASE 3.2 run: 44
- case_id: 2
- status: partial
- observations: 17
- lesions: 2
- lesion aliases: 8 (confirmed extra-name 8, possible 0)
- alias merges (run metric): 5
- unresolved lesion identities: 0
- temporal records: 11 (case/event 10, observation 1; approximate/relative/interval 10)
- dual-domain immune pathology: 0
- genotype records: 0
- explanatory alternatives: 0
- static range marked DECREASED: 0
- spontaneous regression as TREATMENT_RESPONSE: 0
- infection Event present: False
- infection Clinical Context: 0

### Paper 4 (paper 4)

- PHASE 2 run: 45
- PHASE 3.2 run: 47
- case_id: 6
- status: partial
- observations: 33
- lesions: 10
- lesion aliases: 11 (confirmed extra-name 11, possible 0)
- alias merges (run metric): 7
- unresolved lesion identities: 0
- temporal records: 26 (case/event 26, observation 0; approximate/relative/interval 22)
- dual-domain immune pathology: 0
- genotype records: 0
- explanatory alternatives: 1
- static range marked DECREASED: 0
- spontaneous regression as TREATMENT_RESPONSE: 0
- infection Event present: False
- infection Clinical Context: 0

Explanatory alternatives:
- vaccination_associated_regression [AUTHOR_SUGGESTED]

### Paper 3 (paper 3)

- PHASE 2 run: 48
- PHASE 3.2 run: 50
- case_id: 7
- status: partial
- observations: 22
- lesions: 3
- lesion aliases: 4 (confirmed extra-name 4, possible 0)
- alias merges (run metric): 3
- unresolved lesion identities: 0
- temporal records: 25 (case/event 25, observation 0; approximate/relative/interval 24)
- dual-domain immune pathology: 1
- genotype records: 1
- explanatory alternatives: 2
- static range marked DECREASED: 0
- spontaneous regression as TREATMENT_RESPONSE: 0
- infection Event present: True
- infection Clinical Context: 2

Genotypes:
- BRAF WILD_TYPE

Explanatory alternatives:
- infection_or_surgery_immune_trigger [AUTHOR_SUGGESTED]
- delayed_immunotherapy_effect [AUTHOR_SUGGESTED]

## Requested totals

- lesion alias merge count: 24
- unresolved lesion identity count: 0
- approximate/relative/interval temporal records: 59
- dual-domain immune pathology count: 1
- genotype records: 1

## Checklist

- Ong: infection_context_recovered=n/a; spontaneous_misclass_remaining=0
- Behnia: infection_context_recovered=n/a; spontaneous_misclass_remaining=0
- Paper 4: infection_context_recovered=n/a; spontaneous_misclass_remaining=0
- Paper 3: infection_context_recovered=True; spontaneous_misclass_remaining=0
- spontaneous regression misclassification fixed: yes
- infection Clinical Context recovered: yes (Paper 3)
- tests: 58 passed

## External-validation checks

### Paper 4

- Static size range "1 mm to 10 mm" direction = UNKNOWN (not DECREASED)
- Lesion aliases stabilized (left axillary nodule / lymph node share one lesion)
- Relative/approximate PHASE 2 temporal records preserved (22 of 26)
- Fibrosis and "no disease" are PATHOLOGIC_FINDING
- Vaccine speculation stored as ExplanatoryAlternative AUTHOR_SUGGESTED, not a causal fact

### Paper 3

- CD3+/CD8+ infiltration: BIOLOGICAL_STATE + domain_secondary DIAGNOSTIC_EVIDENCE
- BRAF wild-type: GenotypeObservation.state = WILD_TYPE (not ABSENT)
- Complete disappearance / mixed radiographic reduction: DISEASE_PHENOTYPE
- Infection Event also produced CLINICAL_CONTEXT observations
- "most lesions reduced in size" kept as OBSERVED_FACT
- Delayed ipilimumab effect stored as ExplanatoryAlternative AUTHOR_SUGGESTED

## Remaining ontology pressure points

- Canonical names can still be crude (`lymph node lymph node`, generic `skin lesion`).
- Collection membership is incomplete when the paper only names a group (in-transit set) and not each member.
- `POSSIBLE_SAME_LESION` was 0 on these reruns; canonical-name reparse can confirm pairs the raw parser would leave possible.
- Paper 3/4 biological-observation TemporalRecord rows were not written even when `temporal_text` exists on the observation; PHASE 2 TemporalRecords still hold the approximate/relative case and event timing.
- Ong stored `at 6 months` as UNKNOWN on the observation TemporalRecord; the relative parser now accepts that form, but that run was not repeated.
- `del(5q)` remains a cytogenetic observation, not a GenotypeObservation (only BRAF/NRAS/KIT/NF1 are genotyped).
- Unverified quotes still force PARTIAL runs (line-wrap / typography).
- Direction token `MIXED` appeared once and is not yet a first-class direction value.

PHASE 4, Pattern Discovery, Hypothesis Generator, Evidence Graph, and new papers were not started.
