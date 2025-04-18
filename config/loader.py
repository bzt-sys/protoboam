# config/loader.py

import json
import os

DEFAULT_CONFIG = {
    "mode": "auto",
    "live_mode": False,
    "enabled_agents": [
        "meta",
        "goal_interpreter",
        "strategy_planner",
        "market_analyst",
        "risk_manager",
        "execution_agent",
        "compliance_agent"
    ],
    "tax_reserve_ratio": 0.25,
    "meta_interval": 300,
    "risk_threshold": 0.3
}

def load_config(config_path="config/settings.json"):
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r") as f:
            user_config = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(user_config)
            return merged
    except Exception as e:
        print(f"⚠️ Failed to load config file: {e}")
        return DEFAULT_CONFIG
