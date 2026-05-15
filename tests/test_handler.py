import json
from unittest.mock import patch

import pytest

from agent.agent import AgentResult
from agent.handler import handler


@pytest.fixture(autouse=True)
def _reset_agent_singleton() -> None:
    import agent.handler as h

    h._agent = None


def test_missing_message_returns_400() -> None:
    resp = handler({"body": "{}"}, None)
    assert resp["statusCode"] == 400
    assert "message" in resp["body"]


def test_invalid_json_returns_400() -> None:
    resp = handler({"body": "{not json"}, None)
    assert resp["statusCode"] == 400


def test_valid_request_calls_agent_and_returns_200() -> None:
    fake_result = AgentResult(
        output_text="hello",
        session_id="s_123",
        turns=1,
        tool_calls=[],
        input_tokens=5,
        output_tokens=2,
        duration_ms=400,
    )
    with patch("agent.handler._get_agent") as get_agent:
        get_agent.return_value.run.return_value = fake_result
        resp = handler({"body": json.dumps({"message": "hi"})}, None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["output"] == "hello"
    assert body["session_id"] == "s_123"
    assert body["usage"]["input_tokens"] == 5


def test_agent_failure_returns_500() -> None:
    with patch("agent.handler._get_agent") as get_agent:
        get_agent.return_value.run.side_effect = RuntimeError("boom")
        resp = handler({"body": json.dumps({"message": "hi"})}, None)
    assert resp["statusCode"] == 500
    body = json.loads(resp["body"])
    assert "Agent invocation failed" in body["error"]
