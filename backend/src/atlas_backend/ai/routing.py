"""AI provider routing and selection logic."""

from __future__ import annotations

from atlas_backend.ai.config import ProviderType, AIProviderConfig, get_model_metadata


class ProviderRouter:
    """Routes requests to appropriate AI providers based on model and configuration."""

    def __init__(self, config: AIProviderConfig) -> None:
        self.config = config

    def get_provider_for_model(self, model_id: str) -> ProviderType:
        """Get the provider type for a model ID."""
        metadata = get_model_metadata(model_id)
        if metadata is None:
            return self.config.default_provider
        return metadata.provider

    def get_llm_provider(self, model_id: str) -> ProviderType:
        """Get the LLM provider for a model."""
        return self.get_provider_for_model(model_id)

    def get_embedding_provider(self) -> ProviderType:
        """Get the configured embedding provider."""
        return self.config.embedding_provider

    def get_search_provider(self) -> str:
        """Get the configured search provider."""
        return self.config.search_provider

    def validate_configuration(self) -> bool:
        """Validate that required API keys are present for configured providers."""
        if self.config.default_provider == ProviderType.OPENAI and not self.config.openai_api_key:
            return False
        if self.config.default_provider == ProviderType.ANTHROPIC and not self.config.anthropic_api_key:
            return False
        if self.config.default_provider == ProviderType.GOOGLE and not self.config.google_api_key:
            return False
        if self.config.default_provider == ProviderType.DEEPSEEK and not self.config.deepseek_api_key:
            return False
        return True
