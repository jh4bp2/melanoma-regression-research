from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'research.db').as_posix()}"
    papers_dir: Path = Field(default=PROJECT_ROOT / "data" / "papers")
    processed_dir: Path = Field(default=PROJECT_ROOT / "data" / "processed")
    log_level: str = "INFO"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_max_retries: int = Field(default=2, ge=0, le=5)
    llm_timeout_seconds: float = Field(default=300.0, ge=10.0, le=900.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
