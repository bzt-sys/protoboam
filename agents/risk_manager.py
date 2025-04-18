# agents/risk_manager.py

from core.agent_base import BaseAgent
from core.memory import Memory
from llm.local_llm import call_local_llm
import json


class RiskManager(BaseAgent):
    def __init__(self, risk_threshold: float = 8.0, dev_mode: bool = False):
        super().__init__("RiskManager")
        self.risk_threshold = risk_threshold
        self.memory = Memory()
        self.dev_mode = dev_mode
        self.scenario_context = self.load_scenario_corpora()

    def load_scenario_corpora(self) -> str:
        shared = Memory()
        corpora = shared.load("active_corpora")
        if corpora:
            self.logger.info("📚 Scenario corpora loaded for risk evaluation.")
            return corpora.get("text", "")
        else:
            self.logger.info("ℹ️ No scenario corpora found. Proceeding without extra context.")
            return ""

    def run_cycle(self):
        """
        Orchestrator-compatible cycle entry point: pulls evaluated strategy from memory.
        """
        evaluated = self.memory.load("evaluated_strategy")
        self.run_with_data(evaluated)

    def run_with_data(self, evaluated_strategy: dict):
        """
        Performs risk assessment using either LLM or rule-based logic.
        """
        if not evaluated_strategy:
            self.logger.warning("⚠️ No evaluated strategy provided. Skipping risk assessment.")
            return

        self.log("🔍 Running risk assessment...")
        risk_report = self.evaluate_risks(evaluated_strategy, use_llm=not self.dev_mode)

        if risk_report:
            self.memory.save("latest_risk_report", risk_report)
            self.log(f"✅ Risk report generated and saved.\n{json.dumps(risk_report, indent=2)}")
        else:
            self.logger.warning("❌ Risk report generation failed.")

    def evaluate_risks(self, evaluated_strategy: dict, use_llm: bool = True) -> dict:
        """
        Evaluate risk of each step and flag items exceeding the threshold.
        Use local LLM if enabled, else fallback to rule-based risk evaluator.
        """
        if not evaluated_strategy.get("evaluated_steps"):
            self.logger.warning("⚠️ No evaluated steps found in strategy.")
            return {}

        if use_llm:
            try:
                prompt = self.construct_prompt(evaluated_strategy)
                response = call_local_llm(prompt)

                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                if start_idx == -1 or end_idx == -1:
                    raise ValueError("No JSON object found in LLM response.")

                parsed = json.loads(response[start_idx:end_idx])
                if not parsed.get("reviewed_steps"):
                    raise ValueError("LLM response missing 'reviewed_steps'.")

                return parsed

            except Exception as e:
                self.logger.error(f"⚠️ LLM-based risk analysis failed: {e}. Falling back to rule-based.")

        # Fallback: Use rule-based risk evaluation
        return self.rule_based_risk_review(evaluated_strategy)

    def rule_based_risk_review(self, evaluated_strategy: dict) -> dict:
        reviewed_steps = []
        steps = evaluated_strategy.get("evaluated_steps", [])

        for step in steps:
            risk_score = step.get("risk_score", 0)
            is_risky = risk_score > self.risk_threshold

            reviewed_steps.append({
                **step,
                "flagged": is_risky,
                "comment": "Risk exceeds threshold" if is_risky else "Within safe range"
            })

        avg_risk = sum(s.get("risk_score", 0) for s in reviewed_steps) / max(1, len(reviewed_steps))
        overall_flag = avg_risk > self.risk_threshold

        return {
            "reviewed_steps": reviewed_steps,
            "average_risk": round(avg_risk, 2),
            "overall_flagged": overall_flag
        }

    def construct_prompt(self, evaluated_strategy: dict) -> str:
        prompt_parts = []

        prompt_parts.append(
            "You are a risk management agent. Analyze the strategy steps below based on market data and risk scores.\n"
            "For each step, determine if the risk is acceptable. Flag steps that exceed a threshold (default 8.0)."
        )

        if self.scenario_context:
            prompt_parts.append(
                "\n\nCURRENT SCENARIO CONTEXT:\n" + self.scenario_context
            )

        prompt_parts.append(
            "\n\nEVALUATED STRATEGY:\n" + json.dumps(evaluated_strategy, indent=4)
        )

        prompt_parts.append(
            "\n\nRespond ONLY in JSON format with this schema:\n"
            "{ \"reviewed_steps\": [ { \"action\": \"...\", \"risk_score\": 0.0, \"flagged\": true, \"comment\": \"...\" }, ... ], \"average_risk\": 0.0, \"overall_flagged\": true }"
        )

        return "\n\n---\n\n".join(prompt_parts)
