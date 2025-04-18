# utils/resource_monitor.py

import psutil
import logging

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

logger = logging.getLogger("ResourceMonitor")

def get_system_load():
    """
    Returns a dictionary with current system resource usage.
    Includes CPU, RAM, and optionally GPU (if available).
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent

    system_load = {
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent
    }

    if NVML_AVAILABLE:
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # default GPU
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)

            system_load["gpu_memory_used"] = mem_info.used / 1024**2  # in MB
            system_load["gpu_memory_total"] = mem_info.total / 1024**2
            system_load["gpu_utilization"] = gpu_util.gpu
        except Exception as e:
            logger.warning(f"NVML GPU query failed: {e}")

    return system_load
