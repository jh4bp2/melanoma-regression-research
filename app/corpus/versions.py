from __future__ import annotations

from app.services.biological_observation_pipeline import BiologicalObservationPipeline
from app.services.extraction_pipeline import ExtractionPipeline


CORPUS_INFRA_VERSION = "phase4a.2"
CORPUS_RULE_VERSION = "phase4a2-collection-episode-v1"
RECONCILIATION_RUN_TYPE = "corpus_reconciliation"
BATCH_SIZE = 5

FROZEN_PHASE2_SCHEMA = ExtractionPipeline.SCHEMA_VERSION
FROZEN_PHASE2_RULE = ExtractionPipeline.RULE_VERSION
FROZEN_PHASE3_SCHEMA = BiologicalObservationPipeline.SCHEMA_VERSION
FROZEN_PHASE3_RULE = BiologicalObservationPipeline.RULE_VERSION
FROZEN_PHASE3_PROMPT = "biological_observation_extraction:v5"

SEED_PAPERS = (
    {"paper_id": 2, "label": "Ong", "role": "development", "candidate_id": "seed-ong-2016"},
    {"paper_id": 1, "label": "Behnia", "role": "development", "candidate_id": "seed-behnia-2018"},
    {"paper_id": 3, "label": "Moreira", "role": "external_validation", "candidate_id": "seed-moreira-2017"},
    {"paper_id": 4, "label": "Tran", "role": "external_validation", "candidate_id": "seed-tran-2013"},
    {"paper_id": 5, "label": "Oswalt", "role": "external_validation", "candidate_id": "seed-oswalt-2022"},
    {"paper_id": 6, "label": "Spring", "role": "external_validation", "candidate_id": "seed-spring-2017"},
    {"paper_id": 7, "label": "Wang", "role": "external_validation", "candidate_id": "seed-wang-2025"},
)


def frozen_ontology() -> dict[str, str]:
    return {
        "corpus_infra_version": CORPUS_INFRA_VERSION,
        "corpus_rule_version": CORPUS_RULE_VERSION,
        "phase2_schema": FROZEN_PHASE2_SCHEMA,
        "phase2_rule": FROZEN_PHASE2_RULE,
        "phase3_schema": FROZEN_PHASE3_SCHEMA,
        "phase3_rule": FROZEN_PHASE3_RULE,
        "phase3_prompt": FROZEN_PHASE3_PROMPT,
        "policy": (
            "Do not change PHASE 2/3 schema/rule/prompt for a single new paper. "
            "Record ONTOLOGY_PRESSURE_POINT and review in batch. "
            "Corpus collection/episode patches use a reconciliation layer."
        ),
    }
