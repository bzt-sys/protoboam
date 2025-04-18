# core/memory.py

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

MEMORY_DIR = "state/memory"
LOGS_DIR = "state/logs"

class Memory:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        self.session_log: Dict[str, Any] = {}  # In-memory session log for diagnostics

    def _file_path(self, key: str) -> str:
        return os.path.join(MEMORY_DIR, f"{key}.json")

    def _log_path(self, agent: str, timestamp: str) -> str:
        return os.path.join(LOGS_DIR, f"{timestamp}_{agent}.json")

    def save(self, key: str, data: dict):
        """
        Persist a memory item under a key (e.g. 'latest_strategy')
        """
        with open(self._file_path(key), "w") as f:
            json.dump(data, f, indent=2)
        self.session_log[key] = data  # Also track in current run log

    def load(self, key: str) -> Optional[dict]:
        """
        Load a memory item by key
        """
        try:
            with open(self._file_path(key), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def log_agent_action(self, agent_name: str, data: dict):
        """
        Record an agent's contribution to the shared log (in-memory and disk)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log[agent_name] = data  # for diagnostics view

        path = self._log_path(agent_name, timestamp)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def checkpoint(self, data: dict = None):
        """
        Save a full snapshot of current memory or agent session log
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(MEMORY_DIR, f"checkpoint_{timestamp}.json")
        if data is None:
            data = self.session_log
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Return session diagnostics (all memory written during current run)
        """
        return self.session_log

    def reset(self):
        """
        Clear all memory and logs (for clean testing)
        """
        for folder in [MEMORY_DIR, LOGS_DIR]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
        self.session_log.clear()
