"""M9: Desktop Local Runtime skeleton."""

from enum import Enum
from pydantic import BaseModel


class DesktopRuntimeMode(str, Enum):
    """Desktop runtime modes."""
    STARTUP = "startup"
    READY = "ready"
    RUNNING = "running"
    SHUTDOWN = "shutdown"


class DesktopConfig(BaseModel):
    """Desktop application configuration."""
    app_name: str = "Atlas"
    app_version: str = "0.1.0"
    window_width: int = 1400
    window_height: int = 900
    auto_update_enabled: bool = True
    system_tray_enabled: bool = True
    start_minimized: bool = False


class DesktopRuntimeInitializer:
    """Initializes desktop Electron runtime."""

    def __init__(self, config: DesktopConfig):
        self.config = config
        self.state = DesktopRuntimeMode.STARTUP

    async def initialize(self) -> bool:
        """Initialize desktop runtime."""
        raise NotImplementedError("Requires Electron main process integration")

    async def start_backend_server(self) -> bool:
        """Start FastAPI backend server."""
        raise NotImplementedError("Requires uvicorn subprocess management")

    async def initialize_file_system(self) -> bool:
        """Initialize local file system and profiles."""
        raise NotImplementedError("Requires OS file system integration")

    async def check_local_models(self) -> bool:
        """Check local model availability."""
        raise NotImplementedError("Requires Ollama integration check")

    async def ready(self) -> bool:
        """Mark runtime as ready."""
        self.state = DesktopRuntimeMode.READY
        return True

    async def shutdown(self) -> bool:
        """Graceful shutdown."""
        self.state = DesktopRuntimeMode.SHUTDOWN
        return True
