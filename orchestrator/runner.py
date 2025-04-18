# orchestrator/runner.py

import asyncio
import importlib
import logging
from typing import List, Dict
import traceback

from config.mode_config import get_mode_settings  # Will define this shortly

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentRunner")

# ⚠️ REVIEW: This assumes agents follow a common structure.
# All agents must inherit from `BaseAgent` and implement `async run()`

class AgentRunner:
    def __init__(self, mode: str):
        self.mode = mode
        self.agent_configs = get_mode_settings(mode)  # Dynamic agent frequency/priority
        self.agents = []

    async def load_agents(self):
        """
        Dynamically import agents based on config.
        Each config entry should contain:
        - module: import path
        - class: class name
        - schedule: seconds between runs
        """
        for agent_cfg in self.agent_configs:
            try:
                mod = importlib.import_module(agent_cfg["module"])
                cls = getattr(mod, agent_cfg["class"])
                agent = cls(agent_cfg.get("config", {}))
                self.agents.append((agent, agent_cfg["schedule"]))
                logger.info(f"Loaded agent: {agent_cfg['class']} with interval {agent_cfg['schedule']}s")
            except Exception as e:
                logger.error(f"Failed to load agent {agent_cfg}: {e}")
                traceback.print_exc()

    async def run_loop(self):
        """
        Schedule all agents according to their loop interval.
        Each runs in its own task unless 'lite' mode forces staggering.
        """
        async def run_agent(agent, interval):
            while True:
                try:
                    await agent.run()
                except Exception as e:
                    logger.error(f"Agent {agent.__class__.__name__} failed: {e}")
                await asyncio.sleep(interval)

        tasks = []
        for agent, interval in self.agents:
            tasks.append(asyncio.create_task(run_agent(agent, interval)))

        await asyncio.gather(*tasks)

    async def start(self):
        await self.load_agents()
        await self.run_loop()
