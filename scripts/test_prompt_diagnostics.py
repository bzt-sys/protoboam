# scripts/test_prompt_diagnostics.py
# scripts/test_prompt_diagnostics.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import logging
from core.prompt_handler import handle_prompt
from core.memory import Memory
# scripts/_bootstrap.py


logging.basicConfig(level=logging.INFO)

def inspect_memory():
    print("\n🧠 MEMORY INSPECTION")
    print("-" * 40)

    memory_map = {
        "GoalInterpreter": ["latest_user_prompt"],
        "StrategyPlanner": ["latest_strategy"],
        "MarketAnalyst": ["evaluated_strategy"],
        "RiskManager": ["latest_risk_report"],
        "ExecutionAgent": ["last_execution_result"],
        "ComplianceAgent": ["compliance_audit_log", "tax_reserve_status"],  # Optional
    }

    for namespace, keys in memory_map.items():
        mem = Memory()
        print(f"\n📂 {namespace}")
        for key in keys:
            val = mem.recall(key, default="❌ Not set")
            print(f"  - {key}: {val if val else '❌ Empty'}")

def main():
    test_prompt = "I'd like to invest in crypto aggressively with high short-term returns."

    print("\n🔬 Running prompt diagnostic test...")
    summary = handle_prompt(prompt_text=test_prompt, verbose=True)

    print("\n📈 Simulation Summary Output")
    print("-" * 40)
    print(summary)

    inspect_memory()

if __name__ == "__main__":
    main()
