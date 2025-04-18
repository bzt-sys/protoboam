# agents/base.py

import logging
import datetime
from abc import ABC, abstractmethod

# ⚠️ POTENTIAL HALLUCINATION: react_chain is a placeholder — needs actual ReAct loop logic or integration.
# ⚠️ POTENTIAL HALLUCINATION: Memory class not yet implemented — stub provided below.

class BaseAgent(ABC):
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)
        self.last_run = None

        # Optional features
        self.state = {}                 # General-purpose internal state
        self.memory = None             # ⚠️ TODO: Plug in memory module later
        self.react_chain = None        # ⚠️ TODO: Plug in ReAct loop logic later
        self.token_usage = 0           # Used for tracking LLM calls if any

        # Initialize memory/react if config says so
        self._init_optional_features()

    def _init_optional_features(self):
        if self.config.get("enable_memory"):
            # ⚠️ POTENTIAL HALLUCINATION: Memory() class is assumed, will need to implement or mock
            try:
                from core.memory import Memory
                self.memory = Memory(self.name)
                self.log("Memory module attached.")
            except ImportError:
                self.log("Memory module not found, skipping.", level=logging.WARNING)

        if self.config.get("enable_react"):
            # ⚠️ Placeholder — actual ReAct chain logic to
