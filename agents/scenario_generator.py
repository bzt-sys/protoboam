# agents/scenario_generator.py

from core.agent_base import BaseAgent
from core.memory import Memory
import json
import random


class ScenarioGenerator(BaseAgent):
    def __init__(self, dev_mode: bool = False):
        super().__init__("ScenarioGenerator")
        self.memory = Memory()
        self.dev_mode = dev_mode

    def run(self, goal: str) -> dict:
        """
        Generate a scenario context based on the user goal.
        This stub version simulates generation using canned logic.
        """
        self.log("🧱 Generating scenario context from user goal...")

        if self.dev_mode:
            self.log("🧪 [DEV MODE] Using static scenario for development.")
            scenario = self.mock_scenario(goal)
        else:
            scenario = self.generate_scenario(goal)

        self.memory.save("active_scenario", scenario)
        self.log("✅ Scenario context saved to memory.")
        return scenario

    def generate_scenario(self, goal: str) -> dict:
        """
        Future implementation: Use LLM, web scraping, corpora, or heuristics
        to produce a realistic financial scenario from the goal.
        """
        # TODO: Implement LLM or web-enhanced scenario synthesis
        return self.mock_scenario(goal)

    def mock_scenario(self, goal: str) -> dict:
        """
        Placeholder for scenario generation.
        """
        example_sectors = ["tech", "energy", "real estate", "crypto"]
        time_horizons = ["short-term", "mid-term", "long-term"]
        macro_factors = ["inflation", "interest rates", "regulation", "global events"]

        return {
            "goal": goal,
            "sector": random.choice(example_sectors),
            "time_horizon": random.choice(time_horizons),
            "macro_factors": random.sample(macro_factors, k=2),
            "description": f"A simulated scenario based on user goal: {goal}"
        }
