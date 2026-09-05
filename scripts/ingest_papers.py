from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.paper_ingestion import ingest_directory


def main() -> None:
    settings = get_settings()
    init_db()
    with SessionLocal() as session:
        results = ingest_directory(session, settings.papers_dir, settings.processed_dir)

    created_count = sum(result.created for result in results)
    duplicate_count = len(results) - created_count
    print(
        f"Ingestion complete: {created_count} created, "
        f"{duplicate_count} duplicates, {len(results)} PDFs scanned."
    )


if __name__ == "__main__":
    main()
