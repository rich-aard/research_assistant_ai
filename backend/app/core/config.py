from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]
DATABASE_PATH = BASE_DIR / "data" / "research.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    # Application
    app_name: str = Field(alias="APP_NAME")
    app_version: str = Field(alias="APP_VERSION")
    debug: bool = Field(alias="DEBUG")

    # Server
    host: str = Field(alias="HOST")
    port: int = Field(alias="PORT")

    # api keys
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    # models
    groq_llm_model: str = Field(
        default="openai/gpt-oss-120b",
        alias="GROQ_LLM_MODEL",
    )

    huggingface_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="HF_EMBEDDING_MODEL",
    )

    # chunks values
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")

    # logging
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    # Environment
    app_env: Literal[
        "development",
        "production",
        "testing",
    ] = Field(
        default="development",
        alias="APP_ENV",
    )

    # paths for data and vectorstore
    base_dir: Path = BASE_DIR
    faiss_index_path: Path = BASE_DIR / "data" / "vectorstore" / "faiss_index"
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    report_dir: Path = BASE_DIR / "data" / "reports"
    cache_dir: Path = BASE_DIR / "data" / "cache"

    # LangSmith
    langchain_api_key: str | None = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_tracing_v2: bool = Field(
        default=False,
        alias="LANGCHAIN_TRACING_V2",
    )
    langchain_project: str = Field(
        default="research-assistant-ai",
        alias="LANGCHAIN_PROJECT",
    )

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:8501",
    ]

    # database url
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{DATABASE_PATH}",
        alias="DATABASE_URL",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
