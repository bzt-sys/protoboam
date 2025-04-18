# simulation/simulation_manager.py

import logging
from core.orchestrator import AgentOrchestrator
from config.settings import load_config
from core.scenario_loader import load_scenario, apply_scenario

logger = logging.getLogger("SimulationManager")

class SimulationManager:
    def __init__(self, scenario_path: str = None):
        self.config = load_config()
        self.scenario_path = scenario_path or self.config.get("scenario_path")
        self.orchestrator = AgentOrchestrator(mode=self.config.get("mode", "auto"))

    def load_initial_scenario(self):
        """
        If a scenario file is provided, load it and inject it into memory.
        """
        if self.scenario_path:
            try:
                scenario = load_scenario(self.scenario_path)
                apply_scenario(scenario)
                logger.info("🎯 Scenario applied successfully.")
            except Exception as e:
                logger.error(f"❌ Error applying scenario: {e}")
        else:
            logger.info("ℹ️ No scenario specified — starting with blank memory.")

    def run(self):
        self.load_initial_scenario()
        self.orchestrator.run()
