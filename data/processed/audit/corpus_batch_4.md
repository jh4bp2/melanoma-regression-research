# Corpus batch 4

- corpus infra: phase4a.2
- rule: phase4a2-collection-episode-v1
- PHASE 2: phase2.3 / phase2.3-case-scope-v1
- PHASE 3: phase3.4 / phase3.4-stability-v1
- prompt: biological_observation_extraction:v5
- Schema/rule/prompt were not modified.
- Historical extraction and reconciliation runs were preserved.

- candidates attempted: 5
- full text success: 5
- full text failure/unavailable: 0
- excluded after full text: 3
- extracted into corpus: 2

## Candidates and source verification

- `batch4-ehrsam-2016` title=Fully Regressive Melanoma: A Case Without Metastasis. doi=None pmid=27672418 pmcid=PMC5022996 year=2016 journal=The Journal of clinical and aesthetic dermatology
  fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC5022996) url=https://europepmc.org/articles/PMC5022996?pdf=render sha256=65a12f20c5be6bf345e5cba4544a089254b8069bd82cb5720076651544d1a15c pages=5 bytes=118705
- `batch4-allen-1955` title=Malignant melanoma; spontaneous regression after pregnancy. doi=10.1136/bmj.2.4947.1067 pmid=13260663 pmcid=PMC1981517 year=1955 journal=British medical journal
  fulltext=FULLTEXT_FOUND access=Europe PMC full-text PDF (PMC1981517) url=https://europepmc.org/articles/PMC1981517?pdf=render sha256=a2bf6bdd33b60807cf0cc7cb876fe29e0dbae046f9de65ae05c5e3a08a58ce07 pages=1 bytes=249384
- `batch4-tumoral-melanosis-2021` title=Tumoral melanosis without metastasis: a report after three years of follow-up. doi=10.1016/j.abd.2020.04.016 pmid=34598805 pmcid=PMC8790163 year=2021 journal=Anais brasileiros de dermatologia
  fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC8790163.1) url=https://pmc-oa-opendata.s3.amazonaws.com/PMC8790163.1/PMC8790163.1.pdf sha256=0fd0436b5d197ab5a9a522960ba3c48c9c645131fca9b0f674ee08f15c1f9e43 pages=2 bytes=1123043
- `batch4-braf-2019` title=Complete regression of primary melanoma associated with nevi involution under BRAF inhibitors: A case report and review of the literature. doi=10.3892/ol.2018.9738 pmid=30944613 pmcid=PMC6444337 year=2019 journal=Oncology letters
  fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC6444337.1) url=https://pmc-oa-opendata.s3.amazonaws.com/PMC6444337.1/PMC6444337.1.pdf sha256=658b462dd151ba033a75e2396b4fff6c7cefaa8c02e8b31b9420009a6f6b0fb8 pages=7 bytes=1132810
- `batch4-pembrolizumab-2017` title=Tumoral Melanosis Associated with Pembrolizumab-Treated Metastatic Melanoma. doi=10.7759/cureus.1026 pmid=28348944 pmcid=PMC5348220 year=2017 journal=Cureus
  fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC5348220.1) url=https://pmc-oa-opendata.s3.amazonaws.com/PMC5348220.1/PMC5348220.1.pdf sha256=1d15567814946de836a998a0ee2071bcacdb79f9589acb52068a209b68f89acd pages=17 bytes=12527494

## Inclusion classification

- `batch4-ehrsam-2016` paper_id=19 intake=INCLUDED_SPONTANEOUS_REGRESSION research=RETROSPECTIVELY_SUPPORTED_REGRESSION discovery=None excluded=False reason=None
- `batch4-allen-1955` paper_id=20 intake=INCLUDED_SPONTANEOUS_REGRESSION research=DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION discovery=None excluded=False reason=None
- `batch4-tumoral-melanosis-2021` paper_id=21 intake=LATENT_REGRESSION_DISCOVERY_SOURCE research=LATENT_OR_HYPOTHESIZED_REGRESSION discovery=LATENT_REGRESSION excluded=True reason=NOT_SPONTANEOUS_REGRESSION
- `batch4-braf-2019` paper_id=22 intake=TREATMENT_ASSOCIATED_REFERENCE research=TREATMENT_ASSOCIATED_REGRESSION discovery=TREATMENT_ASSOCIATED excluded=True reason=NOT_SPONTANEOUS_REGRESSION
- `batch4-pembrolizumab-2017` paper_id=23 intake=TREATMENT_ASSOCIATED_REFERENCE research=TREATMENT_ASSOCIATED_REGRESSION discovery=TREATMENT_ASSOCIATED excluded=True reason=NOT_SPONTANEOUS_REGRESSION

## Extraction counts (Batch 4 papers extracted into corpus)

- Case: 2
- lesion: 3
- collection: 1
- regression episode (canonical): 3
- observation: 34
- treatment-associated events: 1
- genotype: 0
- FACT_INVERSION: 0

### Per paper

- `batch4-ehrsam-2016` paper_id=19 cases=1 lesions=1 collections=0 episodes=1 observations=20 patients=['paper-19-case-1 [run 168]'] excluded=False
- `batch4-allen-1955` paper_id=20 cases=1 lesions=2 collections=1 episodes=2 observations=14 patients=['paper-20-case-1 [run 170]'] excluded=False
- `batch4-tumoral-melanosis-2021` paper_id=21 cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=True
- `batch4-braf-2019` paper_id=22 cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=True
- `batch4-pembrolizumab-2017` paper_id=23 cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=True

## Measurement status (Batch 4 case-matrix cells)

- NOT_REPORTED: 35
- REPORTED_QUALITATIVELY: 7

## Quote verification (Batch 4 linked evidence)

- VERIFIED_EXACT: 520
- VERIFIED_NORMALIZED: 94
- UNVERIFIED: 5

## PHASE 4A.2 reconciliation

- recon runs this batch: 2
- paper 19: collections=0 episodes 1→1 merged=0 inversions=0
- paper 20: collections=1 episodes 2→2 merged=0 inversions=0

## PHASE 4A.2 patch regression

- collection layer ok: True
- episode merge ok: True for imaging/pathology confirmation pattern; Allen narrative restatement of the same postpartum course remained 2 episodes
- polarity ok: True
- treatment not classified spontaneous: True

## Ontology pressure points

- batch4-ehrsam-2016: Author 'host immune response' mechanism is interpretation, not an observed fact.
- batch4-ehrsam-2016: Residual basal-layer large melanocytes coexist with a fully-regressive diagnosis; they were kept as separate observed findings and were not inverted to tumor-absent.
- batch4-ehrsam-2016: Negative metastatic workup exists as an observed finding, but the case-matrix cell remains NOT_REPORTED rather than REPORTED_ABSENT.
- batch4-allen-1955: Historic BMJ PDF contained the adjacent 'Medical Memoranda / Uterine Fibroids' article. Extracted text was clipped at that boundary before extraction; no second case was created.
- batch4-allen-1955: Author proposes pregnancy/hormone dependence. Pregnancy/delivery were stored as Events. Causation was not stored as OBSERVED_FACT.
- batch4-allen-1955: July 10 nodule disappearance and 'clinically complete within eleven weeks of delivery' remained two canonical episodes of one postpartum course. PHASE 4A.2 merge looks for confirmation-language, not narrative restatement.
- batch4-tumoral-melanosis-2021: Tumoral melanosis != proven prior melanoma. Kept as LATENT_REGRESSION discovery source.
- batch4-braf-2019: Index case includes a prior completely regressed primary plus later BRAF-associated nevi involution/second melanoma. Paper was excluded as TREATMENT_ASSOCIATED_REFERENCE; review-section historical cases were not ingested.

## Possible duplicate reports

- none

## Excluded / discovery-source papers

- batch4-tumoral-melanosis-2021: LATENT_REGRESSION_DISCOVERY_SOURCE — Tumoral melanosis without a directly proven prior melanoma. LATENT/uncertain origin; no forced RegressionEpisode.
- batch4-braf-2019: TREATMENT_ASSOCIATED_REFERENCE — Treatment-associated regression / tumoral melanosis. Not ingested as a spontaneous-regression corpus case.
- batch4-pembrolizumab-2017: TREATMENT_ASSOCIATED_REFERENCE — Treatment-associated regression / tumoral melanosis. Not ingested as a spontaneous-regression corpus case.

## Tests

- 128 passed

## Notes

- Frozen PHASE 2.3 / 3.4 ontology and PHASE 4A.2 patch were not redesigned.
- Abstracts were not used as Evidence.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
- PHASE 4B and Batch 5 were not started.
- Review-section historical cases were not ingested as independent Cases.
