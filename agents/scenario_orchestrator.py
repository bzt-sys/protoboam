# agents/scenario_orchestrator.py

from core.agent_base import BaseAgent
from core.memory import Memory
from agents.strategy_planner import StrategyPlanner
from agents.market_analyst import MarketAnalyst
from agents.scenario_generator import ScenarioGenerator


class ScenarioOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__("ScenarioOrchestrator")
        self.memory = Memory()
        self.strategy_planner = StrategyPlanner()
        self.market_analyst = MarketAnalyst()
        self.scenario_generator = ScenarioGenerator()

    def run_cycle(self):
        self.log("🎯 Starting Scenario Orchestration Cycle...")

        # Step 1: Load the user's goal
        goal = self.memory.load("latest_goal")
        if not goal:
            self.logger.warning("⚠️ No user goal found. Aborting orchestration.")
            return None

        # Step 2: Generate a contextual scenario
        self.log("🧱 Generating scenario context from user goal...")
        scenario = self.scenario_generator.run(goal)
        self.memory.save("active_scenario", scenario)

        # Step 3: Run MarketAnalyst first to extract market conditions
        self.log("📊 Running MarketAnalyst to extract context...")
        self.market_analyst.run_cycle(goal)

        # Step 4: Use market-informed context to plan strategy
        self.log("🧠 Running StrategyPlanner using market-informed context...")
        strategy_result = self.strategy_planner.run_cycle()

        # Step 5: Save orchestrated results to memory
        evaluated = self.memory.load("evaluated_strategy") or {}
        orchestrated_output = {
            "goal": goal,
            "scenario": scenario,
            "strategy": strategy_result,
            "evaluated_strategy": evaluated
        }
        self.memory.save("orchestrated_output", orchestrated_output)

        self.logger.info("✅ Scenario orchestration complete.")

        # Step 6: Return structured result for downstream agent
        return {
            "scenario": scenario,
            "plan": evaluated.get("evaluated_steps", strategy_result.get("steps", []))
        }
