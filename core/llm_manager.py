# core/llm_manager.py

import os
import logging
import time
import json
import requests
from typing import Literal

logger = logging.getLogger("LLMManager")

# ⚠️ REVIEW: Supports 'local' via Ollama and 'openai' via API key. Extendable later.
LLMSource = Literal["local", "openai"]

class LLMManager:
    def __init__(self, mode: str = "default"):
        self.mode = mode
        self.budget_dollars = float(os.getenv("API_BUDGET", "3.00"))
        self.token_price_per_1k = {
            "openai": 0.01,  # ⚠️ REVIEW: Set actual cost per model used
            "local": 0.0
        }
        self.token_usage = 0  # Estimated tokens used
        self.dollar_spent = 0.0

    def check_budget(self, model: LLMSource):
        if self.dollar_spent >= self.budget_dollars:
            logger.warning(f"Budget cap reached: ${self.dollar_spent:.2f} / ${self.budget_dollars}")
            return False
        return True

    def estimate_tokens(self, prompt: str) -> int:
        # ⚠️ Naive estimate: 1 token ~ 4 characters
        return max(1, len(prompt) // 4)

    def update_usage(self, model: LLMSource, tokens_used: int):
        self.token_usage += tokens_used
        cost = (tokens_used / 1000) * self.token_price_per_1k.get(model, 0.01)
        self.dollar_spent += cost

    def route_model(self, prompt: str, model: LLMSource = "local", temperature=0.7):
        if not self.check_budget(model):
            return "[LLMManager]: API usage rejected — budget cap hit."

        tokens = self.estimate_tokens(prompt)
        self.update_usage(model, tokens)

        if model == "local":
            return self._query_local(prompt)
        elif model == "openai":
            return self._query_openai(prompt, temperature)
        else:
            return f"[LLMManager]: Unknown model source: {model}"

    def _query_local(self, prompt: str) -> str:
        try:
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "mistral",  # ⚠️ TODO: Configurable
                "prompt": prompt,
                "stream": False
            })
            result = response.json()
            return result.get("response", "[LLMManager]: No response.")
        except Exception as e:
            logger.error(f"Local LLM failed: {e}")
            return "[LLMManager]: Local model error."

    def _query_openai(self, prompt: str, temperature=0.7) -> str:
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model="gpt-4",  # ⚠️ TODO: Configurable per agent
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return "[LLMManager]: OpenAI error."
