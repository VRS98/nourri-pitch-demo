# Nourri Agentic MVP

This repository contains the MVP for Nourri's **Missing Ingredient Ordering Agent**. 

This agent uses LangGraph, Gemini, and Streamlit to orchestrate a workflow that:
1. Takes a list of missing ingredients as input.
2. Sourced items from local producers (or falls back to supermarkets).
3. Evaluates total price and applies a Human-in-the-Loop (HITL) guardrail before placing the order.

## Project Structure
- `app.py`: Streamlit frontend for the demo.
- `agent/`: LangGraph orchestrator and tool definitions.
- `guardrails/`: Input validation and HITL checks.
- `skills/`: The procedural SKILL.md specifying agent logic.
- `tests/`: Scripts for testing robustness, bias, carbon, and explainability.
- `traces/`: Directory where agent logs and trajectories are saved.

## Setup and Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and add your Gemini API key:
   ```bash
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY
   ```

3. **Run the Streamlit Demo**:
   ```bash
   streamlit run app.py
   ```

4. **Run the Tests**:
   ```bash
   python -m pytest tests/
   ```
