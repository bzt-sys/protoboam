# run_agent.py

import argparse
from core.orchestrator import AgentOrchestrator

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, help="Run mode: lite | balanced | enhanced")
    args = parser.parse_args()

    orchestrator = AgentOrchestrator(mode=args.mode or "auto")
    
    if orchestrator.mode == "auto":
        orchestrator.mode = orchestrator.auto_detect_mode()

    orchestrator.run()
