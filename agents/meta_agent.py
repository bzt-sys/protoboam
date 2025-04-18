# agents/meta_agent.py

import time
import logging
from core.agent_base import BaseAgent
from core.memory import Memory
from utils.resource_monitor import get_system_load
from config.settings import get_current_mode, set_mode

logger = logging.getLogger("MetaAgent")

class MetaAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.memory = Memory()
        self.check_interval = config.get("meta_interval", 300)  # seconds
        self.agent_performance = {}  # runtime stats for other agents

    async def run(self):
        logger.info("MetaAgent activated.")
        while True:
            await self.evaluate()
            await self.sleep_for(self.check_interval)

    async def evaluate(self):
        """
        Evaluate system performance and adjust agent behaviors accordingly.
        """
        current_mode = get_current_mode()
        sys_load = get_system_load()

        # Memory track for audit
        self.memory.remember(f"System load: {sys_load}, mode: {current_mode}")

        if sys_load["cpu_percent"] > 85 or sys_load["ram_percent"] > 80:
            logger.warning("High system load detected.")
            if current_mode != "lite":
                set_mode("lite")
                logger.info("Switched to Lite Mode due to high load.")
                self.memory.remember("Switched to Lite Mode")

        elif sys_load["cpu_percent"] < 40 and sys_load["ram_percent"] < 60:
            if current_mode == "lite":
                set_mode("balanced")
                logger.info("Upgraded to Balanced Mode.")
                self.memory.remember("Upgraded to Balanced Mode")

        # TODO: Monitor API usage and ROI to scale agents on/off
        # TODO: Track per-agent success rates and adjust frequency accordingly
        # TODO: Deactivate or sleep idle agents during off-peak times
  # runtime stats for other agents
