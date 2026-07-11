"""GPU and hardware detection."""

import asyncio
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class GPUType(str, Enum):
    """Supported GPU types."""
    NVIDIA = "nvidia"  # CUDA
    AMD = "amd"  # ROCm
    APPLE = "apple"  # Metal
    NONE = "none"  # CPU only


class GPUConfig(BaseModel):
    """GPU configuration and capabilities."""
    available: bool = False
    gpu_type: GPUType = GPUType.NONE
    device_name: Optional[str] = None
    compute_capability: Optional[str] = None
    total_memory_gb: float = 0
    max_model_vram_gb: float = 0
    cudnn_version: Optional[str] = None
    driver_version: Optional[str] = None


class HardwareDetector:
    """Detects GPU and hardware capabilities."""

    @classmethod
    async def detect_gpu(cls) -> GPUConfig:
        """Detect available GPU."""
        # GPU detection requires external libraries (pycuda, torch, onnxruntime)
        # This is a contract definition.
        raise NotImplementedError("GPU detection requires external libraries")

    @classmethod
    async def detect_cpu_cores(cls) -> int:
        """Detect number of CPU cores."""
        import os
        return os.cpu_count() or 1

    @classmethod
    async def detect_ram_available_gb(cls) -> float:
        """Detect available system RAM."""
        import os

        try:
            import psutil
        except ImportError:
            if hasattr(os, "sysconf") and hasattr(os, "sysconf_names"):
                try:
                    page_size = os.sysconf("SC_PAGE_SIZE")
                    phys_pages = os.sysconf("SC_AVPHYS_PAGES")
                except (ValueError, OSError, AttributeError):
                    page_size = phys_pages = None
                if page_size and phys_pages:
                    return (page_size * phys_pages) / (1024 ** 3)

            try:
                import ctypes

                class MemoryStatusEx(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                status = MemoryStatusEx()
                status.dwLength = ctypes.sizeof(MemoryStatusEx)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                    return status.ullAvailPhys / (1024 ** 3)
            except Exception:
                pass

            return 0.0

        return psutil.virtual_memory().available / (1024 ** 3)

    @classmethod
    async def get_runtime_config(cls) -> dict:
        """Get full runtime configuration."""
        config = {
            "gpu": await cls.detect_gpu(),
            "cpu_cores": await cls.detect_cpu_cores(),
            "ram_available_gb": await cls.detect_ram_available_gb(),
        }
        return config
