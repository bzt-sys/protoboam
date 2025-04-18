# core/agent_base.py

import logging
import time
from abc import ABC, abstractmethod
from config.settings import get_current_mode
from utils.resource_monitor import get_system_load

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent::{self.name}")
        self.last_run_time = 0

    def log(self, message):
        self.logger.info(f"[{self.name}] {message}")

    def should_run(self, min_interval=10):
        """Optional: prevent overactive agents."""
        now = time.time()
        if now - self.last_run_time >= min_interval:
            self.last_run_time = now
            return True
        return False

    def is_system_overloaded(self, cpu_thresh=85, ram_thresh=90):
        stats = get_system_load()
        overloaded = stats["cpu_percent"] > cpu_thresh or stats["ram_percent"] > ram_thresh
        if overloaded:
            self.logger.warning(f"System load high (CPU: {stats['cpu_percent']}%, RAM: {stats['ram_percent']}%) — skipping run.")
        return overloaded

    @abstractmethod
    def run_cycle(self):
        """Subclasses must implement this with their core logic."""
        pass

    def run(self):
        """Wrapper for safe execution and basic load-aware throttling."""
        try:
            if not self.should_run():
                self.logger.debug("Run skipped — interval not met.")
                return
            if self.is_system_overloaded():
                return
            self.logger.debug("Running cycle...")
            self.run_cycle()
        except Exception as e:
            self.logger.error(f"Exception in agent '{self.name}': {e}")
