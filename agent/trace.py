"""Structured JSON-lines tracing.

Every notable event (tool source, tool call, guardrail trigger, decision) is
appended to /traces/agent_log.jsonl as one JSON object per line, and echoed to
stdout. This is the audit log read in Deliverables 6 (guardrails) and 7
(explainability).
"""
import json
import os
from datetime import datetime, timezone

TRACES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "traces")
LOG_PATH = os.path.join(TRACES_DIR, "agent_log.jsonl")


def log_event(event: str, **fields) -> dict:
    """Append a structured event to the trace log and echo it to stdout."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    line = json.dumps(record, default=str)
    try:
        os.makedirs(TRACES_DIR, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass  # never let logging crash the agent
    print(f"[trace] {line}")
    return record
