"""AWS Lambda handler for HTTP-fronted deployment.

Wired to API Gateway HTTP API (payload v2). Expects JSON:

```json
{"message": "...", "session_id": "optional"}
```
"""

from __future__ import annotations

import json
from typing import Any

from agent.agent import Agent
from agent.config import Settings
from agent.memory import Memory

_agent: Agent | None = None


def _get_agent() -> Agent:
    """Lazy-init agent so the Lambda cold start cost happens once per container."""
    global _agent
    if _agent is None:
        settings = Settings.from_env()
        _agent = Agent(settings=settings, memory=Memory.from_env(settings))
    return _agent


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """API Gateway HTTP API (payload v2) Lambda handler."""
    try:
        body_raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64

            body_raw = base64.b64decode(body_raw).decode("utf-8")
        body = json.loads(body_raw)
    except json.JSONDecodeError:
        return _response(400, {"error": "Body must be JSON."})

    message = body.get("message")
    if not message or not isinstance(message, str):
        return _response(400, {"error": "Field 'message' (string) is required."})
    session_id = body.get("session_id")

    try:
        result = _get_agent().run(user_message=message, session_id=session_id)
    except Exception as e:  # noqa: BLE001 — surface as 500 with safe body
        return _response(500, {"error": "Agent invocation failed.", "detail": str(e)})

    return _response(
        200,
        {
            "output": result.output_text,
            "session_id": result.session_id,
            "turns": result.turns,
            "tool_calls": result.tool_calls,
            "usage": {
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "duration_ms": result.duration_ms,
            },
        },
    )


def _response(status: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }
