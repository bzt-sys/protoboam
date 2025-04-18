# 🤖 AutoFinance Agents

**Autonomous Multi-Agent Financial Planning System with Local LLM Support**

AutoFinance Agents is a modular, prompt-driven AI system designed to simulate and execute financial strategies through coordinated multi-agent interaction. It supports local LLM inference and is designed to be corpora-trainable and resource-aware.

---

## Features

- 🧠 Modular Agents: Goal Interpreter, Strategy Planner, Market Analyst, Risk Manager, Execution Agent, and Compliance Agent.
- 🗃️ Scenario-Based Reasoning: Each simulation draws from contextual corpora tailored to specific financial prompts.
- 🔍 Diagnostics: Built-in testing harness to verify simulation cycles and agent outputs.
- 🏠 Local LLM Inference: Runs fully offline via quantized models (e.g. [Nous-Hermes-2](https://huggingface.co/TheBloke/Nous-Hermes-2-Mistral-7B-DPO-GGUF)).
- 💡 Designed for fine-tuning: Each agent is structured for independent training on external corpora.

---

## Project Structure

![System Architecture](docs/system_architecture_diagram.png)
