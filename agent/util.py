"""Small shared helpers."""


def content_text(content) -> str:
    """Normalise a message's content to a plain string.

    In-process tools return a JSON string; MCP tools (via langchain-mcp-adapters)
    return a list of content blocks like ``[{"type": "text", "text": "..."}]``.
    This flattens both to the underlying text so downstream code can json.loads it.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content)
