"""Nourri Sourcing Catalog — FastMCP server.

Exposes the local-producer and supermarket catalog as MCP tools. The agent
connects to this server over stdio (see mcp_server/mcp_config.json) and loads
these tools at runtime.

Run standalone:
    python -m mcp_server.catalog_server
"""
import json

from fastmcp import FastMCP

from agent.catalog import lookup_local, lookup_supermarket

mcp = FastMCP("nourri-sourcing-catalog")


@mcp.tool
def check_local_producer(ingredient: str) -> str:
    """Check if an ingredient is available from local producers.

    Returns a JSON string with availability, price, and source.
    """
    return json.dumps(lookup_local(ingredient))


@mcp.tool
def check_supermarket_fallback(ingredient: str) -> str:
    """Check if an ingredient is available from fallback supermarkets.

    Call only when check_local_producer returns available=false.
    Returns a JSON string with availability, price, and source.
    """
    return json.dumps(lookup_supermarket(ingredient))


if __name__ == "__main__":
    mcp.run(show_banner=False)  # stdio transport by default
