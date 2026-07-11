"""Local model registry and metadata."""

from typing import Optional

from pydantic import BaseModel


class LocalModel(BaseModel):
    """Local model metadata."""
    model_id: str
    name: str
    provider: str  # ollama, huggingface, llama-cpp, etc.
    type: str  # llm, embedding, vision
    quantization: str  # q4, q5, q8, fp16, fp32
    context_window: int
    parameters: str  # 7b, 13b, 70b, etc.
    download_size_gb: float
    vram_required_gb: float
    ram_required_gb: float
    max_tokens: int
    supports_gpu: bool = True
    supports_mps: bool = False  # Metal Performance Shaders (Apple)
    url: Optional[str] = None
    description: Optional[str] = None


class LocalModelRegistry:
    """Registry of available local models."""

    MODELS = {
        # Mistral models
        "mistral-7b": LocalModel(
            model_id="mistral-7b",
            name="Mistral 7B",
            provider="ollama",
            type="llm",
            quantization="q4",
            context_window=8192,
            parameters="7b",
            download_size_gb=3.9,
            vram_required_gb=4,
            ram_required_gb=8,
            max_tokens=8192,
        ),
        # Llama models
        "llama2-7b": LocalModel(
            model_id="llama2-7b",
            name="Llama 2 7B",
            provider="ollama",
            type="llm",
            quantization="q4",
            context_window=4096,
            parameters="7b",
            download_size_gb=3.8,
            vram_required_gb=4,
            ram_required_gb=8,
            max_tokens=4096,
        ),
        "llama2-13b": LocalModel(
            model_id="llama2-13b",
            name="Llama 2 13B",
            provider="ollama",
            type="llm",
            quantization="q4",
            context_window=4096,
            parameters="13b",
            download_size_gb=7.5,
            vram_required_gb=8,
            ram_required_gb=16,
            max_tokens=4096,
        ),
        # Gemma models
        "gemma-7b": LocalModel(
            model_id="gemma-7b",
            name="Gemma 7B",
            provider="ollama",
            type="llm",
            quantization="q4",
            context_window=8192,
            parameters="7b",
            download_size_gb=3.9,
            vram_required_gb=4,
            ram_required_gb=8,
            max_tokens=8192,
        ),
        # Qwen models
        "qwen-7b": LocalModel(
            model_id="qwen-7b",
            name="Qwen 7B",
            provider="ollama",
            type="llm",
            quantization="q4",
            context_window=8192,
            parameters="7b",
            download_size_gb=4.0,
            vram_required_gb=4,
            ram_required_gb=8,
            max_tokens=8192,
        ),
        # Embedding models
        "nomic-embed-text": LocalModel(
            model_id="nomic-embed-text",
            name="Nomic Embed Text",
            provider="ollama",
            type="embedding",
            quantization="fp32",
            context_window=2048,
            parameters="274m",
            download_size_gb=0.3,
            vram_required_gb=1,
            ram_required_gb=2,
            max_tokens=2048,
        ),
    }

    @classmethod
    def get_model(cls, model_id: str) -> Optional[LocalModel]:
        """Get model by ID."""
        return cls.MODELS.get(model_id)

    @classmethod
    def list_models(cls, model_type: Optional[str] = None) -> list[LocalModel]:
        """List available models, optionally filtered by type."""
        models = list(cls.MODELS.values())
        if model_type:
            models = [m for m in models if m.type == model_type]
        return models

    @classmethod
    def list_llm_models(cls) -> list[LocalModel]:
        """List available LLM models."""
        return cls.list_models("llm")

    @classmethod
    def list_embedding_models(cls) -> list[LocalModel]:
        """List available embedding models."""
        return cls.list_models("embedding")
