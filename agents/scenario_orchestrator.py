# agents/scenario_orchestrator.py

from core.agent_base import BaseAgent
from core.memory import Memory
from agents.strategy_planner import StrategyPlanner
from agents.market_analyst import MarketAnalyst
# Placeholder import for scenario generation (to be created next)
from agents.scenario_generator import ScenarioGenerator

import threading
import json


class ScenarioOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__("ScenarioOrchestrator")
        self.memory = Memory()
        self.strategy_planner = StrategyPlanner()
        self.market_analyst = MarketAnalyst()
        self.scenario_generator = ScenarioGenerator()

    def run_cycle(self):
        self.log("🎯 Starting Scenario Orchestration Cycle...")

        goal = self.memory.load("latest_goal")
        if not goal:
            self.logger.warning("⚠️ No user goal found. Aborting orchestration.")
            return

        # === Phase 1: Generate contextual scenario ===
        self.log("🧱 Generating scenario context from user goal...")
        scenario = self.scenario_generator.run(goal)
        self.memory.save("active_scenario", scenario)

        self.log("⚙️ Launching StrategyPlanner and MarketAnalyst in parallel...")

        strategy_result = {}
        market_result = {}

        def plan():
            result = self.strategy_planner.run_cycle()
            if result:
                strategy_result.update(result)

        def analyze():
            # Wait until the strategy is available in memory
            self.market_analyst.run_cycle(self.memory.load("proposed_strategy"))
            market_result.update(self.memory.load("evaluated_strategy") or {})

        t1 = threading.Thread(target=plan)
        t2 = threading.Thread(target=analyze)

        t1.start()
        t1.join()  # Ensure the strategy is written to memory before analysis begins
        t2.start()
        t2.join()

        self.log("🧩 Strategy and market analysis complete.")
        self.memory.save("orchestrated_output", {
            "goal": goal,
            "strategy": strategy_result,
            "evaluated_strategy": market_result
        })

        self.logger.info("✅ Orchestration cycle complete.")
