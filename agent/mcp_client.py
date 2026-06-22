"""Load sourcing tools from the FastMCP catalog server.

Uses langchain-mcp-adapters to spawn the server over stdio and load its tools,
then wraps each async MCP tool in a synchronous shim so the existing sync graph
(and tests/Streamlit) can call them without an async refactor.

Any failure here raises; agent/tools.get_tools() catches it and falls back to
the in-process tools.
"""
import asyncio
import json
import os
import sys
import threading

from langchain_core.tools import StructuredTool

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "mcp_server", "mcp_config.json"
)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def _run_coro_sync(coro):
    """Run a coroutine to completion on a dedicated thread + event loop.

    Using a separate thread avoids "event loop already running" errors when
    called from inside environments that already hold a loop (e.g. Streamlit).
    """
    box = {}

    def runner():
        loop = asyncio.new_event_loop()
        try:
            box["value"] = loop.run_until_complete(coro)
        except BaseException as exc:  # noqa: BLE001 - propagate after join
            box["error"] = exc
        finally:
            loop.close()

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box["value"]


def _build_connections() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        cfg = json.load(fh)

    connections = {}
    for name, server in cfg["mcpServers"].items():
        command = server["command"]
        # The config declares "python" for readability; use the active
        # interpreter so we run inside this venv.
        if command == "python":
            command = sys.executable
        connections[name] = {
            "command": command,
            "args": server["args"],
            "transport": server.get("transport", "stdio"),
            "cwd": PROJECT_ROOT,
            "env": {**os.environ, "PYTHONPATH": PROJECT_ROOT},
        }
    return connections


def _to_sync_tool(async_tool) -> StructuredTool:
    """Wrap an async MCP tool so it can be invoked synchronously."""

    def _call(**kwargs):
        return _run_coro_sync(async_tool.ainvoke(kwargs))

    return StructuredTool.from_function(
        func=_call,
        name=async_tool.name,
        description=async_tool.description,
        args_schema=async_tool.args_schema,
    )


def load_mcp_tools_sync():
    """Load MCP tools from the catalog server and return sync-callable tools."""
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient(_build_connections())
    async_tools = _run_coro_sync(client.get_tools())
    return [_to_sync_tool(t) for t in async_tools]
