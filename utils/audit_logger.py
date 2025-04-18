# utils/audit_logger.py

import json
import os
from datetime import datetime
import logging

logger = logging.getLogger("AuditLogger")

AUDIT_LOG_DIR = "logs/audit"
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, "compliance_audit.log")

# Ensure directory exists
os.makedirs(AUDIT_LOG_DIR, exist_ok=True)

def log_audit_event(event: dict):
    """
    Appends an immutable audit log record to the file in JSON Lines format.

    Each record contains:
    - timestamp (ISO)
    - type (e.g. "income")
    - amount, reserved, source, jurisdiction (etc)
    """
    event = dict(event)  # Make a shallow copy
    event["log_timestamp"] = datetime.utcnow().isoformat()

    try:
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
        logger.info(f"Audit log recorded: {event['type']} ${event.get('amount', '?')}")
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")
