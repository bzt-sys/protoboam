# tests/test_local_llm.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.local_llm import call_local_llm

def test_local_llm_basic():
    prompt = "What is the capital of France?"
    response = call_local_llm(prompt)
    print("\n[LLM Response]:", response)

if __name__ == "__main__":
    test_local_llm_basic()
