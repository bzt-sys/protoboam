# agents/scheduler.py

import time
from config.settings import get_current_mode
from utils.resource_monitor import get_system_load

MODE_INTERVALS = {
    "lite": 30,
    "balanced": 15,
    "enhanced": 5,
}

class Scheduler:
    def __init__(self):
        self.agent_last_run = {}

    def should_run(self, agent_name: str) -> bool:
        mode = get_current_mode()
        interval = MODE_INTERVALS.get(mode, 30)
        now = time.time()

        last_run = self.agent_last_run.get(agent_name, 0)
        if now - last_run >= interval:
            self.agent_last_run[agent_name] = now
            return True
        return False

    def system_is_overloaded(self) -> bool:
        load = get_system_load()
        return load["cpu_percent"] > 85 or load["ram_percent"] > 90
