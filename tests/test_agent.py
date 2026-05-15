"""Agent loop tests with a fake Bedrock client.

The fake matches the shape of the boto3 ``bedrock-runtime`` ``converse`` response
just enough for the loop to exercise both terminal and tool-use paths.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from agent.agent import Agent
from agent.config import Settings
from agent.memory import InMemoryMemory


def _settings() -> Settings:
    return Settings(
        region="us-east-1",
        model_id="fake-model",
        max_tool_rounds=4,
        max_tokens=256,
        temperature=0.0,
        system_prompt="be helpful",
        memory_backend="inmemory",
        sessions_table=None,
    )


class _FakeBedrock:
    """Returns scripted responses in order."""

    def __init__(self, scripted: list[dict[str, Any]]) -> None:
        self._responses: Iterator[dict[str, Any]] = iter(scripted)
        self.calls: list[dict[str, Any]] = []

    def converse(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return next(self._responses)


def test_simple_end_turn_returns_text() -> None:
    fake = _FakeBedrock(
        [
            {
                "stopReason": "end_turn",
                "usage": {"inputTokens": 10, "outputTokens": 3},
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [{"text": "Hello!"}],
                    }
                },
            }
        ]
    )
    agent = Agent(settings=_settings(), memory=InMemoryMemory(), bedrock_client=fake)
    result = agent.run("hi")
    assert result.output_text == "Hello!"
    assert result.turns == 1
    assert result.tool_calls == []
    assert result.input_tokens == 10
    assert result.output_tokens == 3
    assert result.session_id.startswith("s_")


def test_one_tool_use_round_completes() -> None:
    fake = _FakeBedrock(
        [
            {
                "stopReason": "tool_use",
                "usage": {"inputTokens": 12, "outputTokens": 6},
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "toolUse": {
                                    "toolUseId": "t1",
                                    "name": "calculator",
                                    "input": {"expression": "2 + 2"},
                                }
                            }
                        ],
                    }
                },
            },
            {
                "stopReason": "end_turn",
                "usage": {"inputTokens": 20, "outputTokens": 4},
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [{"text": "The answer is 4."}],
                    }
                },
            },
        ]
    )
    agent = Agent(settings=_settings(), memory=InMemoryMemory(), bedrock_client=fake)
    result = agent.run("what is 2+2?")
    assert result.output_text == "The answer is 4."
    assert result.tool_calls == ["calculator"]
    assert result.input_tokens == 32
    assert result.output_tokens == 10


def test_max_rounds_exceeded_returns_graceful_message() -> None:
    # Force an infinite tool-use loop and check we surface a clear message.
    tool_response = {
        "stopReason": "tool_use",
        "usage": {"inputTokens": 1, "outputTokens": 1},
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "toolUse": {
                            "toolUseId": "t",
                            "name": "get_time",
                            "input": {"tz": "UTC"},
                        }
                    }
                ],
            }
        },
    }
    fake = _FakeBedrock([tool_response] * 10)
    settings = Settings(**{**_settings().__dict__, "max_tool_rounds": 3})
    agent = Agent(settings=settings, memory=InMemoryMemory(), bedrock_client=fake)
    result = agent.run("loop")
    assert "max tool-call rounds" in result.output_text


def test_failing_tool_does_not_crash_loop() -> None:
    fake = _FakeBedrock(
        [
            {
                "stopReason": "tool_use",
                "usage": {"inputTokens": 1, "outputTokens": 1},
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "toolUse": {
                                    "toolUseId": "t1",
                                    "name": "calculator",
                                    "input": {"expression": "__import__('os').system('ls')"},
                                }
                            }
                        ],
                    }
                },
            },
            {
                "stopReason": "end_turn",
                "usage": {"inputTokens": 1, "outputTokens": 1},
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [{"text": "Sorry, I cannot."}],
                    }
                },
            },
        ]
    )
    agent = Agent(settings=_settings(), memory=InMemoryMemory(), bedrock_client=fake)
    result = agent.run("be evil")
    assert "Sorry" in result.output_text


def test_session_id_is_reused_when_passed() -> None:
    fake = _FakeBedrock(
        [
            {
                "stopReason": "end_turn",
                "usage": {"inputTokens": 1, "outputTokens": 1},
                "output": {
                    "message": {
                        "role": "assistant",
                        "content": [{"text": "ok"}],
                    }
                },
            }
        ]
    )
    agent = Agent(settings=_settings(), memory=InMemoryMemory(), bedrock_client=fake)
    result = agent.run("hi", session_id="s_abc")
    assert result.session_id == "s_abc"


@pytest.mark.parametrize("missing", ["output", "stopReason"])
def test_malformed_response_raises_predictably(missing: str) -> None:
    response = {
        "stopReason": "end_turn",
        "usage": {"inputTokens": 1, "outputTokens": 1},
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": "x"}],
            }
        },
    }
    response.pop(missing)
    fake = _FakeBedrock([response])
    agent = Agent(settings=_settings(), memory=InMemoryMemory(), bedrock_client=fake)
    with pytest.raises((KeyError, TypeError)):
        agent.run("hi")
