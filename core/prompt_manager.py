# core/prompt_manager.py

import logging
from core.memory import Memory

logger = logging.getLogger("PromptManager")

class PromptManager:
    def __init__(self):
        # Maps scenario classifications to paths (can later include metadata or corpora embeddings)
        self.known_scenarios = {
            "retirement": "data/scenarios/retirement_planning.json",
            "crypto": "data/scenarios/crypto_aggressive.json",
            "real_estate": "data/scenarios/real_estate_growth.json",
            "default": "data/scenarios/default_balanced.json"
        }

    def classify_prompt(self, prompt: str) -> str:
        """
        Very simple keyword-based classification (can be upgraded later to use embeddings or LLM-based parsing).
        """
        prompt_lower = prompt.lower()

        if any(term in prompt_lower for term in ["retire", "401k", "pension", "social security"]):
            return "retirement"
        elif any(term in prompt_lower for term in ["bitcoin", "crypto", "nft", "blockchain"]):
            return "crypto"
        elif any(term in prompt_lower for term in ["property", "real estate", "mortgage", "rental"]):
            return "real_estate"
        else:
            return "default"

    def process_prompt(self, prompt: str) -> dict:
        """
        Classify the prompt, store metadata to memory, and return scenario path and normalized prompt.
        """
        classification = self.classify_prompt(prompt)
        scenario_path = self.known_scenarios.get(classification)

        normalized_prompt = prompt.strip()

        logger.info(f"🔎 Prompt classified as '{classification}'")

        # Persist to shared memory for use by GoalInterpreter, StrategyPlanner, etc.
        memory = Memory()
        memory.save("classified_scenario", classification)
        memory.save("normalized_prompt", normalized_prompt)

        return {
            "classification": classification,
            "scenario_path": scenario_path,
            "normalized_prompt": normalized_prompt
        }
