# core/orchestrator.py

import asyncio
import logging
import psutil

from agents.scheduler import Scheduler
from agents.goal_interpreter import GoalInterpreter
from agents.strategy_planner import StrategyPlanner
from agents.market_analyst import MarketAnalyst
from agents.risk_manager import RiskManager
from agents.execution_agent import ExecutionAgent
from agents.compliance_agent import ComplianceAgent
from agents.meta_agent import MetaAgent

from config.settings import load_config

from core.memory import Memory

logger = logging.getLogger("Orchestrator")

class AgentOrchestrator:
    def __init__(self, mode: str = "auto"):
        config = load_config()
        self.mode = self.auto_detect_mode() if mode == "auto" else mode
        self.scheduler = Scheduler()
        self.memory = Memory("Orchestrator", persist=True)

        # Initialize agents
        self.agents = {
            "meta": MetaAgent({"meta_interval": 300}),
            "goal": GoalInterpreter(),
            "strategy": StrategyPlanner(),
            "market": MarketAnalyst(),
            "risk": RiskManager(),
            "execution": ExecutionAgent(live_mode=False),
            "compliance": ComplianceAgent({"tax_reserve_ratio": 0.25}),
        }

    def auto_detect_mode(self) -> str:
        ram = psutil.virtual_memory().total / (1024 ** 3)
        cores = psutil.cpu_count(logical=False)
        if ram >= 48 and cores >= 12:
            return "enhanced"
        elif ram >= 24:
            return "balanced"
        return "lite"

    async def run_sequence(self):
        logger.info("Agent loop beginning...")

        if self.scheduler.system_is_overloaded():
            logger.warning("🚨 High system load detected — deferring agent activity.")
            await asyncio.sleep(10)
            return

        agent_order = ["meta", "goal", "strategy", "market", "risk", "execution", "compliance"]

        for name in agent_order:
            agent = self.agents.get(name)
            if not agent or not self.scheduler.should_run(name):
                continue

            try:
                logger.info(f"🌀 Running {name} agent...")
                await agent.run()
            except Exception as e:
                logger.error(f"❌ Error running {name} agent: {e}")

        self.scheduler.log_schedule_state()

    def run(self):
        asyncio.run(self.run_sequence())
