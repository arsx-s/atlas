"""Local runtime health checks."""

from typing import Optional

from pydantic import BaseModel

from .hardware import HardwareDetector, GPUConfig
from .models import LocalModelRegistry


class LocalRuntimeHealth(BaseModel):
    """Local runtime health status."""
    healthy: bool
    gpu_available: bool
    gpu_config: Optional[GPUConfig] = None
    cpu_cores: int
    ram_available_gb: float
    local_models_available: int
    embedding_models_available: int


async def check_local_runtime_health() -> LocalRuntimeHealth:
    """Check health of local runtime."""
    try:
        gpu_config = await HardwareDetector.detect_gpu()
    except Exception:
        gpu_config = GPUConfig()

    try:
        cpu_cores = await HardwareDetector.detect_cpu_cores()
    except Exception:
        cpu_cores = 0

    try:
        ram_available_gb = await HardwareDetector.detect_ram_available_gb()
    except Exception:
        ram_available_gb = 0

    llm_models = LocalModelRegistry.list_llm_models()
    embedding_models = LocalModelRegistry.list_embedding_models()

    return LocalRuntimeHealth(
        healthy=cpu_cores > 0 and ram_available_gb > 0,
        gpu_available=gpu_config.available,
        gpu_config=gpu_config,
        cpu_cores=cpu_cores,
        ram_available_gb=ram_available_gb,
        local_models_available=len(llm_models),
        embedding_models_available=len(embedding_models),
    )
