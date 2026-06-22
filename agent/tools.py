"""Sourcing tools for the agent.

Two layers live here:

1. In-process LangChain tools (`check_local_producer`, `check_supermarket_fallback`)
   that wrap the shared catalog. These are the reliable *fallback* used when the
   MCP server is unavailable.
2. `get_tools()` — the entry point the graph calls. It tries to load the tools
   from the FastMCP catalog server first (the "real" path) and gracefully falls
   back to the in-process tools, logging which path was taken to /traces/.

Tools return JSON strings so the local and MCP paths produce identical,
parseable tool output downstream.
"""
import json
import time

from langchain_core.tools import tool

from agent.catalog import lookup_local, lookup_supermarket
from agent.trace import log_event


@tool
def check_local_producer(ingredient: str) -> str:
    """Check if an ingredient is available from local producers.

    Args:
        ingredient: The name of the ingredient (e.g., 'oat milk').
    Returns:
        JSON string with availability, price, and source.
    """
    time.sleep(0.3)  # simulate network latency
    return json.dumps(lookup_local(ingredient))


@tool
def check_supermarket_fallback(ingredient: str) -> str:
    """Check if an ingredient is available from fallback supermarkets (Monoprix, Carrefour).

    Call this ONLY if check_local_producer returns available=false.

    Args:
        ingredient: The name of the ingredient.
    Returns:
        JSON string with availability, price, and source.
    """
    time.sleep(0.3)  # simulate network latency
    return json.dumps(lookup_supermarket(ingredient))


# The in-process tools, used directly as the fallback path.
LOCAL_TOOLS = [check_local_producer, check_supermarket_fallback]


def get_tools():
    """Return the sourcing tools, preferring the MCP server, falling back in-process.

    The graph calls this once at build time. If the FastMCP catalog server can be
    reached and its tools loaded, those are used (the "real" MCP path). Any
    failure (missing deps, server down, transport error) degrades gracefully to
    the in-process tools so the agent always runs.
    """
    try:
        from agent.mcp_client import load_mcp_tools_sync

        tools = load_mcp_tools_sync()
        if tools:
            log_event("tools.source", source="mcp", count=len(tools),
                      names=[t.name for t in tools])
            return tools
        raise RuntimeError("MCP returned no tools")
    except Exception as exc:  # noqa: BLE001 - any failure should fall back
        log_event("tools.source", source="in_process_fallback",
                  reason=str(exc), count=len(LOCAL_TOOLS))
        return LOCAL_TOOLS
