# agents/logging_agent.py

import logging
from core.agent_base import BaseAgent
from core.memory import Memory
from datetime import datetime

logger = logging.getLogger("LoggingAgent")

class LoggingAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.memory = Memory()
        self.log_buffer = []

    async def run(self):
        logger.info("📘 LoggingAgent started.")
        while True:
            await self.flush_logs()
            await self.sleep_for(self.config.get("interval", 300))  # Every 5 min

    def record_event(self, event_type: str, message: str, source: str = "system"):
        """
        Store an event for eventual flushing to persistent memory or external logging.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "message": message,
            "source": source
        }
        self.log_buffer.append(event)
        logger.debug(f"Buffered log event: {event_type} | {message}")

    async def flush_logs(self):
        if not self.log_buffer:
            logger.debug("No logs to flush.")
            return

        # Merge with existing persistent logs
        historical_logs = self.memory.recall("logs", default=[])
        historical_logs.extend(self.log_buffer)
        self.memory.save("logs", historical_logs)
        logger.info(f"📤 Flushed {len(self.log_buffer)} log events to memory.")
        self.log_buffer.clear()

    def fetch_logs(self, limit=100):
        """
        Retrieve recent log events.
        """
        all_logs = self.memory.recall("logs", default=[])
        return all_logs[-limit:]
