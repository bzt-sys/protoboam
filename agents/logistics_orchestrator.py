from core.agent_base import BaseAgent
from core.memory import Memory
from agents.risk_manager import RiskManager
from agents.compliance_agent import ComplianceAgent
from agents.execution_agent import ExecutionAgent

import threading
import json


class LogisticsOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__("LogisticsOrchestrator")
        self.memory = Memory()
        self.risk_manager = RiskManager()
        self.compliance_agent = ComplianceAgent()
        self.execution_agent = ExecutionAgent()

    def run_cycle(self):
        self.log("📦 Starting Logistics Orchestration Cycle...")

        evaluated_strategy = self.memory.load("evaluated_strategy")
        if not evaluated_strategy:
            self.logger.warning("⚠️ No evaluated strategy found. Aborting logistics validation.")
            return

        risk_report = {}
        compliance_report = {}
        execution_report = {}

        def assess_risks():
            self.risk_manager.run_cycle(evaluated_strategy)
            nonlocal risk_report
            risk_report = self.memory.load("latest_risk_report") or {}

        def check_compliance():
            self.compliance_agent.run_cycle(evaluated_strategy)
            nonlocal compliance_report
            compliance_report = self.memory.load("latest_compliance_report") or {}

        def simulate_execution():
            self.execution_agent.run_cycle(evaluated_strategy, simulate_only=True)
            nonlocal execution_report
            execution_report = self.memory.load("execution_simulation_result") or {}

        self.log("⚖️ Launching RiskManager, ComplianceAgent, and ExecutionAgent in parallel...")

        t1 = threading.Thread(target=assess_risks)
        t2 = threading.Thread(target=check_compliance)
        t3 = threading.Thread(target=simulate_execution)

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        self.memory.save("logistics_validation", {
            "risk_report": risk_report,
            "compliance_report": compliance_report,
            "execution_report": execution_report
        })

        self.log("✅ Logistics validation cycle complete.")
