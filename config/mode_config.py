# config/mode_config.py

def get_mode_settings(mode: str):
    """
    Returns agent schedule config based on resource mode.
    """
    # ⚠️ These intervals are arbitrary and need tuning from performance feedback
    base_agents = [
        {"module": "agents.goal_interpreter", "class": "GoalInterpreter", "schedule": 120},
        {"module": "agents.strategy_planner", "class": "StrategyPlanner", "schedule": 180},
        {"module": "agents.market_analyst", "class": "MarketAnalyst", "schedule": 60},
        {"module": "agents.execution_agent", "class": "ExecutionAgent", "schedule": 10},
        {"module": "agents.risk_manager", "class": "RiskManager", "schedule": 30},
        {"module": "agents.compliance_agent", "class": "ComplianceAgent", "schedule": 300},
        {"module": "agents.watchdog", "class": "WatchdogAgent", "schedule": 20},
        {"module": "agents.meta_agent", "class": "MetaAgent", "schedule": 240},
    ]

    if mode == "lite":
        for a in base_agents:
            a["schedule"] *= 2  # Slow things down in low-resource mode
    elif mode == "enhanced":
        for a in base_agents:
            a["schedule"] = max(a["schedule"] // 2, 5)  # Speed up on better hardware

    return base_agents
