"""AI provider configuration and model metadata."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ProviderType(StrEnum):
    """Supported AI provider types."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    LOCAL = "local"


class ModelFamily(StrEnum):
    """Supported model families."""

    GPT = "gpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    DEEPSEEK_CHAT = "deepseek-chat"
    MISTRAL = "mistral"
    LLAMA = "llama"
    GEMMA = "gemma"
    QWEN = "qwen"


class ModelMetadata(BaseModel):
    """Metadata for an AI model."""

    model_id: str
    provider: ProviderType
    family: ModelFamily
    context_window: int
    max_output: int
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_streaming: bool = True


class AIProviderConfig(BaseModel):
    """Configuration for AI providers."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-4"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-opus-20240229"
    google_api_key: str | None = None
    google_model: str = "gemini-2.0-flash"
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-chat"
    local_model_path: str | None = None
    default_provider: ProviderType = ProviderType.OPENAI
    embedding_provider: ProviderType = ProviderType.OPENAI
    embedding_model: str = "text-embedding-3-large"
    search_provider: str = "tavily"
    tavily_api_key: str | None = None
    brave_api_key: str | None = None
    enable_streaming: bool = True
    max_retries: int = 3
    timeout_seconds: int = 60


MODELS: dict[str, ModelMetadata] = {
    "gpt-4": ModelMetadata(
        model_id="gpt-4",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT,
        context_window=8192,
        max_output=4096,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06,
        supports_vision=False,
        supports_function_calling=True,
    ),
    "gpt-4-turbo": ModelMetadata(
        model_id="gpt-4-turbo",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT,
        context_window=128000,
        max_output=4096,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "gpt-4o": ModelMetadata(
        model_id="gpt-4o",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT,
        context_window=128000,
        max_output=4096,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "gpt-4o-mini": ModelMetadata(
        model_id="gpt-4o-mini",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT,
        context_window=128000,
        max_output=4096,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "claude-3-opus-20240229": ModelMetadata(
        model_id="claude-3-opus-20240229",
        provider=ProviderType.ANTHROPIC,
        family=ModelFamily.CLAUDE,
        context_window=200000,
        max_output=4096,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "claude-3-sonnet-20240229": ModelMetadata(
        model_id="claude-3-sonnet-20240229",
        provider=ProviderType.ANTHROPIC,
        family=ModelFamily.CLAUDE,
        context_window=200000,
        max_output=4096,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "claude-3-haiku-20240307": ModelMetadata(
        model_id="claude-3-haiku-20240307",
        provider=ProviderType.ANTHROPIC,
        family=ModelFamily.CLAUDE,
        context_window=200000,
        max_output=4096,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "gemini-2.0-flash": ModelMetadata(
        model_id="gemini-2.0-flash",
        provider=ProviderType.GOOGLE,
        family=ModelFamily.GEMINI,
        context_window=1000000,
        max_output=8192,
        cost_per_1k_input=0.075,
        cost_per_1k_output=0.3,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "gemini-1.5-pro": ModelMetadata(
        model_id="gemini-1.5-pro",
        provider=ProviderType.GOOGLE,
        family=ModelFamily.GEMINI,
        context_window=1000000,
        max_output=8192,
        cost_per_1k_input=0.0035,
        cost_per_1k_output=0.0105,
        supports_vision=True,
        supports_function_calling=True,
    ),
    "deepseek-chat": ModelMetadata(
        model_id="deepseek-chat",
        provider=ProviderType.DEEPSEEK,
        family=ModelFamily.DEEPSEEK_CHAT,
        context_window=64000,
        max_output=4096,
        cost_per_1k_input=0.0014,
        cost_per_1k_output=0.0028,
        supports_vision=False,
        supports_function_calling=True,
    ),
    "mistral-large": ModelMetadata(
        model_id="mistral-large",
        provider=ProviderType.LOCAL,
        family=ModelFamily.MISTRAL,
        context_window=32000,
        max_output=8192,
        supports_function_calling=True,
    ),
    "llama-2-70b": ModelMetadata(
        model_id="llama-2-70b",
        provider=ProviderType.LOCAL,
        family=ModelFamily.LLAMA,
        context_window=4096,
        max_output=4096,
        supports_function_calling=False,
    ),
    "gemma-7b": ModelMetadata(
        model_id="gemma-7b",
        provider=ProviderType.LOCAL,
        family=ModelFamily.GEMMA,
        context_window=8192,
        max_output=8192,
        supports_function_calling=False,
    ),
    "qwen-14b": ModelMetadata(
        model_id="qwen-14b",
        provider=ProviderType.LOCAL,
        family=ModelFamily.QWEN,
        context_window=4096,
        max_output=2048,
        supports_function_calling=True,
    ),
    "text-embedding-3-large": ModelMetadata(
        model_id="text-embedding-3-large",
        provider=ProviderType.OPENAI,
        family=ModelFamily.GPT,
        context_window=8191,
        max_output=1,
    ),
}


def get_model_metadata(model_id: str) -> ModelMetadata | None:
    """Get metadata for a model by ID."""
    return MODELS.get(model_id)
