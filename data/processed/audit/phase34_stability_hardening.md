# PHASE 3.4 Extraction Stability & Recall Hardening

PHASE 4 was not started.

Versions: PHASE 3 schema/rule `phase3.4` / `phase3.4-stability-v1`; prompt `biological_observation_extraction:v5`.

## Ong

- latest PHASE 3.4 runs: 82
- recovered by recall: none in the latest extract (LLM already had the core set, or nothing to recover)
- golden suv_decrease: MISS
- golden necrosis: PASS
- golden viable_cells_absent: PASS
- observations: 22
- genotypes: 0
- irAE: 0
- episodes: 1
- alternatives: 0

## Behnia

- latest PHASE 3.4 runs: 83
- recovered by recall: alternative biopsy_induced_inflammation
- golden regressing_vs_progressing: PASS
- observations: 18
- genotypes: 0
- irAE: 0
- episodes: 2
- alternatives: biopsy_induced_inflammation

## Moreira

- latest PHASE 3.4 runs: 93
- recovered by recall: none in the latest extract (LLM already had the core set, or nothing to recover)
- golden infection_context: PASS
- golden cd3_cd8_infiltration: PASS
- golden braf_wild_type: PASS
- golden delayed_ipilimumab_alternative: PASS
- observations: 22
- genotypes: BRAF WILD_TYPE, del(5q) DELETED
- irAE: 0
- episodes: 3
- alternatives: author_suggested_regression_mechanism, infection_or_surgery_immune_trigger, delayed_immunotherapy_effect

## Tran

- latest PHASE 3.4 runs: 91
- recovered by recall: none in the latest extract (LLM already had the core set, or nothing to recover)
- golden vaccination_event: PASS
- golden fever: PASS
- golden causal_not_promoted: PASS
- observations: 27
- genotypes: HLA UNKNOWN
- irAE: 0
- episodes: 4
- alternatives: 0

## Oswalt

- latest PHASE 3.4 runs: 101
- recovered by recall: genotype BRAF, genotype MEFV, alternative pyrin_related_predisposition, alternative infection_or_surgery_immune_trigger
- golden multiple_regression_episodes: PASS
- golden irae: PASS
- golden mefv_germline_variant: PASS
- golden braf_finding: PASS
- observations: 10
- genotypes: BRAF MUTATED, MEFV VARIANT_PRESENT
- irAE: 2
- episodes: 2
- alternatives: pyrin_related_predisposition, infection_or_surgery_immune_trigger

## Spring

- latest PHASE 3.4 runs: 88
- recovered by recall: alternative author_suggested_regression_mechanism
- golden leukoderma: PASS
- golden viable_tumor_absence: PASS
- golden fibrosis_melanophages_split: PASS
- observations: 20
- genotypes: 0
- irAE: 0
- episodes: 1
- alternatives: author_suggested_regression_mechanism

## Wang

- latest PHASE 3.4 runs: 98, 99
- recovered by recall: none in the latest extract (LLM already had the core set, or nothing to recover)
- golden two_cases_separate: PASS
- golden braf_v600e_wild_type: PASS
- golden primary_and_nodal_coexist: PASS
- observations: 42
- genotypes: BRAF WILD_TYPE, BRAF WILD_TYPE
- irAE: 0
- episodes: 3
- alternatives: 0

## Stability metric

Core-entity recall stability is golden-core retention: the named core entities that must appear in every repeated extract.

- Moreira: 100% over runs 84, 92, 93 (CD3/CD8, BRAF WT, delayed ipilimumab, infection)
- Oswalt: 100% over runs 87, 100, 101 (episodes, irAE, MEFV, BRAF). Runs 94–95 predating the MEFV quote-clause fix are excluded
- Wang: 100% over case-pairs (89,90), (96,97), (98,99) (2 cases, BRAF V600E WILD_TYPE, primary + nodal coexistence)
- mean golden-core retention: 100%
- optional-signature Jaccard (extra lesion states / MC1R): 81.8% / 81.8% / 85.7%

## Recovered entities

- Moreira: CD3/CD8 dual-domain infiltration, BRAF WILD_TYPE, delayed ipilimumab ExplanatoryAlternative
- Oswalt: BRAF MUTATED from liver-biopsy mutation analysis; MEFV germline P369S/R408Q when the body quote verifies; irAE collapsed to hepatotoxicity + polymyositis
- Wang: BRAF V600E WILD_TYPE on both cases
- Cross-layer: PHASE 2 gene Events become GenotypeObservation only after verified PDF quotes and a clear parser state; otherwise RECONCILIATION_REQUIRED

## Remaining missed entities

- Ong/suv_decrease

## Duplicate reduction

- irAE: one canonical row per event_type (polymyositis no longer triples)
- RegressionEpisode: Abstract/Case restatements of the same organ/extent merge; Moreira 5 restatements collapsed to 3
- GenotypeObservation / ExplanatoryAlternative: unique per gene or alternative type in a run

## Remaining pressure points

- LLM observation count still varies; deterministic recall holds the core genotype/immune/alternative set when quotes verify
- Very long PDF sentences can mix observation and interpretation; genotype quotes are truncated to the factual clause
- Extra WES table genes are not promoted; only patient-anchored body findings persist
- Ong SUV wording can miss a strict `SUV` token if the LLM uses a synonym

PHASE 4 was not started.
