# agents/risk_manager_hybrid.py

from core.agent_base import BaseAgent
from core.memory import Memory
from core.corpora_loader import load_corpora_for_topic
import json

class HybridRiskManager(BaseAgent):
    def __init__(self, risk_threshold: float = 8.0, dev_mode: bool = False):
        super().__init__("HybridRiskManager")
        self.risk_threshold = risk_threshold
        self.memory = Memory()
        self.dev_mode = dev_mode

        try:
            self.risk_heuristics = load_corpora_for_topic("risk_management") or []
            self.logger.info(f"📚 Loaded {len(self.risk_heuristics)} risk heuristic patterns from corpora.")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load risk corpora: {e}")
            self.risk_heuristics = []

    def run_cycle(self, evaluated_strategy: dict):
        if not evaluated_strategy:
            self.logger.warning("⚠️ No evaluated strategy provided. Skipping hybrid risk assessment.")
            return

        self.log("🔍 Running hybrid risk assessment (scores + corpora)...")
        report = self.evaluate_risks(evaluated_strategy)

        if report:
            self.memory.save("latest_risk_report", report)
            self.log(f"✅ Hybrid risk report saved to memory.\n{json.dumps(report, indent=2)}")
        else:
            self.logger.warning("❌ Risk report generation failed.")

    def evaluate_risks(self, evaluated_strategy: dict) -> dict:
        reviewed_steps = []
        steps = evaluated_strategy.get("evaluated_steps", [])

        if not steps:
            self.logger.warning("⚠️ No evaluated steps found.")
            return {}

        for step in steps:
            risk_score = step.get("risk_score", 0)
            flagged = risk_score > self.risk_threshold
            comments = ["Risk exceeds threshold"] if flagged else ["Within safe range"]

            action = step.get("action", "")
            for heuristic in self.risk_heuristics:
                pattern = heuristic.get("pattern")
                if pattern and pattern in action:
                    comments.append("⚠️ Matches external high-risk pattern")
                    flagged = True
                    break

            reviewed_steps.append({
                **step,
                "flagged": flagged,
                "comment": " | ".join(comments)
            })

        total_risk = sum(s.get("risk_score", 0) for s in reviewed_steps) / max(1, len(reviewed_steps))
        overall_flag = total_risk > self.risk_threshold

        return {
            "reviewed_steps": reviewed_steps,
            "average_risk": round(total_risk, 2),
            "overall_flagged": overall_flag
        }
