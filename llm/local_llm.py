# llm/local_llm.py

import logging
from typing import Optional

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None  # Will raise if llama-cpp-python isn't available

logger = logging.getLogger("LLM")

# === CONFIGURATION ===
USE_LLAMA_CPP = True  # Switch to False later when integrating Mistral backend
GGUF_MODEL_PATH = "models/Nous-Hermes-13B.Q5_K_M.gguf"
MAX_TOKENS = 512
CONTEXT_WINDOW = 2048
N_GPU_LAYERS = -1  # Offload all layers to GPU (RTX 4080 will handle this well)
N_THREADS = 8      # Adjust if needed for CPU fallback

# === GLOBAL STATE ===
#llama_model: Optional[Llama] = None

if USE_LLAMA_CPP and Llama is not None:
    try:
        llama_model = Llama(
            model_path=GGUF_MODEL_PATH,
            n_ctx=CONTEXT_WINDOW,
            n_threads=N_THREADS,
            n_gpu_layers=N_GPU_LAYERS,
            use_mlock=True,
            verbose=False
        )
        logger.info("Nous-Hermes-2 model loaded successfully with llama-cpp.")
    except Exception as e:
        logger.error(f"Failed to initialize GGUF model: {e}")
        llama_model = None
        USE_LLAMA_CPP = False  # Disable to prevent usage downstream


def call_local_llm(prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """
    Routes prompt through local LLM (Nous-Hermes-2) or prepares for future Mistral-based backend.
    """
    try:
        if USE_LLAMA_CPP and llama_model:
            response = llama_model(prompt, max_tokens=max_tokens, stop=["\n\n"], echo=False)
            return response["choices"][0]["text"].strip()

        # === Placeholder for Mistral (future) ===
        logger.warning("Mistral backend not yet implemented. Returning placeholder.")
        return "[Mistral integration pending]"

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "[Error generating response]"
