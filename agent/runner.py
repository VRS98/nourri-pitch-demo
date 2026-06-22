"""UI-facing helpers to run the agent and surface its trajectory.

No Streamlit imports here — app.py owns graph caching and passes the compiled
graph in. These helpers run the graph to the HITL gate, resume/cancel it, and
turn the message history into display-friendly steps.
"""
import json
import uuid

from agent.util import content_text


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def run_to_approval(graph, missing_ingredients: list) -> dict:
    """Run the agent from input up to the HITL gate (or an error guardrail)."""
    thread_id = f"ui-{uuid.uuid4().hex[:8]}"
    state = {
        "messages": [],
        "missing_ingredients": missing_ingredients,
        "cart": [],
        "total_price": 0.0,
        "status": "",
        "error_message": "",
        "order_id": "",
    }
    out = graph.invoke(state, config=_config(thread_id))
    return _snapshot(out, thread_id)


def resume_order(graph, thread_id: str, approved: bool) -> dict:
    """Resume past the HITL gate: place the order, or cancel it."""
    cfg = _config(thread_id)
    if not approved:
        graph.update_state(cfg, {"status": "cancelled"})
    out = graph.invoke(None, config=cfg)
    return _snapshot(out, thread_id)


def _snapshot(out: dict, thread_id: str) -> dict:
    return {
        "thread_id": thread_id,
        "status": out.get("status"),
        "cart": out.get("cart", []),
        "total_price": out.get("total_price", 0.0),
        "error_message": out.get("error_message", ""),
        "order_id": out.get("order_id", ""),
        "trajectory": extract_trajectory(out.get("messages", [])),
    }


def extract_trajectory(messages: list) -> list:
    """Turn the message history into ordered display steps (one per tool result)."""
    steps = []
    for m in messages:
        if m.__class__.__name__ != "ToolMessage":
            continue
        data = {}
        try:
            data = json.loads(content_text(m.content))
        except (ValueError, TypeError):
            pass
        steps.append({
            "tool": getattr(m, "name", ""),
            "ingredient": data.get("ingredient"),
            "available": data.get("available"),
            "source": data.get("source"),
            "price": data.get("price"),
            "channel": "local" if getattr(m, "name", "") == "check_local_producer" else "supermarket",
        })
    return steps
