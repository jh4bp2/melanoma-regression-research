# Corpus batch 5

- corpus infra: phase4a.2
- rule: phase4a2-collection-episode-v1
- PHASE 2: phase2.3 / phase2.3-case-scope-v1
- PHASE 3: phase3.4 / phase3.4-stability-v1
- prompt: biological_observation_extraction:v5
- Schema/rule/prompt were not modified.
- Historical extraction and reconciliation runs were preserved.

- candidates attempted: 5
- full text success: 3
- full text failure/unavailable: 2
- excluded after full text: 0
- extracted into corpus: 3

## Identified papers (query slot → exact record)

- Query 1 metastatic case report → David Filho et al. 2020, BJSTR. Exact Kalialis 2008 title is already FULLTEXT_UNAVAILABLE in corpus. Closest unused documented primary case with legal OA PDF.
- Query 2 brain metastases → Satzger et al. 2006, Eur J Dermatol. Exact closest primary case. No PMC/OA PDF.
- Query 3 after biopsy → Hurwitz 1991, Ann Plast Surg. Exact closest unused primary case (Behnia already in corpus). No PMC/OA PDF.
- Query 4 fever/infection → no unused legal OA fever/infection primary case found. Michael et al. 2007 used as closest unused documented visceral SR case. Fever/infection is not assumed.
- Query 5 complete without systemic treatment → Krebbers et al. 2021, Otol Neurotol. Closest unused OA complete histologic SR case. Surgery and adjuvant RT remain Events.

## Candidates and source verification

- `batch5-davidfilho-2020` title=Spontaneous Regression of a Metastasis from Melanoma: A Case Report doi=10.26717/BJSTR.2020.28.004593 pmid=None pmcid=None year=2020 journal=Biomedical Journal of Scientific & Technical Research
  fulltext=FULLTEXT_FOUND access=BJSTR publisher open-access PDF url=https://biomedres.us/pdfs/BJSTR.MS.ID.004593.pdf sha256=f088f1a13ab300460c2d76ee4453d85b034c940e365ad844bcc4eb46bf4489e8 pages=5 bytes=475609
- `batch5-satzger-2006` title=Spontaneous regression of melanoma with distant metastases - report of a patient with brain metastases doi=None pmid=16935819 pmcid=None year=2006 journal=European Journal of Dermatology
  fulltext=FULLTEXT_UNAVAILABLE access=EJD publisher PDF if legally available; otherwise FULLTEXT_UNAVAILABLE url=None sha256=None pages=None bytes=None
- `batch5-hurwitz-1991` title=Spontaneous regression of metastatic melanoma. doi=10.1097/00000637-199104000-00016 pmid=1872546 pmcid=None year=1991 journal=Annals of Plastic Surgery
  fulltext=FULLTEXT_UNAVAILABLE access=Annals of Plastic Surgery; legal PDF only if publisher OA url=None sha256=None pages=None bytes=None
- `batch5-michael-2007` title=Disease regression in malignant melanoma: spontaneous resolution or a result of treatment with antioxidants, green tea, and pineapple cores? A case report. doi=10.1177/1534735406298897 pmid=17393612 pmcid=None year=2007 journal=Integrative Cancer Therapies
  fulltext=FULLTEXT_FOUND access=University of Surrey institutional repository PDF url=https://openresearch.surrey.ac.uk/view/pdfCoverPage?download=true&filePid=13140500260002346&instCode=44SUR_INST sha256=d3719923207ab697e58d17ca760e4bbf6a0614082e2e3b3752d0faf44bbbfcf1 pages=9 bytes=800058
- `batch5-krebbers-2021` title=Spontaneous Regression of a Middle Ear Melanoma. doi=10.1097/mao.0000000000003371 pmid=34607999 pmcid=PMC8584193 year=2021 journal=Otology & neurotology
  fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC8584193.1) url=https://pmc-oa-opendata.s3.amazonaws.com/PMC8584193.1/PMC8584193.1.pdf sha256=88c4a38a46c88418e9097271d4092e0614dd19068fc29504c11526ed40f463f7 pages=5 bytes=745718

## Inclusion classification

- `batch5-davidfilho-2020` paper_id=24 intake=INCLUDED_SPONTANEOUS_REGRESSION research=DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION discovery=None excluded=False reason=None
- `batch5-satzger-2006` paper_id=None intake=None research=None discovery=None excluded=False reason=None
- `batch5-hurwitz-1991` paper_id=None intake=None research=None discovery=None excluded=False reason=None
- `batch5-michael-2007` paper_id=25 intake=INCLUDED_SPONTANEOUS_REGRESSION research=DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION discovery=None excluded=False reason=None
- `batch5-krebbers-2021` paper_id=26 intake=INCLUDED_SPONTANEOUS_REGRESSION research=RETROSPECTIVELY_SUPPORTED_REGRESSION discovery=None excluded=False reason=None

## Extraction counts (Batch 5 papers extracted into corpus)

- Case: 3
- lesion: 7
- collection: 2
- regression episode (canonical): 3
- observation: 66
- treatment-associated events: 4
- genotype: 1
- irAE: 0
- immune pathology observations: 6
- FACT_INVERSION: 0

### Per paper

- `batch5-davidfilho-2020` paper_id=24 cases=1 lesions=3 collections=0 episodes=1 observations=21 patients=['paper-24-case-1 [run 174]'] excluded=False
- `batch5-satzger-2006` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=False
- `batch5-hurwitz-1991` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=False
- `batch5-michael-2007` paper_id=25 cases=1 lesions=2 collections=2 episodes=1 observations=24 patients=['paper-25-case-1 [run 176]'] excluded=False
- `batch5-krebbers-2021` paper_id=26 cases=1 lesions=2 collections=0 episodes=1 observations=21 patients=['68-year-old male patient [run 178]'] excluded=False

## Measurement status (Batch 5 case-matrix cells)

- MEASURED: 2
- NOT_REPORTED: 50
- REPORTED_QUALITATIVELY: 11

## Quote verification (Batch 5 linked evidence)

- VERIFIED_EXACT: 981
- VERIFIED_NORMALIZED: 131
- UNVERIFIED: 11

## PHASE 4A.2 reconciliation

- recon runs this batch: 3
- paper 24: collections=0 episodes 1→1 merged=0 inversions=0
- paper 25: collections=2 episodes 1→1 merged=0 inversions=0
- paper 26: collections=0 episodes 1→1 merged=0 inversions=0

## PHASE 4A.2 patch regression

- LesionCollection missing: PASS
- RegressionEpisode over-splitting: PASS
- RegressionEpisode collapse: PASS
- fact inversion: PASS
- negation scope: PASS
- phantom lesion: PASS
- treatment-associated contamination: PASS

Constructed lesion_identifier labels (for example "left arm primary melanoma lesion") match documented sites in the source text and were not counted as phantom lesions.

## Ontology pressure points

- batch5-davidfilho-2020: Author discusses biopsy as a possible antigen-release trigger; this remains AUTHOR_INTERPRETATION, not OBSERVED_FACT causation.
- batch5-davidfilho-2020: Discussion Table 1 compiles Kalialis/Bramhall historical cases; those review rows were not ingested as independent Cases.
- batch5-michael-2007: Diet, exercise, antioxidants, green tea, and pineapple cores are documented exposures/Events. The paper leaves cause open; they were not promoted to a causal spontaneous-regression fact.
- batch5-michael-2007: Query slot was fever/infection; no unused legal OA fever/infection primary case was found. This paper is the closest unused documented visceral SR case.
- batch5-krebbers-2021: Author mentions biopsy as a possible trigger; must remain AUTHOR_INTERPRETATION, not OBSERVED_FACT causation.
- batch5-krebbers-2021: Literature discussion mentions infection/surgery as hypothesized associates. This patient is not reported to have infection; infection-not-mentioned is not infection-absent.
- batch5-krebbers-2021: Fine-needle aspiration of an enlarged neck node showed reactive lymphoid cells without melanoma. A workup-negative node is not automatically a melanoma lesion.
- batch5-satzger-2006: Identified primary brain-metastasis case; no legal OA PDF. Kept FULLTEXT_UNAVAILABLE; not replaced.
- batch5-hurwitz-1991: Identified post-biopsy nodal SR case; no legal OA PDF. Kept FULLTEXT_UNAVAILABLE; not replaced.

## Possible duplicate reports

- none of the extracted Batch 5 cases are the same patient as an existing corpus Case
- David Filho 2020 cites Behnia 2018 and Allen 1955 as literature, not as this patient
- Satzger 2006 / Hurwitz 1991 remain identifier-only rows and do not collide with existing paper_ids

## Excluded / discovery-source papers

- none classified C/D/E after full text
- `batch5-satzger-2006`: FULLTEXT_UNAVAILABLE (Europe PMC isOpenAccess=N; publisher PDF not legally retrieved)
- `batch5-hurwitz-1991`: FULLTEXT_UNAVAILABLE (Europe PMC isOpenAccess=N; LWW 403)

## Tests

- 136 passed (pytest -q); PHASE 2.3 / 3.4 / 4A.2 / Batch 4 tests unchanged

## Notes

- Frozen PHASE 2.3 / 3.4 ontology and PHASE 4A.2 patch were not redesigned.
- Abstracts were not used as Evidence.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
- PHASE 4B was not started.
- No unused legal OA fever/infection primary case was found; Michael 2007 is the closest unused documented visceral SR case.
- Review-section historical cases were not ingested as independent Cases.
