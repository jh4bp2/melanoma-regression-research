# PHASE 4A.2 corpus ontology patch

- corpus infra: phase4a.2
- rule: phase4a2-collection-episode-v1
- PHASE 2/3 schema, rule, and prompt were not redesigned.
- Historical extraction runs were preserved. New reconciliation runs were added.

## Before / after (Batch 1–3 extracted papers)

- LesionCollection before: 0
- LesionCollection after: 12
- COLLECTION_ONLY after: 7
- linked members after: 8
- RegressionEpisode before: 18
- RegressionEpisode after (canonical): 15

## Patch actions

- recovered collections: 12
- merged duplicate/fragmented episodes: 2
- split true distinct episodes: 0
- FACT_INVERSION count: 1
- rejected contradiction outputs: 1
- canonical lesion-name improvements: 1

## Per paper

- paper 8: collections=1 episodes 4→4 merged=0 split=0 inversions=0 names=0
- paper 9: collections=1 episodes 2→2 merged=0 split=0 inversions=0 names=0
- paper 10: collections=3 episodes 1→1 merged=0 split=0 inversions=0 names=0
- paper 11: collections=1 episodes 2→2 merged=0 split=0 inversions=0 names=0
- paper 12: collections=0 episodes 1→1 merged=0 split=0 inversions=0 names=0
- paper 13: collections=1 episodes 1→1 merged=0 split=0 inversions=0 names=0
- paper 14: collections=0 episodes 3→1 merged=1 split=0 inversions=0 names=1
- paper 15: collections=0 episodes 2→1 merged=1 split=0 inversions=0 names=0
- paper 16: collections=2 episodes 1→1 merged=0 split=0 inversions=0 names=0
- paper 17: collections=3 episodes 1→1 merged=0 split=0 inversions=1 names=0

## Recovered collections (latest reconciliation run)

- Paper 8 Lynch: cutaneous metastatic group, PARTIAL_MEMBERS_KNOWN
- Paper 9 Levison: pulmonary metastases, PARTIAL_MEMBERS_KNOWN
- Paper 10 Khosravi: cutaneous group (PARTIAL); unnamed pulmonary and brain groups (COLLECTION_ONLY)
- Paper 11 Paolino: melanocytic nevi group, COLLECTION_ONLY
- Paper 13 Haight: pulmonary nodules, COLLECTION_ONLY (normal liver scan excluded)
- Paper 16 Sandru: pulmonary group (PARTIAL, one known member); unnamed LN group (COLLECTION_ONLY); measured brain lesions remain individual
- Paper 17 Martinez-Lopez: nevi group (COLLECTION_ONLY); pulmonary group (PARTIAL); LN group (COLLECTION_ONLY)

## Golden-case corrections

- Koibuchi: 3 confirmation fragments → 1 canonical episode with 3 milestones; `right mass` → `right subcutaneous thigh mass`; FNA-caused regression not promoted to fact
- Yamada: partial → complete primary course → 1 episode with PARTIAL_TO_COMPLETE; inguinal lesion remains a separate lesion state
- Martinez-Lopez: observation 1152 rejected as FACT_INVERSION; correction observation `lentigines remained` on the reconciliation run; historical observation preserved

## Unresolved pressure points

- Haight mixed pulmonary course (some nodules disappeared, later new nodules) remains one LUNG-scoped episode
- Martinez inguinal vs iliac remain one LN collection, not two site-specific collections
- Weak names without sufficient anatomical evidence were not forced (e.g. Haight lymph-node label)
- Sandru marker bundling (Melan-A vs Tyrosinase) was not redesigned
- Seed papers 1–7 were not backfilled; Oswalt / Moreira true multi-episode structure was left untouched

## Notes

- Abstracts were not used as Evidence.
- Pattern Discovery / Hypothesis Generator / Evidence Graph were not run.
- PHASE 4B and Batch 4 were not started.
- index rebuild: {'cases': 19, 'lesions': 41, 'episodes': 31, 'matrix_columns': 21, 'quality_cases': 19}
