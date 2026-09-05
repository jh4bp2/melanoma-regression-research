# Corpus batch 6

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

## Candidates and source verification

- `batch6-pique-2011` title=Complete regression of melanoma associated with vitiligo doi=10.5070/D37SN7H2J7 pmid=21272495 pmcid=None year=2011 journal=Dermatology Online Journal site_subtype=CUTANEOUS
  fulltext=FULLTEXT_UNAVAILABLE access=UC eScholarship / Dermatology Online Journal OA PDF url=None sha256=None pages=None bytes=None
  identifier_notes=Europe PMC stores DOI as 10.5070/d37sn7h2j7 (lowercase). Author given as MaSol Martínez-Martín; user suggestion María Sol Martínez-Martín.
- `batch6-patel-2022` title=Partial spontaneous regression of choroidal melanoma: A case image with histopathology and gene expression profiling doi=10.1016/j.ajoc.2022.101517 pmid=35496766 pmcid=PMC9048143 year=2022 journal=American Journal of Ophthalmology Case Reports site_subtype=UVEAL_CHOROIDAL
  fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC9048143.1) url=https://pmc-oa-opendata.s3.amazonaws.com/PMC9048143.1/PMC9048143.1.pdf sha256=76a32435f040c292b0186e349ccf0389809884ef93f600d5a2254591130e2d76 pages=3 bytes=3971604
  identifier_notes=Identifiers match the user suggestion.
- `batch6-goncharov-2025` title=Spontaneous regression of metastases in malignant melanoma: a case report doi=10.20333/25000136-2025-3-102-105 pmid=None pmcid=None year=2025 journal=Siberian Medical Review site_subtype=CUTANEOUS
  fulltext=FULLTEXT_FOUND access=Siberian Medical Review publisher OA PDF url=https://journals.rcsi.science/1819-9496/article/download/413125/680297 sha256=3f598a7bd453794df586659da646d20e5b1722e976f2094d2214bfe6aff51c60 pages=4 bytes=1067296
  identifier_notes=No PMID/PMCID in Europe PMC at validation. Publisher DOI confirmed.
- `batch6-emanuel-2008` title=Complete regression of primary malignant melanoma doi=10.1097/DAD.0b013e318165641a pmid=18360126 pmcid=None year=2008 journal=The American Journal of Dermatopathology site_subtype=CUTANEOUS
  fulltext=FULLTEXT_UNAVAILABLE access=LWW closed access. ResearchGate not used. No institutional/author-manuscript PDF located. url=None sha256=None pages=None bytes=None
  identifier_notes=Europe PMC stores DOI as 10.1097/dad.0b013e318165641a (lowercase).
- `batch6-lallas-2012` title=Extensive regression in pigmented skin lesions: a dangerous confounding feature doi=10.5826/dpc.0202a08 pmid=23785596 pmcid=PMC3663342 year=2012 journal=Dermatology Practical & Conceptual site_subtype=CUTANEOUS
  fulltext=FULLTEXT_FOUND access=NIH NLM NCBI PMC Article Datasets on AWS (PMC3663342.1) url=https://pmc-oa-opendata.s3.amazonaws.com/PMC3663342.1/PMC3663342.1.pdf sha256=fc80a45320ee67c445e9de8e421c7d95847cabbd8ae228ec7104512e4dfa251c pages=4 bytes=1224840
  identifier_notes=Neutral query over OA case-report journals; not in the exclusion author list.

## Inclusion classification

- `batch6-pique-2011` paper_id=None intake=None research=None discovery=None excluded=False reason=None
- `batch6-patel-2022` paper_id=27 intake=INCLUDED_SPONTANEOUS_REGRESSION research=DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION discovery=None excluded=False reason=None
- `batch6-goncharov-2025` paper_id=28 intake=INCLUDED_SPONTANEOUS_REGRESSION research=DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION discovery=None excluded=False reason=None
- `batch6-emanuel-2008` paper_id=None intake=None research=None discovery=None excluded=False reason=None
- `batch6-lallas-2012` paper_id=29 intake=INCLUDED_SPONTANEOUS_REGRESSION research=DIRECTLY_DOCUMENTED_SPONTANEOUS_REGRESSION discovery=None excluded=False reason=None

## Extraction counts (Batch 6 papers extracted into corpus)

- Case: 3
- lesion: 3
- collection: 0
- regression episode (canonical): 3
- observation: 45
- treatment-associated events: 2
- genotype: 2
- irAE: 0
- immune pathology observations: 4
- FACT_INVERSION: 0

### Per paper

- `batch6-pique-2011` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=False
- `batch6-patel-2022` paper_id=27 cases=1 lesions=0 collections=0 episodes=1 observations=19 patients=['paper-27-case-1 [run 187]'] excluded=False
- `batch6-goncharov-2025` paper_id=28 cases=1 lesions=2 collections=0 episodes=1 observations=18 patients=['27-year-old woman of European descent [run 189]'] excluded=False
- `batch6-emanuel-2008` paper_id=None cases=0 lesions=0 collections=0 episodes=0 observations=0 patients=None excluded=False
- `batch6-lallas-2012` paper_id=29 cases=1 lesions=1 collections=0 episodes=1 observations=8 patients=['paper-29-case-1 [run 191]'] excluded=False

## Measurement status (Batch 6 case-matrix cells)

- NOT_REPORTED: 53
- REPORTED_ABSENT: 1
- REPORTED_QUALITATIVELY: 9

## Quote verification (Batch 6 linked evidence)

- VERIFIED_EXACT: 605
- VERIFIED_NORMALIZED: 203
- UNVERIFIED: 5

## PHASE 4A.2 reconciliation

- recon runs this batch: 3
- paper 27: collections=0 episodes 2→1 merged=1 inversions=0
- paper 28: collections=0 episodes 3→1 merged=1 inversions=0
- paper 29: collections=0 episodes 1→1 merged=0 inversions=0

## PHASE 4A.2 patch regression

- LesionCollection missing: PASS
- RegressionEpisode over-splitting: PASS
- RegressionEpisode collapse: PASS
- fact inversion: PASS
- negation scope: PASS
- phantom lesion: PASS
- treatment-associated contamination: PASS
- cross-case contamination: PASS

Patel PET/CT-negative wording was not multiple metastases. The detector match on "metastasis" was a false collection-missing flag and is recorded as PASS after review.

## Ontology pressure points

- batch6-patel-2022: ONTOLOGY_PRESSURE_POINT: MELANOMA_SITE_SUBTYPE. Choroidal/uveal melanoma must not share a cutaneous denominator in PHASE 4B. Frozen schema has organ/location fields but no CUTANEOUS/UVEAL_CHOROIDAL/MUCOSAL/ACRAL/UNKNOWN enum.
- batch6-patel-2022: Named right-eye choroidal mass is present on observations and Events but no Lesion row was persisted on the PHASE 3 run.
- batch6-patel-2022: Serial ultrasound 9.0×12.4×15.3 → 3.7×10.0×11.3 → 3.2×7.2×10.5 mm stored as OBSERVED_FACT. One-year growth and later plaque brachytherapy remain later Events, not a second spontaneous episode after recon merge 2→1.
- batch6-patel-2022: PET/CT negative is metastatic workup, not primary-tumor regression.
- batch6-patel-2022: Research site/subtype metadata: UVEAL_CHOROIDAL.
- batch6-goncharov-2025: Fucoidan stored as DRUG_EXPOSURE Event. Not promoted to causal OBSERVED_FACT.
- batch6-goncharov-2025: Author/discussion biopsy or immune wording remains AUTHOR_INTERPRETATION.
- batch6-goncharov-2025: Research site/subtype metadata: CUTANEOUS.
- batch6-lallas-2012: Only the melanoma patient was a Case. Nevus and LPLK comparators were not Cases.
- batch6-lallas-2012: Arm primary is the regressed lesion; extraction persisted an axillary-node Lesion and not a separate arm-primary Lesion row.
- batch6-lallas-2012: Research site/subtype metadata: CUTANEOUS.
- batch6-pique-2011: Identified; eScholarship/DOJ PDF 403 in this environment. Kept FULLTEXT_UNAVAILABLE. Not replaced.
- batch6-emanuel-2008: Identified; LWW closed. ResearchGate not used. Kept FULLTEXT_UNAVAILABLE. Not replaced.

## Possible duplicate reports

- none of the extracted Batch 6 Cases match an existing corpus patient
- Lallas arm + axillary node is a different patient from Khosravi / Yamada / Wang complete-primary-plus-node cases

## Excluded / discovery-source papers

- none classified C/D/E after full text
- `batch6-pique-2011`: FULLTEXT_UNAVAILABLE
- `batch6-emanuel-2008`: FULLTEXT_UNAVAILABLE
- PMID 41030443 (COVID + ICI blue-nevus melanoma) rejected as discovery substitute (treatment-associated)

## Tests

- 143 passed (7 Batch 6 + 136 prior)

## Notes

- Frozen PHASE 2.3 / 3.4 ontology and PHASE 4A.2 patch were not redesigned.
- Abstracts were not used as Evidence.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
- PHASE 4B was not started.
- Discovery paper is Lallas 2012 (PMC3663342), not a hypothesis-biased query.
- ICI/COVID blue-nevus melanoma (PMID 41030443) was rejected as treatment-associated.
- Vitiligo/fucoidan/diet remain phenotype or exposure, not cause.
- Review-section historical cases and Lallas nevus/LPLK comparators are not Cases.
- Corpus inventory (count only, no pattern interpretation): total candidate papers 43; fulltext/ingested papers 29; included spontaneous papers 25; excluded/reference/unavailable 18; latest-index Cases 27; latest-index lesions 54; latest-index collections not separately totaled in rebuild (Batch 6 extracted collections 0); latest-index canonical episodes 40.
