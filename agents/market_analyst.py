# agents/market_analyst.py

from core.agent_base import BaseAgent
from core.memory import Memory
from llm.local_llm import call_local_llm
import random
import json


def mock_market_data_lookup(asset: str) -> dict:
    return {
        "price": round(random.uniform(50, 200), 2),
        "volatility": round(random.uniform(0.01, 0.1), 3),
        "trend": random.choice(["up", "down", "sideways"]),
    }


class MarketAnalyst(BaseAgent):
    def __init__(self, dev_mode: bool = False):
        super().__init__("MarketAnalyst")
        self.memory = Memory()
        self.dev_mode = dev_mode
        self.scenario_context = self.load_scenario_corpora()

    def load_scenario_corpora(self) -> str:
        """
        Attempt to retrieve scenario corpora from shared memory.
        Returns string content if found, else empty string.
        """
        shared = Memory()
        corpora = shared.load("active_corpora")
        if corpora:
            self.logger.info("📚 Scenario corpora loaded for market analysis.")
            return corpora.get("text", "")
        else:
            self.logger.info("ℹ️ No scenario corpora found. Proceeding without extra context.")
            return ""

    def run_cycle(self, strategy: dict):
        scenario = self.memory.load("active_scenario")

        if not strategy:
            self.logger.warning("⚠️ No strategy provided. Skipping market analysis.")
            return

        self.log("📊 Evaluating market feasibility of strategy with scenario context...")
        evaluated = self.evaluate_strategy(strategy, scenario=scenario, use_mock=self.dev_mode)

        if evaluated:
            self.memory.save("evaluated_strategy", evaluated)
            self.log("✅ Strategy evaluation complete and saved to memory.")
        else:
            self.logger.warning("❌ Strategy evaluation failed.")


    def evaluate_strategy(self, strategy: dict, scenario: dict = None, use_mock: bool = False) -> dict:
        if use_mock:
            return self.mock_evaluation(strategy)

        try:
            prompt = self.construct_prompt(strategy, scenario)
            response = call_local_llm(prompt)
            evaluated = json.loads(response)

            if not evaluated.get("evaluated_steps"):
                raise ValueError("LLM response missing 'evaluated_steps'.")

            return evaluated

        except Exception as e:
            self.logger.error(f"⚠️ LLM evaluation failed: {e}. Falling back to mock evaluator.")
            return self.mock_evaluation(strategy)


    def construct_prompt(self, strategy: dict, scenario: dict = None) -> str:
        scenario_block = json.dumps(scenario or {}, indent=2)
        return (
            "You are a market analyst AI. Evaluate each action in the proposed financial strategy below.\n\n"
            f"Scenario Context:\n{scenario_block}\n\n"
            f"Strategy:\n{json.dumps(strategy, indent=4)}\n\n"
            "For each step, add realistic market data (price, volatility, trend), and assign a risk score from 0–100.\n"
            "Respond ONLY in JSON format like:\n"
            "{ 'evaluated_steps': [ { 'action': '...', 'justification': '...', 'expected_roi': '...', "
            "'market_data': { 'price': 0.0, 'volatility': 0.0, 'trend': 'up' }, 'risk_score': 0 }, ... ] }"
        )


    def mock_evaluation(self, strategy: dict) -> dict:
        steps = strategy.get("steps", []) if strategy else []
        evaluation = []

        for step in steps:
            asset = self.extract_asset_from_action(step.get("action", "unknown"))
            market_data = mock_market_data_lookup(asset)
            risk = self.estimate_risk(market_data)

            evaluation.append({
                "action": step.get("action", "unknown"),
                "justification": step.get("justification", "N/A"),
                "expected_roi": step.get("expected_roi", "0%"),
                "market_data": market_data,
                "risk_score": risk
                })

            return {"evaluated_steps": evaluation}

    def extract_asset_from_action(self, action: str) -> str:
        action = action.lower()
        if "options" in action:
            return "SPY"
        elif "crypto" in action:
            return "BTC"
        elif "savings" in action:
            return "USDT"
        else:
            return "AAPL"

    def estimate_risk(self, market_data: dict) -> float:
        base = market_data["volatility"] * 100
        trend_penalty = 5 if market_data["trend"] == "down" else 0
        return round(base + trend_penalty, 2)
