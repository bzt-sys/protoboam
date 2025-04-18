import json
from core.agent_base import BaseAgent
from core.memory import Memory
from llm.local_llm import call_local_llm


class GoalInterpreter(BaseAgent):
    def __init__(self):
        super().__init__("GoalInterpreter")
        self.memory = Memory()

    def run_cycle(self):
        self.log("🔍 Running Goal Interpreter cycle...")

        prompt = self.memory.load("latest_prompt")
        if not prompt:
            self.logger.warning("⚠️ No user prompt found. Aborting goal interpretation.")
            return

        llm_prompt = self.build_goal_prompt(prompt)
        response = call_local_llm(llm_prompt)

        try:
            parsed_goal = self.extract_goal(response)
        except Exception as e:
            self.logger.error(f"❌ Failed to parse goal: {e}")
            return

        if not parsed_goal.get("objective"):
            self.logger.warning("⚠️ Interpreted goal lacks objective. Incomplete interpretation.")
        
        self.memory.save("latest_goal", parsed_goal)
        self.log(f"✅ Goal parsed and stored: {json.dumps(parsed_goal, indent=2)}")

    def build_goal_prompt(self, prompt: str) -> str:
        return (
            "You are a financial planning assistant. Interpret the following user prompt into a structured financial goal.\n\n"
            f"Prompt:\n\"{prompt}\"\n\n"
            "Return a JSON object with the following fields:\n"
            "- objective (e.g., retire early, buy a house, reduce debt)\n"
            "- time_horizon (e.g., 2 years, 10 years)\n"
            "- risk_tolerance (low, medium, high)\n"
            "- constraints (e.g., income limit, family obligations)\n"
            "- tags (list of scenario tags)\n"
        )

    def extract_goal(self, response: str) -> dict:
        try:
            # Extract only the first JSON-like structure
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_block = response[json_start:json_end]
            return json.loads(json_block)
        except Exception as e:
            raise ValueError(f"Could not parse LLM response as JSON:\n{response}\nError: {e}")
