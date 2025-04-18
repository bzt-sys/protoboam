# memory/goal_memory.py

import json
import os
import logging

logger = logging.getLogger("Memory")

MEMORY_DIR = "data/goals"
MEMORY_FILE = os.path.join(MEMORY_DIR, "latest_goal.json")

def save_goal(goal_data: dict):
    """
    Saves the interpreted goal to disk in JSON format.
    """
    try:
        os.makedirs(MEMORY_DIR, exist_ok=True)
        with open(MEMORY_FILE, "w") as f:
            json.dump(goal_data, f, indent=4)
        logger.info("Saved goal to memory.")
    except Exception as e:
        logger.error(f"Failed to save goal: {e}")

def load_latest_goal() -> dict:
    """
    Loads the most recently interpreted goal.
    """
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("No goal file found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Corrupted goal file.")
        return {}
