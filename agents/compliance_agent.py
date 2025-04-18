# agents/compliance_agent.py

import logging
from core.agent_base import BaseAgent
from core.memory import Memory
from datetime import datetime
from utils.audit_logger import log_audit_event  # Stub or placeholder
from config.settings import get_jurisdiction  # Stub for user config

logger = logging.getLogger("ComplianceAgent")

class ComplianceAgent(BaseAgent):
    def __init__(self, config, dev_mode: bool = False):
        super().__init__(config)
        self.memory = Memory()
        self.tax_reserve_ratio = config.get("tax_reserve_ratio", 0.25)
        self.jurisdiction = get_jurisdiction() or "unknown"
        self.high_risk_flags = ["Cayman Islands", "Panama", "Liberia", "unknown"]
        self.dev_mode = dev_mode  # Enables detailed logging for testing

    def run_cycle(self):
        """
        Sync version of compliance checks for integration in simulation pipeline.
        """
        logger.info("🧾 Running compliance cycle...")

        # Log additional details in dev mode
        if self.dev_mode:
            logger.debug(f"Compliance settings: tax reserve ratio = {self.tax_reserve_ratio}, jurisdiction = {self.jurisdiction}")
        
        self.check_and_reserve_taxes(sync=True)

    def record_income(self, amount, source="unknown"):
        """
        Record an income event and store it in memory.
        """
        event = {
            "amount": amount,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        events = self.memory.recall("income_events", default=[])
        events.append(event)
        self.memory.save("income_events", events)

        # Log for development
        if self.dev_mode:
            logger.debug(f"Recorded income event: {event}")

    def check_and_reserve_taxes(self, sync=False):
        """
        Compliance step for tax reserve + audit logging.
        Can be used in async or sync mode.
        """
        new_income_events = self.memory.recall("income_events", default=[])
        if not new_income_events:
            logger.debug("No new income events.")
            return

        reserved_total = 0
        audit_log = []

        for event in new_income_events:
            amount = event.get("amount", 0)
            source = event.get("source", "unknown")
            timestamp = event.get("timestamp", datetime.utcnow().isoformat())
            reserve = round(amount * self.tax_reserve_ratio, 2)
            reserved_total += reserve

            audit_entry = {
                "type": "income",
                "amount": amount,
                "reserved": reserve,
                "source": source,
                "timestamp": timestamp,
                "jurisdiction": self.jurisdiction,
            }

            # Log the reserve operation for development mode
            if self.dev_mode:
                logger.debug(f"Reserving {reserve} for income from {source} with total {reserved_total}")

            audit_log.append(audit_entry)
            self.memory.remember(f"Reserved ${reserve} for tax from ${amount} income ({source})")
            log_audit_event(audit_entry)  # Stub

        # Expose audit + reserve for agents or CLI
        self.memory.save("latest_tax_reserve", {
            "total_reserved": reserved_total,
            "entries": audit_log,
            "jurisdiction": self.jurisdiction,
            "flagged_high_risk": self.jurisdiction in self.high_risk_flags,
        })

        # Logging the final results
        logger.info(f"💰 Reserved ${reserved_total} for tax compliance.")
        if self.dev_mode:
            logger.debug(f"High-risk jurisdiction flag: {self.jurisdiction in self.high_risk_flags}")

        self.memory.clear("income_events")
