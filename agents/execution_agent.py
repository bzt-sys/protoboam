# agents/execution_agent.py

from core.agent_base import BaseAgent
from core.memory import Memory

class ExecutionAgent(BaseAgent):
    def __init__(self, live_mode: bool = False, dev_mode: bool = False):
        super().__init__("ExecutionAgent")
        self.memory = Memory()
        self.live_mode = live_mode
        self.dev_mode = dev_mode

    def execute_plan(self, steps: list):
        if not steps:
            self.logger.warning("⚠️ No strategy steps to execute.")
            return

        executed = []

        for step in steps:
            action = step.get("action", "unknown")

            if step.get("flagged", False):
                self.logger.warning(f"❌ Skipping flagged step: {action}")
                continue

            try:
                if self.live_mode:
                    self.send_order(action)
                    self.logger.info(f"🟢 Executed LIVE order: {action}")
                    executed.append({"action": action, "status": "sent"})
                else:
                    self.logger.info(f"[SIMULATION] Executing: {action}")
                    executed.append({"action": action, "status": "simulated"})
            except Exception as e:
                self.logger.error(f"❌ Error executing step {action}: {e}")

        self.memory.save("last_execution_result", {"executed": executed})
        self.logger.info(f"✅ Execution complete. {len(executed)} steps processed.")

    def send_order(self, action: str):
        """
        Stub: Replace with broker API call for live trading.
        """
        self.logger.info(f"📡 [LIVE TRADE] Order sent: {action}")
        return True  # Placeholder

    def run_cycle(self):
        self.logger.info("📥 Loading reviewed strategy steps...")

        reviewed = self.memory.load("latest_risk_report")
        if not reviewed:
            self.logger.warning("⚠️ No reviewed steps found. Aborting execution.")
            return

        steps = reviewed.get("reviewed_steps", [])
        if not steps:
            self.logger.info("✅ No unflagged steps to execute.")
            return

        self.logger.info(f"🚀 Executing {len(steps)} approved strategy steps...")
        self.execute_plan(steps)
