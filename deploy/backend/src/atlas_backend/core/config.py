"""Runtime configuration contracts for Atlas backend."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
import os

from pydantic import BaseModel, Field, field_validator


class AtlasEnvironment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class AtlasRuntimeMode(StrEnum):
    """Supported Atlas runtime modes."""

    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class AtlasSettings(BaseModel):
    """Typed backend settings loaded from environment variables."""

    app_name: str = "Atlas API"
    environment: AtlasEnvironment = AtlasEnvironment.DEVELOPMENT
    runtime_mode: AtlasRuntimeMode = AtlasRuntimeMode.HYBRID
    api_version: str = "v1"
    api_base_path: str = "/api/v1"
    api_base_url: str = "http://localhost:8000/api/v1"
    local_mode_enabled: bool = True
    cloud_sync_enabled: bool = False
    https_only: bool = True
    log_level: str = "info"
    cors_allowed_origins: tuple[str, ...] = Field(default_factory=tuple)
    database_url: str | None = None
    sqlite_path: str | None = None
    redis_url: str | None = None
    qdrant_url: str | None = None
    neo4j_url: str | None = None
    storage_type: str = "filesystem"
    storage_path: str | None = None
    s3_bucket: str | None = None
    # Security
    jwt_secret: str | None = None
    rate_limit_enabled: bool = True

    # M6: Document Intelligence
    documents_storage_path: str | None = None
    ocr_provider: str = "tesseract"  # tesseract, cloud
    max_document_size_mb: int = 100
    chunking_strategy: str = "semantic"  # semantic, sliding_window
    chunk_min_size: int = 100
    chunk_max_size: int = 2000
    # M7: Projects & Knowledge
    knowledge_graph_enabled: bool = False
    # M8: Local Intelligence
    local_models_enabled: bool = True
    ollama_base_url: str = "http://localhost:11434"
    local_embedding_model: str = "nomic-embed-text"
    local_llm_model: str = "mistral-7b"
    local_cache_max_size: int = 1000
    local_memory_max_entries: int = 10000

    @field_validator("api_base_path")
    @classmethod
    def api_base_path_must_be_versioned(cls, value: str) -> str:
        if not value.startswith("/api/v"):
            raise ValueError("api_base_path must use explicit /api/v* versioning")
        return value.rstrip("/")

    @field_validator("log_level")
    @classmethod
    def log_level_must_be_known(cls, value: str) -> str:
        normalized = value.lower()
        allowed = {"debug", "info", "warning", "error", "critical"}
        if normalized not in allowed:
            raise ValueError(f"log_level must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @property
    def is_local_runtime(self) -> bool:
        return self.runtime_mode == AtlasRuntimeMode.LOCAL

    @property
    def is_cloud_runtime(self) -> bool:
        return self.runtime_mode == AtlasRuntimeMode.CLOUD


def load_settings(environ: Mapping[str, str] | None = None) -> AtlasSettings:
    """Load Atlas backend settings from an environment mapping."""

    source = environ or os.environ
    environment = _read_str(source, "ATLAS_ENV", AtlasEnvironment.DEVELOPMENT.value)

    return AtlasSettings(
        app_name=_read_str(source, "ATLAS_APP_NAME", "Atlas API"),
        environment=AtlasEnvironment(environment),
        runtime_mode=AtlasRuntimeMode(_read_str(source, "ATLAS_RUNTIME_MODE", "hybrid")),
        api_version=_read_str(source, "ATLAS_API_VERSION", "v1"),
        api_base_path=_read_str(source, "ATLAS_API_BASE_PATH", "/api/v1"),
        api_base_url=_read_str(source, "ATLAS_API_BASE_URL", "http://localhost:8000/api/v1"),
        local_mode_enabled=_read_bool(source, "ATLAS_LOCAL_MODE_ENABLED", True),
        cloud_sync_enabled=_read_bool(source, "ATLAS_CLOUD_SYNC_ENABLED", False),
        https_only=_read_bool(source, "ATLAS_HTTPS_ONLY", True),
        log_level=_read_str(source, "ATLAS_LOG_LEVEL", "info"),
        cors_allowed_origins=_read_tuple(source, "ATLAS_CORS_ALLOWED_ORIGINS"),
        database_url=_read_optional_str(source, "DATABASE_URL"),
        sqlite_path=_read_optional_str(source, "ATLAS_SQLITE_PATH"),
        redis_url=_read_optional_str(source, "REDIS_URL"),
        qdrant_url=_read_optional_str(source, "QDRANT_URL"),
        neo4j_url=_read_optional_str(source, "NEO4J_URL"),
        storage_type=_read_str(source, "ATLAS_STORAGE_TYPE", "filesystem"),
        storage_path=_read_optional_str(source, "ATLAS_STORAGE_PATH"),
        s3_bucket=_read_optional_str(source, "AWS_S3_BUCKET"),
        # Security
        rate_limit_enabled=_read_bool(source, "ATLAS_RATE_LIMIT_ENABLED", True),
        jwt_secret=_read_optional_str(source, "ATLAS_JWT_SECRET"),

        # M6: Document Intelligence
        documents_storage_path=_read_optional_str(source, "ATLAS_DOCUMENTS_PATH"),
        ocr_provider=_read_str(source, "ATLAS_OCR_PROVIDER", "tesseract"),
        max_document_size_mb=int(_read_str(source, "ATLAS_MAX_DOCUMENT_SIZE_MB", "100")),
        chunking_strategy=_read_str(source, "ATLAS_CHUNKING_STRATEGY", "semantic"),
        chunk_min_size=int(_read_str(source, "ATLAS_CHUNK_MIN_SIZE", "100")),
        chunk_max_size=int(_read_str(source, "ATLAS_CHUNK_MAX_SIZE", "2000")),
        # M7: Projects & Knowledge
        knowledge_graph_enabled=_read_bool(source, "ATLAS_KNOWLEDGE_GRAPH_ENABLED", False),
        # M8: Local Intelligence
        local_models_enabled=_read_bool(source, "ATLAS_LOCAL_MODELS_ENABLED", True),
        ollama_base_url=_read_str(source, "OLLAMA_BASE_URL", "http://localhost:11434"),
        local_embedding_model=_read_str(source, "ATLAS_LOCAL_EMBEDDING_MODEL", "nomic-embed-text"),
        local_llm_model=_read_str(source, "ATLAS_LOCAL_LLM_MODEL", "mistral-7b"),
        local_cache_max_size=int(_read_str(source, "ATLAS_LOCAL_CACHE_MAX_SIZE", "1000")),
        local_memory_max_entries=int(_read_str(source, "ATLAS_LOCAL_MEMORY_MAX_ENTRIES", "10000")),
    )


def _read_str(environ: Mapping[str, str], key: str, default: str) -> str:
    value = environ.get(key)
    if value is None or value == "":
        return default
    return value


def _read_optional_str(environ: Mapping[str, str], key: str) -> str | None:
    value = environ.get(key)
    if value is None or value == "":
        return None
    return value


def _read_bool(environ: Mapping[str, str], key: str, default: bool) -> bool:
    value = environ.get(key)
    if value is None or value == "":
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{key} must be a boolean value")


def _read_tuple(environ: Mapping[str, str], key: str) -> tuple[str, ...]:
    value = environ.get(key)
    if value is None or value.strip() == "":
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())
