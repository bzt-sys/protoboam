import os
import psutil
import platform
import subprocess
import json

# Optional: Import pynvml to detect GPU VRAM if available
try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
except pynvml.NVMLError:
    GPU_AVAILABLE = False

MODES = {
    "lite": "Lite Mode",
    "balanced": "Balanced Mode",
    "enhanced": "Enhanced Mode"
}

def detect_gpu_info():
    if not GPU_AVAILABLE:
        return None
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        name = pynvml.nvmlDeviceGetName(handle)
        return {
            "name": name.decode() if isinstance(name, bytes) else name,
            "total_vram_gb": round(mem_info.total / (1024 ** 3), 2)
        }
    except Exception as e:
        return None

def detect_hardware():
    cpu_count = psutil.cpu_count(logical=True)
    total_ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    gpu_info = detect_gpu_info()

    return {
        "cpu_cores": cpu_count,
        "ram_gb": total_ram,
        "gpu": gpu_info,
        "os": platform.system()
    }

def determine_mode(hw):
    """Basic thresholds — may be improved over time or by feedback loops"""
    if hw['ram_gb'] < 16 or hw['cpu_cores'] < 8:
        return "lite"
    elif hw['ram_gb'] >= 32 and (hw.get("gpu", {}).get("total_vram_gb", 0) >= 8):
        return "balanced"
    elif hw['ram_gb'] >= 48 and hw['cpu_cores'] >= 12 and hw.get("gpu", {}).get("total_vram_gb", 0) >= 12:
        return "enhanced"
    return "lite"

def boot_system(selected_mode=None):
    hw = detect_hardware()
    mode = selected_mode or determine_mode(hw)

    print(f"🚀 Booting in {MODES.get(mode)} based on detected hardware:")
    print(json.dumps(hw, indent=2))

    # REVIEW: May want to persist this info to a state file
    return mode, hw

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=MODES.keys(), help="Override auto-detection")
    args = parser.parse_args()

    boot_system(args.mode)
