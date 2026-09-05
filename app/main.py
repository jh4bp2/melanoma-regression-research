from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.papers_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title="Melanoma Spontaneous Regression Research System",
    description=(
        "Research-only literature ingestion and evidence provenance API. "
        "Association does not imply causation."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router, prefix="/api/v1")
