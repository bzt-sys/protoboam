# main.py

from core.prompt_handler import handle_prompt
import sys

import argparse
import asyncio
import logging
from core.orchestrator import AgentOrchestrator
from core.simulation_manager import SimulationManager
from core.prompt_manager import PromptManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

async def run_orchestrator():
    orchestrator = AgentOrchestrator()
    logging.info("🚀 Autonomous Agent System Started")

    while True:
        await orchestrator.run_sequence()
        await asyncio.sleep(1)

def run_simulation(cycles: int = 1, scenario_path: str = None):
    sim = SimulationManager()
    if scenario_path:
        try:
            sim.load_scenario(scenario_path)
        except Exception as e:
            logging.error(f"❌ Failed to load scenario: {e}")
            return

    if cycles == 1:
        sim.simulate_once()
    else:
        sim.simulate_batch(cycles)


def parse_args():
    parser = argparse.ArgumentParser(description="Autonomous Agent System CLI")
    parser.add_argument(
        "--simulate",
        type=int,
        nargs="?",
        const=1,
        help="Run the simulation manager (optionally specify number of cycles)"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        help="Path to a scenario JSON file to preload for simulation"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["lite", "balanced", "enhanced", "auto"],
        help="Manually set the system mode"
    )
    parser.add_argument(
    "--prompt",
    type=str,
    help="User prompt to trigger automated reasoning, planning, simulation, and trade"
    )
    parser.add_argument(
    "--verbose",
    action="store_true",
    help="Display detailed memory contents and diagnostics"
    )
    parser.add_argument(
    "--diagnostics",
    action="store_true",
    help="Display system status, memory keys, schedule activity, and runtime mode"
    )

    return parser.parse_args()

def print_diagnostics():
    from config.settings import get_current_mode
    from core.memory import Memory
    from agents.scheduler import Scheduler

    print("\n🔍 SYSTEM DIAGNOSTICS\n" + "-" * 40)

    print(f"🧠 Current Mode: {get_current_mode()}")
    #print(f"🧮 CPU Cores: {psutil.cpu_count(logical=False)}")
    #print(f"💾 Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")

    mem = Memory()
    keys = mem.list_keys()
    print(f"\n🗃️ Memory Keys: {', '.join(keys) if keys else 'None'}")

    scheduler = Scheduler()
    state = scheduler.get_schedule_state()
    print("\n📅 Agent Schedule State:")
    for k, v in state.items():
        print(f"  - {k}: {v}")

    try:
        current_scenario = Memory().recall("current_scenario", default=None)
        if current_scenario:
            print(f"\n📦 Loaded Scenario: {current_scenario.get('name', 'Unnamed')}")
    except Exception:
        pass

    print("\n✅ System looks good. No fatal errors detected.\n")

if __name__ == "__main__":
    args = parse_args()

    try:
        if args.prompt:
            logging.info("🧠 Prompt mode activated...")
            summary = handle_prompt(args.prompt, scenario_path=args.scenario, verbose=args.verbose)
            print("\n📈 TRADE RATIONALE:\n" + summary)
            sys.exit(0)

        elif args.simulate is not None:
            run_simulation(cycles=args.simulate, scenario_path=args.scenario)

        else:
            asyncio.run(run_orchestrator())

    except KeyboardInterrupt:
        logging.info("🛑 Shutdown requested by user.")
