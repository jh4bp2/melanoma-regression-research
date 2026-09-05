# PHASE 4A Corpus Expansion Infrastructure

PHASE 4B / Pattern Discovery / Hypothesis Generator / Evidence Graph were not started.

## Corpus infrastructure version

- `phase4a.1` / `corpus-infra-v1`
- Frozen PHASE 2: `phase2.3` / `phase2.3-case-scope-v1`
- Frozen PHASE 3: `phase3.4` / `phase3.4-stability-v1` / `biological_observation_extraction:v5`

## Seed papers

- 7 extracted seed papers (Ong, Behnia, Moreira, Tran, Oswalt, Spring, Wang)
- 6 additional `FULLTEXT_UNAVAILABLE` candidates preserved from the acquisition manifest and not used as Evidence

## Seed cases / lesions / episodes

- cases: 8
- lesions: 15
- regression episodes: 16

## Matrix

- columns: 21
- each column stores `value` and `measurement_status` separately
- case rows filled from existing frozen extracts
- lesion and episode rows are empty skeletons
- `analysis_enabled`: false

## Measurement status model

- `MEASURED`
- `REPORTED_QUALITATIVELY`
- `REPORTED_ABSENT`
- `NOT_REPORTED`
- `UNCERTAIN`

`NOT_REPORTED` is not treated as `REPORTED_ABSENT`.

## Batch runner status

- batch size: 5
- seed registered as batch 0
- runner is idle and waiting for an external candidate list
- resume skips already `EXTRACTED` / `AUDITED` papers
- no new papers were searched or added

## Tests

- 98 passed

## Remaining technical limitations

- Legal full-text search is not automated in this environment; a manual PDF or legal URL is required
- Closed-access candidates stay `FULLTEXT_UNAVAILABLE` and cannot become Evidence
- Lesion/episode matrix cells are not yet populated
- Ontology stays frozen; new wording is recorded as `ONTOLOGY_PRESSURE_POINT` only
