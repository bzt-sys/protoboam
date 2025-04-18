# agents/strategy_planner.py

from core.agent_base import BaseAgent
from core.memory import Memory
from llm.local_llm import call_local_llm
import json

class StrategyPlanner(BaseAgent):
    def __init__(self):
        super().__init__("StrategyPlanner")
        self.memory = Memory()
        self.scenario_context = self.load_scenario_corpora()

    def load_scenario_corpora(self) -> str:
        corpora = self.memory.load("active_corpora")
        if corpora:
            self.logger.info("📚 Scenario corpora loaded for strategy context.")
            return corpora.get("text", "")
        else:
            self.logger.info("ℹ️ No scenario corpora found. Proceeding without extra context.")
            return ""

    def plan_strategy(self, goal: dict) -> dict:
        try:
            prompt_parts = [
                "You are a financial strategy agent operating under strict formatting rules.",
                "Generate a viable investment plan based on the user's goal below. Consider the context, risk tolerance, and return expectations.",
                f"USER GOAL:\n{json.dumps(goal, indent=4)}"
            ]

            if self.scenario_context:
                prompt_parts.append("CONTEXTUAL SCENARIO:\n" + self.scenario_context)

            prompt_parts.append(
                "\nRespond ONLY in valid JSON format with this schema:\n"
                "{ \"steps\": [ { \"action\": \"...\", \"justification\": \"...\", \"expected_roi\": \"...%\" }, ... ] }"
            )

            final_prompt = "\n\n---\n\n".join(prompt_parts)
            response = call_local_llm(final_prompt)

            # Extract JSON
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON object found in LLM response.")

            parsed = json.loads(response[start_idx:end_idx])
            return parsed

        except json.JSONDecodeError:
            self.logger.error("❌ Failed to parse strategy from LLM response.")
            return {}

        except Exception as e:
            self.logger.exception(f"🧨 Exception during strategy planning: {e}")
            return {}

    def run_cycle(self):
        goal = self.memory.load("latest_goal")
        if not goal:
            self.logger.warning("⚠️ No user goal found. Skipping strategy planning.")
            return

        self.log("🧠 Generating strategy from goal and scenario...")

        strategy = self.plan_strategy(goal)
        if strategy:
            self.memory.save("latest_strategy", strategy)
            self.log("✅ Strategy saved to memory.")
        else:
            self.logger.error("❌ Strategy generation failed.")
