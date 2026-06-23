import pytest
import os
import json

def test_explainability_trace_completeness():
    trace_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "traces", "agent_log.jsonl")
    if not os.path.exists(trace_path):
        pytest.skip("No trace file found to test explainability.")
        
    with open(trace_path, 'r') as f:
        lines = f.readlines()
        
    events = [json.loads(line) for line in lines if line.strip()]
    
    # We want to ensure that tool.call, tool.result, and cart.compiled are present
    event_types = set(e["event"] for e in events)
    
    assert "tool.call" in event_types, "Trace is missing tool calls."
    assert "tool.result" in event_types, "Trace is missing tool results."
    assert "cart.compiled" in event_types, "Trace is missing final decision/cart compilation."
    
    # User-facing explanation quality test
    cart_events = [e for e in events if e["event"] == "cart.compiled"]
    for ce in cart_events:
        for item in ce.get("cart", []):
            assert "price" in item, "User-visible cart is missing price explanation."
            assert "source" in item, "User-visible cart is missing source explanation."
