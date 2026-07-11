"""AI provider health checking."""

from __future__ import annotations

from enum import StrEnum


class ProviderHealth(StrEnum):
    """Health state for AI providers."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ProviderHealthCheck:
    """Health check result for an AI provider."""

    def __init__(self, provider_name: str, status: ProviderHealth, message: str) -> None:
        self.provider_name = provider_name
        self.status = status
        self.message = message

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider": self.provider_name,
            "status": self.status.value,
            "message": self.message,
        }


async def check_llm_provider_health(provider_name: str, provider: Any) -> ProviderHealthCheck:
    """Check LLM provider health."""
    try:
        is_healthy = await provider.health_check()
        status = ProviderHealth.HEALTHY if is_healthy else ProviderHealth.UNAVAILABLE
        message = f"{provider_name} is available." if is_healthy else f"{provider_name} is unavailable."
    except Exception as e:
        status = ProviderHealth.UNAVAILABLE
        message = f"{provider_name} health check failed: {str(e)}"

    return ProviderHealthCheck(provider_name, status, message)


async def check_embedding_provider_health(provider_name: str, provider: Any) -> ProviderHealthCheck:
    """Check embedding provider health."""
    try:
        is_healthy = await provider.health_check()
        status = ProviderHealth.HEALTHY if is_healthy else ProviderHealth.UNAVAILABLE
        message = f"{provider_name} embeddings available." if is_healthy else f"{provider_name} embeddings unavailable."
    except Exception as e:
        status = ProviderHealth.UNAVAILABLE
        message = f"{provider_name} embedding health check failed: {str(e)}"

    return ProviderHealthCheck(provider_name, status, message)


async def check_search_provider_health(provider_name: str, provider: Any) -> ProviderHealthCheck:
    """Check search provider health."""
    try:
        is_healthy = await provider.health_check()
        status = ProviderHealth.HEALTHY if is_healthy else ProviderHealth.UNAVAILABLE
        message = f"{provider_name} search available." if is_healthy else f"{provider_name} search unavailable."
    except Exception as e:
        status = ProviderHealth.UNAVAILABLE
        message = f"{provider_name} search health check failed: {str(e)}"

    return ProviderHealthCheck(provider_name, status, message)
