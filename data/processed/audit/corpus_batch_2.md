# Corpus batch 2

Infrastructure version: phase4a.1
Frozen ontology: PHASE 2.3 / PHASE 3.4 / biological_observation_extraction:v5
Schema/rule/prompt were not modified.

- candidates attempted: 5
- full text success: 1
- full text failure/unavailable: 4

## Full text

- `batch2-haight-1984` paper_id=13 fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC2153525) bytes=2704607 sha256=c5b436686e864d6cdae5d9387f40aa378a35db2c0e8e002060b9b2b55591681a pages=4 downloaded=2026-09-05
- `batch2-mikhail-1986` paper_id=None fulltext=FULLTEXT_UNAVAILABLE access=Not in PMC; Europe PMC hasPDF=N; Unpaywall oa_status=closed, has_repository_copy=false; OpenAlex is_oa=false; Deep Blue handle 2027.42/74434 is a restricted/non-OA deposit (403) bytes=None sha256=None pages=None downloaded=None
- `batch2-kessler-1984` paper_id=None fulltext=FULLTEXT_UNAVAILABLE access=Not in PMC; Europe PMC hasPDF=N; Unpaywall oa_status=closed, has_repository_copy=false; OpenAlex is_oa=false; LWW/PRS closed bytes=None sha256=None pages=None downloaded=None
- `batch2-macdougal-1976` paper_id=None fulltext=FULLTEXT_UNAVAILABLE access=Not in PMC; Europe PMC hasPDF=N; Unpaywall oa_status=closed, has_repository_copy=false; OpenAlex is_oa=false; LWW/PRS closed. Europe PMC OpenAlex 'Free' DOI link is the publisher landing page, not an OA PDF bytes=None sha256=None pages=None downloaded=None
- `batch2-grafton-1994` paper_id=None fulltext=FULLTEXT_UNAVAILABLE access=No DOI; not in PMC; Europe PMC hasPDF=N; OpenAlex is_oa=false, any_repository_has_fulltext=false; J La State Med Soc closed bytes=None sha256=None pages=None downloaded=None

## Extraction counts (Batch 2 papers with full text)

- Case: 1
- lesion: 2
- collection: 0
- regression episode: 1
- observation: 15

### Per paper

- `batch2-haight-1984` paper_id=13 cases=1 lesions=2 collections=0 episodes=1 observations=15 patients=['72-year-old retired farmer [run 114]']
- `batch2-mikhail-1986` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0
- `batch2-kessler-1984` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0
- `batch2-macdougal-1976` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0
- `batch2-grafton-1994` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0

## Measurement status (Batch 2 case-matrix cells)

- NOT_REPORTED: 17
- REPORTED_QUALITATIVELY: 4
- MEASURED: 0
- REPORTED_ABSENT: 0
- UNCERTAIN: 0

## Quote verification (Batch 2 linked evidence)

- VERIFIED_EXACT: 44
- VERIFIED_NORMALIZED: 33
- UNVERIFIED: 4

## Ontology pressure points

- [WORSENED] batch2-haight-1984: Multiple pulmonary nodules have neither a Lesion row nor a LesionCollection. Some nodules disappeared on serial films while others appeared later; the frozen model cannot group that imaging-only mixed course.
- [NEW] batch2-haight-1984: The paper states there was no histological documentation of the pulmonary nodules, but that clause was stored as DIAGNOSTIC_EVIDENCE HISTOLOGICAL_DOCUMENTATION_OF_PULMONARY_NODULES with an empty value instead of REPORTED_ABSENT.
- [REPEATED] batch2-haight-1984: Case-level RegressionEpisode still cannot separately encode neck recurrence versus later mixed pulmonary-nodule regression and new nodules.

## Repeated Batch 1 pressure-point watch

- LesionCollection missing: WORSENED — Haight pulmonary nodules have no collection and no lesion rows, only unscoped observations.
- host predisposition expression: RESOLVED_BY_EXISTING_MODEL — Haight has no XP/host-genotype claim; the Batch 1 host-slot gap did not recur.
- dermoscopic/pathology domain ambiguity: RESOLVED_BY_EXISTING_MODEL — Haight has no dermoscopic findings.
- retrospective vs directly observed regression: RESOLVED_BY_EXISTING_MODEL — Haight pulmonary change is serial chest-film observation, not a retrospective occult-primary diagnosis.
- primary regression + metastatic persistence/progression coexistence: REPEATED — neck recurrence then later mixed pulmonary regression/new nodules remain one case-level episode.
- old scanned PDF article-boundary contamination: RESOLVED_BY_EXISTING_MODEL — PDF is the target article plus French summary; Nathanson review cases were not created as patients.

## Possible duplicate reports

- none

## Excluded papers

- none

## Tests

- 98 passed (full suite)

## Notes

- Frozen PHASE 2.3 / 3.4 ontology was not modified.
- Abstracts were not used as Evidence.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
- Death is recorded as an Event (OTHER) from hiatus-hernia surgical complications and was not promoted to regression failure.
