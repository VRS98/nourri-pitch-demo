"""Deliverable 3 — tool & model stack tests.

Covers the in-process tools, the MCP-then-fallback behaviour of get_tools(),
and the deterministic mock LLM's sourcing logic. These run fast (no MCP
subprocess) by exercising the in-process layer and monkeypatching the MCP path.
"""
import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import agent.tools as tools_mod
from agent.tools import check_local_producer, check_supermarket_fallback, get_tools, LOCAL_TOOLS
from agent.llm import MockSourcingLLM


def test_in_process_tools_return_valid_json():
    local = json.loads(check_local_producer.invoke({"ingredient": "eggs"}))
    assert local["available"] is True
    assert local["source"] == "Sunrise Dairy Co-op"
    assert local["ingredient"] == "eggs"

    # harissa paste is not local -> supermarket fallback finds it
    not_local = json.loads(check_local_producer.invoke({"ingredient": "harissa paste"}))
    assert not_local["available"] is False
    market = json.loads(check_supermarket_fallback.invoke({"ingredient": "harissa paste"}))
    assert market["available"] is True
    assert market["source"] == "Carrefour"


def test_get_tools_falls_back_when_mcp_unavailable(monkeypatch):
    # Force the MCP loader to fail; get_tools must degrade to in-process tools.
    def boom():
        raise RuntimeError("simulated MCP outage")

    monkeypatch.setattr("agent.mcp_client.load_mcp_tools_sync", boom)
    result = get_tools()
    assert result is LOCAL_TOOLS


def test_mock_llm_local_first_then_fallback():
    llm = MockSourcingLLM()

    # Round 1: from the instruction, query every ingredient locally.
    instruction = HumanMessage(
        content="Find sourcing for these missing ingredients: eggs, harissa paste. "
                "Always check local producers first."
    )
    r1 = llm.invoke([instruction])
    assert [tc["name"] for tc in r1.tool_calls] == ["check_local_producer", "check_local_producer"]

    # Feed local results back: eggs available, harissa not.
    local_msgs = [
        ToolMessage(content=json.dumps({"ingredient": "eggs", "available": True}),
                    name="check_local_producer", tool_call_id="check_local_producer::eggs"),
        ToolMessage(content=json.dumps({"ingredient": "harissa paste", "available": False}),
                    name="check_local_producer", tool_call_id="check_local_producer::harissa paste"),
    ]
    # Round 2: only the unavailable item goes to the supermarket.
    r2 = llm.invoke([instruction, r1, *local_msgs])
    assert len(r2.tool_calls) == 1
    assert r2.tool_calls[0]["name"] == "check_supermarket_fallback"
    assert r2.tool_calls[0]["args"]["ingredient"] == "harissa paste"

    # Round 3: with fallback resolved, the agent stops (no tool calls).
    market_msg = ToolMessage(
        content=json.dumps({"ingredient": "harissa paste", "available": True}),
        name="check_supermarket_fallback", tool_call_id="check_supermarket_fallback::harissa paste",
    )
    r3 = llm.invoke([instruction, r1, *local_msgs, r2, market_msg])
    assert not r3.tool_calls
