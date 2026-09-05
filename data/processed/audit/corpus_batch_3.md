# Corpus batch 3

Infrastructure version: phase4a.1
Frozen ontology: PHASE 2.3 / PHASE 3.4 / biological_observation_extraction:v5
Schema/rule/prompt were not modified.

- candidates attempted: 5
- full text success: 5
- full text failure/unavailable: 0
- excluded after full text: 1

## Full text

- `batch3-koibuchi-2022` paper_id=14 fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC10632326) bytes=534835 sha256=97959a8116361e3dd208b83bcc2b450ce7d2cf335b47c3fc8a0c9cd3b7efa63a pages=3 downloaded=2026-09-05
- `batch3-yamada-2016` paper_id=15 fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC4960676.1) bytes=2173284 sha256=dc37353487b4619ed223ab5976400e03f7a120c43c4db44097292a359f2b3200 pages=6 downloaded=2026-09-05
- `batch3-sandru-2020` paper_id=16 fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC7271722) bytes=349504 sha256=d1e95378b76cf6e19ba11f9de47e3da4488b7f379ce760a725254950eb3795c1 pages=4 downloaded=2026-09-05
- `batch3-martinez-lopez-2017` paper_id=17 fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC5527740.1) bytes=308648 sha256=cda8fc9af75f2044240fdd3cad4573b5bb3a75daaa53a7208fde7ca0d0dc3b7a pages=2 downloaded=2026-09-05
- `batch3-unknown-primary-2012` paper_id=18 fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC4543345) bytes=2077322 sha256=89441b35c323e67414cf922d8daacdc87603f55628ad2ec4de9d1c5e4eb8749e pages=4 downloaded=2026-09-05

## Extraction counts (Batch 3 papers extracted into corpus)

- Case: 4
- lesion: 10
- collection: 0
- regression episode: 7
- observation: 69

### Per paper

- `batch3-koibuchi-2022` paper_id=14 cases=1 lesions=2 collections=0 episodes=3 observations=15 patients=['paper-14-case-1 [run 117]'] excluded=False exclusion_reason=None
- `batch3-yamada-2016` paper_id=15 cases=1 lesions=2 collections=0 episodes=2 observations=19 patients=['The patient [run 119]'] excluded=False exclusion_reason=None
- `batch3-sandru-2020` paper_id=16 cases=1 lesions=4 collections=0 episodes=1 observations=24 patients=['paper-16-case-1 [run 121]'] excluded=False exclusion_reason=None
- `batch3-martinez-lopez-2017` paper_id=17 cases=1 lesions=2 collections=0 episodes=1 observations=11 patients=['55-year-old woman [run 123]'] excluded=False exclusion_reason=None
- `batch3-unknown-primary-2012` paper_id=18 cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=True exclusion_reason=NOT_SPONTANEOUS_REGRESSION

## Measurement status (Batch 3 case-matrix cells)

- NOT_REPORTED: 67
- REPORTED_ABSENT: 1
- REPORTED_QUALITATIVELY: 16

## Quote verification (Batch 3 linked evidence)

- VERIFIED_EXACT: 193
- VERIFIED_NORMALIZED: 54
- UNVERIFIED: 8

## Ontology pressure points

- [NEW] batch3-koibuchi-2022: One FNA-then-disappearance course was stored as three RegressionEpisode rows (disappearance statement, CT absence, ultrasound absence). The frozen episode model fragments serial confirmation of one course.
- [NEW] batch3-koibuchi-2022: The thigh subcutaneous/tubular metastasis was stored as canonical_name='right mass' without thigh/femur location. It was kept separate from the ankle primary.
- [REPEATED] batch3-yamada-2016: Multiple-site wording is present but no LesionCollection row was created.
- [WORSENED] batch3-sandru-2020: Sandru multiple lymph-node / lung / brain metastases have no LesionCollection rows. Frozen parser can create a collection only when lesion_identifier contains multiple/multifocal/numerous/several wording.
- [NEW] batch3-sandru-2020: Melan-A negative and Tyrosinase negative were stored in one observation instead of two marker-level rows. They were not equated to tumor-cell absence.
- [REPEATED] batch3-sandru-2020: Multiple-site wording is present but no LesionCollection row was created.
- [REPEATED] batch3-sandru-2020: Frozen RegressionEpisode remains case-level and collapsed distinct lesion courses into one episode.
- [WORSENED] batch3-martinez-lopez-2017: Martinez-Lopez 'all nevi disappeared' has no LesionCollection (MULTIPLE_MELANOCYTIC_NEVI or equivalent). Individual unnamed nevi were not invented, but the collection slot remains empty.
- [REPEATED] batch3-martinez-lopez-2017: Nevi disappearance and later metastatic disease remain one case-level RegressionEpisode.
- [NEW] batch3-martinez-lopez-2017: The paper states lentigines remained; extraction stored lentigines as having disappeared. This is a fact inversion, not an ontology gap.
- [REPEATED] batch3-martinez-lopez-2017: Multiple-site wording is present but no LesionCollection row was created.
- [REPEATED] batch3-martinez-lopez-2017: Frozen RegressionEpisode remains case-level and collapsed distinct lesion courses into one episode.
- [NEW] batch3-unknown-primary-2012: Latent/hypothesized regressed occult primary was not promoted to a patient-level spontaneous-regression fact. Paper was EXCLUDED at the inclusion gate and was not extracted.

## Repeated pressure-point watch

- multiple pulmonary metastases collection: WORSENED — Multiple lung metastases are present without a LesionCollection. This now spans Batch 1, 2, and 3.
- multiple lymph-node collection: WORSENED — Multiple lymph-node collection is present in Batch 3 extractions but still has no LesionCollection. This now spans Batch 1, 2, and 3.
- multifocal / multiple-nevi collection: WORSENED — All-nevi / multiple-nevi wording has no LesionCollection. This now spans Batch 1 (Paolino) and Batch 3 (Martinez-Lopez).
- multiple brain metastases collection: WORSENED — Multiple brain metastases have no LesionCollection.
- regression episode collapse: REPEATED — At least one Batch 3 paper still has one case-level episode for distinct lesion courses. This now spans Batch 1, 2, and 3.
- primary regression + metastatic persistence: REPEATED — Yamada complete primary regression coexists with a persistent inguinal metastasis; Sandru regressive primary coexists with lymph-node, lung, and brain metastases; Martinez nevi disappearance coexists with subcutaneous/lung/nodal metastases. The frozen episode model still cannot hold those as one non-contradictory scoped pair.
- vascular/lymphovascular lesion identity: NEW — Koibuchi vascular/lymphatic structure is present; identity was left as extracted without forcing merge or split beyond the quote.
- dual-domain immune pathology: REPEATED — Immune-pathology findings again sit in BIOLOGICAL_STATE and/or DIAGNOSTIC_EVIDENCE because frozen ontology has no dedicated immune-pathology domain.
- latent regression vs observed regression: RESOLVED_BY_EXISTING_MODEL — Unknown-primary paper was EXCLUDED at the inclusion gate. Hypothesized regressed primary was not extracted as a patient fact and no RegressionEpisode was created.

## PHASE4A2_PATCH_CANDIDATE

- PHASE4A2_PATCH_CANDIDATE / PATCH_CANDIDATE_HIGH_PRIORITY: LesionCollection missing — LesionCollection absence now repeats across Batch 1, 2, and 3. Patch is recorded only; it was not executed.
- PHASE4A2_PATCH_CANDIDATE / PATCH_CANDIDATE_HIGH_PRIORITY: RegressionEpisode collapse — Case-level episode collapse now repeats across Batch 1, 2, and 3. Patch is recorded only; it was not executed.

## Possible duplicate reports

- none

## Excluded papers

- batch3-unknown-primary-2012: NOT_SPONTANEOUS_REGRESSION — EXCLUDED: melanoma of unknown primary. Wood's lamp did not show a regressed-primary scar. Lung-lesion change followed chemotherapy and is a treatment response, not spontaneous regression. Regressed occult primary is an author/literature explanatory theory (UNKNOWN PRIMARY != PROVEN SPONTANEOUS REGRESSION). Kept as LATENT_REGRESSION / observation-bias discovery source. woods_negative=True chemo_response=True theory_only=True

## Tests

- 98 passed (full suite; includes `tests/test_phase4a_corpus.py` and `tests/test_phase34_stability.py`)

## Notes

- Frozen PHASE 2.3 / 3.4 ontology was not modified.
- Abstracts were not used as Evidence.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
- PHASE4A2 patch candidates were recorded only; no patch was executed.
- Koibuchi: ankle primary and thigh mass were kept as separate Lesion rows. FNA is an Event; later disappearance is Observation/Episode. FNA was not stored as causing regression. Blood-flow wording was kept qualitative.
- Yamada: primary sole and inguinal node were separated. Melanophages, fibrosis, reactive vascular proliferation, CD8 infiltrate, and viable melanoma-cell absence were separate observations. CD8 is BIOLOGICAL_STATE + DIAGNOSTIC_EVIDENCE.
- Sandru: two measured brain metastases were stored as individual lesions (not invented unnamed members). Multiple lymph-node and lung metastases have no LesionCollection. Melan-A and Tyrosinase negatives share one observation and were not treated as tumor-cell absence.
- Martinez-Lopez: unnamed nevi were not invented as individual lesions, but no MULTIPLE_MELANOCYTIC_NEVI collection was created. Lentigines were inverted to disappeared.
- Christopoulos 2012 remains a LATENT_REGRESSION discovery source only.
