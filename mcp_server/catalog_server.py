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

import asyncio
import time
from collections import deque

mcp = FastMCP("nourri-sourcing-catalog")

# Rate limiting configuration (60 requests per minute, 4 concurrent sessions max)
request_times = deque()
MAX_REQUESTS = 60
TIME_WINDOW = 60.0
concurrent_sessions = asyncio.Semaphore(4)

async def check_rate_limit():
    async with concurrent_sessions:
        now = time.time()
        while request_times and now - request_times[0] > TIME_WINDOW:
            request_times.popleft()
            
        if len(request_times) >= MAX_REQUESTS:
            raise RuntimeError("Rate limit exceeded: 60 requests per minute.")
            
        request_times.append(now)

@mcp.tool
async def check_local_producer(ingredient: str) -> str:
    """Check if an ingredient is available from local producers.

    Returns a JSON string with availability, price, and source.
    """
    await check_rate_limit()
    # Apply a max 10s timeout logic via asyncio.wait_for
    result = await asyncio.wait_for(asyncio.to_thread(lookup_local, ingredient), timeout=10.0)
    return json.dumps(result)


@mcp.tool
async def check_supermarket_fallback(ingredient: str) -> str:
    """Check if an ingredient is available from fallback supermarkets.

    Call only when check_local_producer returns available=false.
    Returns a JSON string with availability, price, and source.
    """
    await check_rate_limit()
    result = await asyncio.wait_for(asyncio.to_thread(lookup_supermarket, ingredient), timeout=10.0)
    return json.dumps(result)


if __name__ == "__main__":
    mcp.run(show_banner=False)  # stdio transport by default
