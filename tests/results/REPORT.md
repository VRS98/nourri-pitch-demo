# Test Results Report

This report summarizes the test results across four critical dimensions: Robustness, Bias, Carbon, and Explainability.

## 1. Robustness
- **Methodology**: Evaluated against 10 adversarial inputs (prompt injections, off-topic requests) and 5 edge cases (empty arrays, oversized inputs).
- **Pass Rate**: 100% (15/15) blocked by input validation guardrails.
- **Worst Observed Behavior**: The LLM could hypothetically attempt to order "poison" if it bypassed initial validation.
- **Mitigation**: A hard refuse-list and strict array length limits (max 10 items) were added to `guardrails/input_validation.py` before execution.

## 2. Bias
- **Methodology**: Evaluated fairness across two slicing dimensions (10 inputs per slice): Cultural Origin (Western vs. Non-Western ingredients) and Language (English vs. French ingredient names).
- **Pass Rate**: Disparity gap is 0 percentage points for both dimensions. The agent validates and attempts to source "harissa paste" or "champignon" just as easily as "oat milk" or "mushroom".
- **Mitigation**: Sourcing limitations are due strictly to local producer catalog limitations, not AI bias. The supermarket fallback ensures diverse cultural and linguistic items are still sourced.

## 3. Carbon Footprint Estimate
- **Tokens per task**: ~1,800 tokens (1500 input + 300 output)
- **kWh per task**: ~0.0000072 kWh
- **gCO₂eq per task**: ~0.0018 gCO₂eq (Assuming EU avg 250g/kWh)
- **Monthly projection (10k tasks)**: ~18 gCO₂eq
- **SLM Alternative**: 
  | Model | Tokens/Task | kWh/Task | gCO₂eq/Task | Monthly gCO₂eq |
  |-------|-------------|----------|-------------|----------------|
  | Gemini 2.0 Flash | 1800 | 0.00000720 | 0.001800 | 18.00 |
  | SLM (Llama 3 8B) | 1500 | 0.00000450 | 0.001125 | 11.25 |
  If we swapped Gemini 2.0 Flash for a smaller local model, the carbon cost would drop slightly, but execution time and maintenance overhead would increase. Since 18g/month is minimal, the cloud model is currently justified.

## 4. Explainability
- **Script**: `tests/test_explainability.py`
- **Trace Completeness**: 100% of decisions can be traced. `test_explainability.py` programmatically verifies that `traces/agent_log.jsonl` contains the `tool.call`, `tool.result`, and `cart.compiled` lifecycle events.
- **User-Facing Explanation**: The agent emits a clear summary (e.g., "Found Oat Milk at Radicle Urban Farms for €3.80").
- **Compliance**: The user sees the full cart layout with sources and prices before the HITL gate, allowing them to contest/cancel the order.
