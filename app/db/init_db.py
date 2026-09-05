from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine
from app.models import (  # noqa: F401
    BiologicalObservation,
    Case,
    Event,
    Evidence,
    ExplanatoryAlternative,
    ExtractionRun,
    FieldEvidenceLink,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    Lesion,
    LesionAlias,
    LesionCollection,
    LesionCollectionMembership,
    LesionState,
    Paper,
    RegressionEpisode,
    TemporalRecord,
)


ADDITIVE_COLUMNS = {
    "cases": {
        "extraction_confidence": "FLOAT",
        "field_statuses": "TEXT",
        "extraction_run_id": "INTEGER",
        "primary_site_status": "VARCHAR(32)",
        "first_observed_reduction": "TEXT",
        "regression_duration": "TEXT",
        "regression_extent_clinical": "VARCHAR(32)",
        "viable_tumor_at_pathology": "VARCHAR(32)",
    },
    "events": {
        "relative_time": "TEXT",
        "source_date_precision": "VARCHAR(32)",
        "relation_to_regression": "VARCHAR(32)",
        "temporal_order_confidence": "FLOAT",
        "temporal_value": "FLOAT",
        "temporal_unit": "VARCHAR(32)",
        "temporal_relation": "VARCHAR(32)",
        "temporal_precision": "VARCHAR(32)",
        "anchor_event_id": "INTEGER",
        "extraction_run_id": "INTEGER",
    },
    "extraction_runs": {
        "reason_codes": "TEXT",
        "schema_version": "VARCHAR(50)",
        "rule_version": "VARCHAR(100)",
        "case_id": "INTEGER",
        "source_extraction_run_id": "INTEGER",
        "run_type": "VARCHAR(50)",
    },
    "biological_observations": {
        "paper_id": "INTEGER",
        "normalized_variable": "VARCHAR(255)",
        "normalized_value": "TEXT",
        "temporal_precision": "VARCHAR(32)",
        "observation_domain": "VARCHAR(32)",
        "domain_secondary": "VARCHAR(32)",
        "measurement_semantics": "VARCHAR(32)",
        "scope_type": "VARCHAR(32)",
        "lesion_identifier": "VARCHAR(255)",
        "lesion_id": "INTEGER",
        "lesion_collection_id": "INTEGER",
        "regression_role": "VARCHAR(32)",
        "qualitative_level": "VARCHAR(32)",
        "temporal_text": "TEXT",
        "temporal_value": "FLOAT",
        "temporal_unit": "VARCHAR(32)",
        "temporal_relation": "VARCHAR(32)",
        "anchor_event_id": "INTEGER",
        "observation_context": "TEXT",
        "evidence_type": "VARCHAR(32)",
        "confidence": "FLOAT",
        "linked_event_id": "INTEGER",
        "created_from_run_id": "INTEGER",
        "created_at": "DATETIME",
        "clinical_context_subtype": "VARCHAR(32)",
        "case_scope_status": "VARCHAR(32)",
    },
    "evidence": {
        "raw_source_quote": "TEXT",
        "normalized_source_quote": "TEXT",
        "verification_status": "VARCHAR(32)",
    },
    "genotype_observations": {
        "transcript": "VARCHAR(100)",
        "coding_change": "VARCHAR(255)",
        "protein_change": "VARCHAR(255)",
        "rs_id": "VARCHAR(64)",
        "variant_type": "VARCHAR(32)",
        "zygosity": "VARCHAR(32)",
        "origin": "VARCHAR(32)",
        "assay": "VARCHAR(255)",
        "source_context": "TEXT",
    },
    "lesions": {
        "reconciled_canonical_name": "VARCHAR(255)",
    },
    "lesion_collections": {
        "member_count_reported": "INTEGER",
        "membership_confidence": "FLOAT",
        "collection_only": "BOOLEAN",
        "laterality": "VARCHAR(32)",
        "normalized_label": "VARCHAR(255)",
        "count_semantics": "VARCHAR(32)",
        "membership_status": "VARCHAR(32)",
    },
    "regression_episodes": {
        "associated_collection_ids": "TEXT",
        "anatomic_scope": "VARCHAR(255)",
        "milestones": "TEXT",
        "source_episode_ids": "TEXT",
        "extent_transition": "VARCHAR(64)",
        "is_canonical": "BOOLEAN",
    },
    "lesion_collection_memberships": {
        "membership_confidence": "FLOAT",
    },
}


def _apply_safe_additive_migrations() -> None:
    """Add nullable PHASE 2 columns without rewriting or deleting existing rows."""
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, expected_columns in ADDITIVE_COLUMNS.items():
            if not inspector.has_table(table_name):
                continue
            existing = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            for column_name, sql_type in expected_columns.items():
                if column_name not in existing:
                    connection.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ADD COLUMN {column_name} {sql_type}"
                        )
                    )


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _apply_safe_additive_migrations()


if __name__ == "__main__":
    init_db()
