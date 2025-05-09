# core/simulation_manager.py

import logging
from core.memory import Memory
from agents.scenario_orchestrator import ScenarioOrchestrator
from agents.logistics_orchestrator import LogisticsOrchestrator

logger = logging.getLogger("SimulationManager")

class SimulationManager:
    def __init__(self):
        logger.info("🧪 Initializing Simulation Manager...")
        self.memory = Memory()

        # ReAct-style orchestrators
        self.scenario_orchestrator = ScenarioOrchestrator()
        self.logistics_orchestrator = LogisticsOrchestrator()

    def load_scenario(self, scenario_path: str):
        """
        Load scenario from a JSON file and store its data in memory.
        """
        import json
        from pathlib import Path

        path = Path(scenario_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

        with open(path, "r") as f:
            scenario = json.load(f)

        self.memory.save("current_scenario", scenario)
        logger.info(f"📦 Scenario loaded: {scenario.get('name', 'Unnamed Scenario')}")

        # Preload scenario context into memory
        self.memory.save("scenario_tags", scenario.get("tags", []))
        self.memory.save("market_context", scenario.get("market_context", {}))
        self.memory.save("preconditions", scenario.get("preconditions", {}))

    def simulate_once(self, diagnostic: bool = False):
        """
        Run a single simulation cycle via orchestrators.
        """
        logger.info("▶️ Starting simulation cycle...")

        # Step 1: Scenario Orchestration
        scenario_output = self.scenario_orchestrator.run_cycle()
        if not scenario_output:
            logger.warning("⚠️ ScenarioOrchestrator returned no output. Aborting cycle.")
            return

        scenario_data = scenario_output.get("scenario")
        financial_plan = scenario_output.get("plan")

        if not financial_plan:
            logger.warning("⚠️ No financial plan generated. Aborting cycle.")
            return

        # Step 2: Logistics Orchestration
        self.logistics_orchestrator.run_cycle(
            scenario_data=scenario_data,
            plan=financial_plan
        )

        if diagnostic:
            self.print_diagnostics()

        logger.info("✅ Simulation cycle complete.")

    def simulate_batch(self, cycles: int = 5):
        for i in range(cycles):
            logger.info(f"\n🔁 Simulation cycle {i + 1}/{cycles}")
            self.simulate_once()

    def print_diagnostics(self):
        current = self.memory.recall("current_scenario", default={})
        if current:
            logger.info(f"🧾 Scenario: {current.get('name')} | Tags: {current.get('tags', [])}")

        for agent_name in ["ScenarioOrchestrator", "LogisticsOrchestrator"]:
            agent_mem = Memory()
            logger.debug(f"[{agent_name}] Memory: {agent_mem.snapshot()}")
