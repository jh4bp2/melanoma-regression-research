import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import (  # noqa: F401
    Case,
    Event,
    Evidence,
    ExplanatoryAlternative,
    GenotypeObservation,
    ImmuneRelatedAdverseEvent,
    Lesion,
    LesionAlias,
    LesionCollection,
    LesionState,
    Paper,
    RegressionEpisode,
    TemporalRecord,
)


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()
