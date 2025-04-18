# config/settings.py

import os
import json
from pathlib import Path

CONFIG_PATH = Path("./config/current_settings.json")
DEFAULT_MODE = "lite"

# ⚠️ You may want to lock this path for VM safety later

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"mode": DEFAULT_MODE}

def save_config(config_data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)

def get_current_mode():
    config = load_config()
    return config.get("mode", DEFAULT_MODE)

def set_mode(new_mode):
    config = load_config()
    config["mode"] = new_mode
    save_config(config)

def is_mode(mode_name):
    return get_current_mode() == mode_name

# config/settings.py

def get_jurisdiction() -> str:
    """
    Returns the current financial/tax jurisdiction for compliance agents.
    Defaults to 'us_federal' if not set.
    
    TODO: Implement detection from config file, env var, or prompt.
    """
    return os.getenv("JURISDICTION", "us_federal")
 