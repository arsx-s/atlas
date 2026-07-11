"""Unit tests for AI provider abstractions (Milestone 4)."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from atlas_backend.ai.config import (
    ProviderType,
    ModelFamily,
    AIProviderConfig,
    ModelMetadata,
    get_model_metadata,
    MODELS,
)
from atlas_backend.ai.routing import ProviderRouter
from atlas_backend.ai.providers.llm import LLMProvider
from atlas_backend.ai.providers.embedding import EmbeddingProvider
from atlas_backend.ai.providers.search import SearchProvider


class AIProviderTests(unittest.TestCase):
    """Test AI provider abstractions."""

    def test_model_metadata_exists_for_gpt4(self) -> None:
        """Verify model metadata is registered for GPT-4."""
        metadata = get_model_metadata("gpt-4")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.provider, ProviderType.OPENAI)
        self.assertEqual(metadata.family, ModelFamily.GPT)
        self.assertEqual(metadata.context_window, 8192)

    def test_model_metadata_exists_for_claude(self) -> None:
        """Verify model metadata is registered for Claude."""
        metadata = get_model_metadata("claude-3-opus-20240229")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.provider, ProviderType.ANTHROPIC)
        self.assertEqual(metadata.family, ModelFamily.CLAUDE)
        self.assertTrue(metadata.supports_vision)

    def test_model_metadata_exists_for_gemini(self) -> None:
        """Verify model metadata is registered for Gemini."""
        metadata = get_model_metadata("gemini-2.0-flash")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.provider, ProviderType.GOOGLE)
        self.assertEqual(metadata.family, ModelFamily.GEMINI)
        self.assertEqual(metadata.context_window, 1000000)

    def test_model_metadata_exists_for_deepseek(self) -> None:
        """Verify model metadata is registered for DeepSeek."""
        metadata = get_model_metadata("deepseek-chat")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.provider, ProviderType.DEEPSEEK)

    def test_model_metadata_exists_for_local_models(self) -> None:
        """Verify model metadata is registered for local models."""
        for model_id in ["mistral-large", "llama-2-70b", "gemma-7b", "qwen-14b"]:
            metadata = get_model_metadata(model_id)
            self.assertIsNotNone(metadata)
            self.assertEqual(metadata.provider, ProviderType.LOCAL)

    def test_embedding_model_metadata(self) -> None:
        """Verify embedding model metadata is registered."""
        metadata = get_model_metadata("text-embedding-3-large")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.provider, ProviderType.OPENAI)
        self.assertEqual(metadata.context_window, 8191)

    def test_models_registry_contains_all_models(self) -> None:
        """Verify MODELS registry has expected count."""
        self.assertGreaterEqual(len(MODELS), 14)

    def test_llm_provider_interface_is_abstract(self) -> None:
        """Verify LLM provider interface cannot be instantiated."""
        with self.assertRaises(TypeError):
            LLMProvider()

    def test_embedding_provider_interface_is_abstract(self) -> None:
        """Verify embedding provider interface cannot be instantiated."""
        with self.assertRaises(TypeError):
            EmbeddingProvider()

    def test_search_provider_interface_is_abstract(self) -> None:
        """Verify search provider interface cannot be instantiated."""
        with self.assertRaises(TypeError):
            SearchProvider()

    def test_ai_provider_config_defaults(self) -> None:
        """Verify AI provider config has sensible defaults."""
        config = AIProviderConfig()
        self.assertEqual(config.default_provider, ProviderType.OPENAI)
        self.assertEqual(config.openai_model, "gpt-4")
        self.assertEqual(config.anthropic_model, "claude-3-opus-20240229")
        self.assertTrue(config.enable_streaming)
        self.assertEqual(config.max_retries, 3)

    def test_ai_provider_config_with_api_keys(self) -> None:
        """Verify AI provider config accepts API keys."""
        config = AIProviderConfig(
            openai_api_key="sk-test",
            anthropic_api_key="sk-ant-test",
            default_provider=ProviderType.OPENAI,
        )
        self.assertEqual(config.openai_api_key, "sk-test")
        self.assertEqual(config.anthropic_api_key, "sk-ant-test")

    def test_provider_router_gets_provider_for_model(self) -> None:
        """Verify provider router returns correct provider for model."""
        config = AIProviderConfig(openai_api_key="sk-test")
        router = ProviderRouter(config)

        self.assertEqual(router.get_provider_for_model("gpt-4"), ProviderType.OPENAI)
        self.assertEqual(router.get_provider_for_model("claude-3-opus-20240229"), ProviderType.ANTHROPIC)
        self.assertEqual(router.get_provider_for_model("gemini-2.0-flash"), ProviderType.GOOGLE)

    def test_provider_router_gets_llm_provider(self) -> None:
        """Verify provider router returns LLM provider."""
        config = AIProviderConfig(openai_api_key="sk-test")
        router = ProviderRouter(config)
        provider = router.get_llm_provider("gpt-4")
        self.assertEqual(provider, ProviderType.OPENAI)

    def test_provider_router_gets_embedding_provider(self) -> None:
        """Verify provider router returns configured embedding provider."""
        config = AIProviderConfig(embedding_provider=ProviderType.OPENAI)
        router = ProviderRouter(config)
        provider = router.get_embedding_provider()
        self.assertEqual(provider, ProviderType.OPENAI)

    def test_provider_router_gets_search_provider(self) -> None:
        """Verify provider router returns configured search provider."""
        config = AIProviderConfig(search_provider="tavily")
        router = ProviderRouter(config)
        provider = router.get_search_provider()
        self.assertEqual(provider, "tavily")

    def test_provider_router_validates_configuration(self) -> None:
        """Verify provider router validates configuration."""
        config_missing_key = AIProviderConfig(default_provider=ProviderType.OPENAI)
        router_missing_key = ProviderRouter(config_missing_key)
        self.assertFalse(router_missing_key.validate_configuration())

        config_with_key = AIProviderConfig(
            default_provider=ProviderType.OPENAI,
            openai_api_key="sk-test",
        )
        router_with_key = ProviderRouter(config_with_key)
        self.assertTrue(router_with_key.validate_configuration())

    def test_model_metadata_cost_tracking(self) -> None:
        """Verify model metadata includes cost data."""
        gpt4 = get_model_metadata("gpt-4")
        self.assertGreater(gpt4.cost_per_1k_input, 0)
        self.assertGreater(gpt4.cost_per_1k_output, 0)

    def test_model_metadata_capability_flags(self) -> None:
        """Verify model metadata includes capability flags."""
        claude = get_model_metadata("claude-3-opus-20240229")
        self.assertTrue(claude.supports_vision)
        self.assertTrue(claude.supports_function_calling)

        local_llama = get_model_metadata("llama-2-70b")
        self.assertFalse(local_llama.supports_vision)
        self.assertFalse(local_llama.supports_function_calling)


if __name__ == "__main__":
    unittest.main()
