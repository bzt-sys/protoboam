# agents/logistics_orchestrator.py

from core.agent_base import BaseAgent
from core.memory import Memory
from agents.risk_manager import RiskManager
from agents.compliance_agent import ComplianceAgent
from agents.execution_agent import ExecutionAgent

import threading


class LogisticsOrchestrator(BaseAgent):
    """
    Coordinates downstream validation agents — RiskManager, ComplianceAgent, and ExecutionAgent.
    Ensures that proposed strategies are realistic, compliant, and executable before continuing.
    """

    def __init__(self):
        super().__init__("LogisticsOrchestrator")
        self.memory = Memory()
        self.risk_manager = RiskManager()
        self.compliance_agent = ComplianceAgent()
        self.execution_agent = ExecutionAgent()

    def run_cycle(self):
        self.log("📦 Starting Logistics Orchestration Cycle...")

        # Load strategy output from ScenarioOrchestrator
        evaluated_strategy = self.memory.load("evaluated_strategy")
        if not evaluated_strategy:
            self.logger.warning("⚠️ No evaluated strategy found. Aborting logistics validation.")
            return None

        # === Initialize parallel results ===
        results = {
            "risk_report": None,
            "compliance_report": None,
            "execution_report": None
        }

        # === Agent runners ===
        def run_risk_analysis():
            self.risk_manager.run_cycle(evaluated_strategy)
            results["risk_report"] = self.memory.load("latest_risk_report") or {}

        def run_compliance_check():
            self.compliance_agent.run_cycle(evaluated_strategy)
            results["compliance_report"] = self.memory.load("latest_compliance_report") or {}

        def simulate_execution():
            self.execution_agent.run_cycle(evaluated_strategy, simulate_only=True)
            results["execution_report"] = self.memory.load("execution_simulation_result") or {}

        self.log("⚖️ Launching RiskManager, ComplianceAgent, and ExecutionAgent in parallel...")

        # === Launch all agents in parallel ===
        threads = [
            threading.Thread(target=run_risk_analysis),
            threading.Thread(target=run_compliance_check),
            threading.Thread(target=simulate_execution),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # === Save validation output ===
        self.memory.save("logistics_validation", results)
        self.log("✅ Logistics validation complete. Results saved.")

        # === Placeholder gatekeeper logic ===
        # Future logic: If risk is too high or non-compliance detected, block execution.
        # If all checks pass, LogisticsOrchestrator will trigger real trades.

        return results
