# core/prompt_handler.py

import logging
from core.simulation_manager import SimulationManager
from core.memory import Memory
from core.prompt_manager import PromptManager

logger = logging.getLogger("PromptHandler")
sim_manager = SimulationManager()
prompt_manager = PromptManager()

def handle_prompt(prompt_text: str, scenario_path: str = None, verbose: bool = False):
    """
    Handle a user-submitted prompt:
    - Use PromptManager to classify and resolve scenario path
    - Save prompt to memory for GoalInterpreter
    - Load scenario
    - Run one simulation cycle
    - Return summarized output
    """
    logger.info("📨 Received user prompt.")

    # Classify and normalize prompt if scenario not provided
    if not scenario_path:
        prompt_info = prompt_manager.process_prompt(prompt_text)
        scenario_path = prompt_info.get("scenario_path")
    else:
        logger.info(f"📦 Using explicitly provided scenario path: {scenario_path}")
        Memory().save("normalized_prompt", prompt_text.strip())

    # Save prompt to GoalInterpreter memory
    Memory().save("latest_user_prompt", prompt_text.strip())

    # Load scenario (if any)
    if scenario_path:
        sim_manager.load_scenario(scenario_path)

    # Run the full simulation once
    sim_manager.simulate_once(diagnostic=verbose)

    return format_summary(verbose=verbose)

def format_summary(verbose=False):
    """
    Gather outputs from shared memory (e.g. strategy steps, risk analysis, trade plan)
    and return a user-facing summary.
    """
    summary = []

    strategy = Memory().recall("latest_strategy", default={})
    risk = Memory().recall("latest_risk_report", default={})
    execution = Memory().recall("last_execution_result", default={})

    if strategy:
        summary.append("📌 Proposed Strategy:\n" + strategy.get("summary", "No summary available."))

    if risk:
        flagged = [s for s in risk.get("reviewed_steps", []) if s.get("flagged")]
        approved = [s for s in risk.get("reviewed_steps", []) if not s.get("flagged")]
        summary.append(f"✅ Approved Steps: {len(approved)} | ❌ Flagged Steps: {len(flagged)}")

    if execution:
        summary.append("📊 Executed Steps:")
        for step in execution.get("executed", []):
            summary.append(f" - {step.get('action')} [{step.get('status')}]")

    if verbose:
        summary.append("\n🛠 Full memory snapshot:")
        summary.append(str(strategy))
        summary.append(str(risk))
        summary.append(str(execution))

    return "\n".join(summary) if summary else "⚠️ No output generated."
