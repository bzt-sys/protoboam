# core/scenario_loader.py

import json
import logging
from pathlib import Path
from core.memory import Memory

logger = logging.getLogger("ScenarioLoader")

def load_scenario(path: str) -> dict:
    """
    Loads and parses a scenario file.
    """
    try:
        scenario_path = Path(path)
        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {path}")

        with open(scenario_path, "r") as f:
            scenario = json.load(f)

        logger.info(f"✅ Loaded scenario: {scenario.get('name', 'Unnamed')}")
        return scenario

    except Exception as e:
        logger.error(f"❌ Failed to load scenario: {e}")
        raise

def apply_scenario(scenario: dict):
    """
    Applies the scenario data to agent memory using Memory interface.
    """
    if not scenario or "events" not in scenario:
        logger.warning("⚠️ No events found in scenario.")
        return

    for event in scenario["events"]:
        agent = event.get("agent")
        memory_key = event.get("memory_key")
        payload = event.get("payload")

        if not agent or not memory_key:
            logger.warning(f"⚠️ Skipping incomplete event: {event}")
            continue

        memory = Memory(agent, persist=True)
        memory.save(memory_key, payload)
        logger.info(f"📦 Injected payload for '{agent}' -> '{memory_key}'")
