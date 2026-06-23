"""Model factory for the sourcing agent.

`get_llm()` returns the real Gemini model when GEMINI_API_KEY is set, otherwise
a deterministic mock that reproduces the sourcing behaviour with no network and
no API key. This keeps tests and the demo runnable in under 10 minutes while
still allowing a real model when a key is present.

The model name is declared here (MODEL_NAME) so it appears in code, per
Deliverable 3.
"""
import json
import os
import re

from agent.trace import log_event
from agent.util import content_text

MODEL_NAME = "gemini-2.0-flash"

LOCAL_TOOL = "check_local_producer"
SUPERMARKET_TOOL = "check_supermarket_fallback"


def get_llm():
    """Return a bind_tools-capable model: real Gemini if keyed, else the mock."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key and api_key.lower() != "dummy":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            log_event("llm.init", mode="gemini", model=MODEL_NAME)
            return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0, api_key=api_key)
        except Exception as exc:  # noqa: BLE001 - degrade to mock on any init error
            log_event("llm.init", mode="mock", model=MODEL_NAME,
                      reason=f"gemini_init_failed: {exc}")
            return MockSourcingLLM()
    log_event("llm.init", mode="mock", model=MODEL_NAME, reason="no_api_key")
    return MockSourcingLLM()


def _tool_call(name: str, ingredient: str) -> dict:
    # Deterministic, unique id (tool name differs between rounds; ingredients
    # are de-duplicated, so this never collides).
    return {"name": name, "args": {"ingredient": ingredient},
            "id": f"{name}::{ingredient}", "type": "tool_call"}


def _safe_json(text) -> dict:
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except (ValueError, TypeError):
        return {}


def _extract_ingredients(messages) -> list:
    """Pull the ingredient list out of the agent's first instruction message."""
    text = ""
    for m in messages:
        if m.__class__.__name__ == "HumanMessage":
            text = m.content
    match = re.search(r"missing ingredients:\s*(.+?)\.", text, re.IGNORECASE)
    if not match:
        return []
    seen, out = set(), []
    for raw in match.group(1).split(","):
        ing = raw.strip()
        if ing and ing.lower() not in seen:
            seen.add(ing.lower())
            out.append(ing)
    return out


class MockSourcingLLM:
    """Deterministic stand-in for the sourcing agent's LLM.

    Mirrors the SKILL.md procedure purely from message history (so it is fully
    reproducible): query local producers for every ingredient, then the
    supermarket fallback for whatever was unavailable locally, then stop.
    """

    name = f"{MODEL_NAME}-mock"

    def bind_tools(self, tools=None, **kwargs):
        # Tool names are fixed for this domain mock; nothing to store.
        return self

    def invoke(self, messages, **kwargs):
        from langchain_core.messages import AIMessage

        id_to_ingredient = {}
        local_queried, supermarket_queried = set(), set()
        for m in messages:
            for tc in getattr(m, "tool_calls", None) or []:
                ingredient = (tc.get("args") or {}).get("ingredient")
                id_to_ingredient[tc.get("id")] = ingredient
                if tc.get("name") == LOCAL_TOOL:
                    local_queried.add(ingredient)
                elif tc.get("name") == SUPERMARKET_TOOL:
                    supermarket_queried.add(ingredient)

        local_available = {}
        for m in messages:
            if m.__class__.__name__ != "ToolMessage":
                continue
            if getattr(m, "name", "") != LOCAL_TOOL:
                continue
            ingredient = id_to_ingredient.get(getattr(m, "tool_call_id", None))
            local_available[ingredient] = bool(_safe_json(content_text(m.content)).get("available"))

        # Round 1 — nothing queried yet: check every ingredient locally.
        if not local_queried:
            ingredients = _extract_ingredients(messages)
            if not ingredients:
                return AIMessage(content="No ingredients to source.")
            return AIMessage(content="",
                             tool_calls=[_tool_call(LOCAL_TOOL, i) for i in ingredients])

        # Round 2 — fall back to supermarket for locally-unavailable items.
        pending = [ing for ing, ok in local_available.items()
                   if not ok and ing not in supermarket_queried]
        if pending:
            return AIMessage(content="",
                             tool_calls=[_tool_call(SUPERMARKET_TOOL, i) for i in pending])

        # Done — no more tool calls; the graph moves on to compile the cart.
        return AIMessage(content="Sourcing complete. Cart compiled from local "
                                 "producers with supermarket fallback where needed.")
