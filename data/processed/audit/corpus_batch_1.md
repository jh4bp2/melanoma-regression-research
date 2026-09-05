# Corpus batch 1

Infrastructure version: phase4a.1
Frozen ontology: PHASE 2.3 / PHASE 3.4 / biological_observation_extraction:v5
Schema/rule/prompt were not modified.

## Full text

- success: 5
- failure/unavailable: 0

- `batch1-lynch-1978` paper_id=8 fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC1013731) bytes=1808808 sha256=7de2e92fde2fabea65131b7ad89b078dd0b99379e31cef3f24fab88d3b80c6fe pages=6 downloaded=2026-09-05
- `batch1-levison-1955` paper_id=9 fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC2061225) bytes=503353 sha256=9c1286ddfb9db14165e3cd7b7d1356e7d4e43ba91013c05996987454113254ec pages=2 downloaded=2026-09-05
- `batch1-khosravi-2016` paper_id=10 fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC5144746.1) bytes=1061410 sha256=8fc1197ff0692972bee46365e1e24e1b4b50f7c2b440f031ca6b505b4dbaf8b2 pages=3 downloaded=2026-09-05
- `batch1-paolino-2020` paper_id=11 fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC7346594.1) bytes=618554 sha256=6471312a947c57e92736e75a675b48cd7e6e985c6271047207f82bf013c448f1 pages=3 downloaded=2026-09-05
- `batch1-nwabudike-2022` paper_id=12 fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC9289571.1) bytes=1578150 sha256=019d3958fc0ba450eb5d9f39783e5dcf9ee4b9d0f422240b7628ce06f9f21f26 pages=7 downloaded=2026-09-05

## Extraction counts (Batch 1 papers only)

- Case: 6
- lesion: 14
- collection: 0
- regression episode: 10
- observation: 97

### Per paper

- `batch1-lynch-1978` paper_id=8 cases=2 lesions=4 collections=0 episodes=4 observations=23 patients=['CASE 1; proband (Fig. 1; II.4) [run 102]', 'CASE 2; sister of the proband (Fig. 1; II.2) [run 102]']
- `batch1-levison-1955` paper_id=9 cases=1 lesions=3 collections=0 episodes=2 observations=12 patients=['paper-9-case-1 [run 105]']
- `batch1-khosravi-2016` paper_id=10 cases=1 lesions=4 collections=0 episodes=1 observations=27 patients=['paper-10-case-1 [run 107]']
- `batch1-paolino-2020` paper_id=11 cases=1 lesions=2 collections=0 episodes=2 observations=16 patients=['paper-11-case-1 [run 109]']
- `batch1-nwabudike-2022` paper_id=12 cases=1 lesions=1 collections=0 episodes=1 observations=19 patients=['paper-12-case-1 [run 112]']

## Measurement status (Batch 1 case-matrix cells)

- NOT_REPORTED: 105
- REPORTED_QUALITATIVELY: 21

## Quote verification (Batch 1 linked evidence)

- VERIFIED_EXACT: 316
- VERIFIED_NORMALIZED: 28
- UNVERIFIED: 16

## Ontology pressure points

- batch1-lynch-1978: Frozen ontology has no dedicated host/genetic clinical-context type. Xeroderma pigmentosum was stored as CLINICAL_CONTEXT on one sibling, BIOLOGICAL_STATE on the other, and as genotype gene=XDP. Inflammatory infiltrate was kept as an observed Biological State only where the paper described cells.
- batch1-levison-1955: The legal PMC PDF includes adjacent BMJ articles on the same pages. Sparse 1955 dates have no richer UNKNOWN-date slot than missing values. Pulmonary findings used a 'collection' lesion_identifier without a LesionCollection row. Unmentioned findings must remain NOT_REPORTED.
- batch1-khosravi-2016: Frozen RegressionEpisode is case-level and cannot separately encode primary complete regression coexisting with later metastatic progression. Those facts were stored as separate observations/events and were not collapsed into a single contradictory episode.
- batch1-paolino-2020: Multiple melanocytic nevi have no LesionCollection row; remaining nevi were one DIAGNOSTIC_EVIDENCE observation. Dermoscopic regression was stored as DISEASE_PHENOTYPE/DERMATOLOGIC_PHENOTYPE because there is no dermoscopic observation domain.
- batch1-nwabudike-2022: No dermoscopic observation domain; collision-tumour impression versus histopathologic melanoma share one lesion. The first PHASE 2 attempt failed because REPORTED_ABSENT is valid only for primary_site. Lymphocytic infiltrate was stored as both DIAGNOSTIC_EVIDENCE and BIOLOGICAL_STATE.

## Excluded papers

- none

## Tests

- 98 passed (full suite; includes `tests/test_phase4a_corpus.py` and `tests/test_phase34_stability.py`)

## Notes

- Frozen PHASE 2.3 / 3.4 ontology was not modified.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
