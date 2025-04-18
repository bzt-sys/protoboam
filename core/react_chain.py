# core/react_chain.py

import logging
from core.llm_manager import LLMManager

logger = logging.getLogger("ReActChain")

class ReActChain:
    def __init__(self, agent_name: str, mode: str = "default"):
        self.agent_name = agent_name
        self.llm = LLMManager(mode=mode)

        # ⚠️ TODO: Support multiple reasoning modes, e.g., simple chain-of-thought or tool-augmented reasoning
        self.max_steps = 5
        self.stop_phrases = ["FINAL ANSWER", "END", "DONE"]

    def run(self, prompt: str, model: str = "local") -> str:
        """
        Performs a basic ReAct loop: think → act → observe → refine → repeat.
        """
        reasoning_history = []
        current_input = prompt

        for step in range(self.max_steps):
            full_prompt = self.build_prompt(reasoning_history, current_input)
            output = self.llm.route_model(full_prompt, model=model)

            reasoning_history.append(output)

            if any(stop in output.upper() for stop in self.stop_phrases):
                break

            # ⚠️ TODO: Tool calls / act execution could be parsed from output here
            current_input = output  # Feed forward the output

        return "\n".join(reasoning_history)

    def build_prompt(self, history: list, current_input: str) -> str:
        """
        Generates a chain-of-thought style prompt from prior steps.
        """
        # ⚠️ TODO: Refactor with prompt template system
        preamble = f"You are a financial reasoning agent named {self.agent_name}.\n"
        history_text = "\n".join(history)
        return f"{preamble}{history_text}\nThought: {current_input}\nAction:"
