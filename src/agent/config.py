"""Environment-driven configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    region: str
    model_id: str
    max_tool_rounds: int
    max_tokens: int
    temperature: float
    system_prompt: str
    memory_backend: str
    sessions_table: str | None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            region=os.environ.get("AWS_REGION", "us-east-1"),
            model_id=os.environ.get(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
            ),
            max_tool_rounds=int(os.environ.get("AGENT_MAX_TOOL_ROUNDS", "8")),
            max_tokens=int(os.environ.get("AGENT_MAX_TOKENS", "2048")),
            temperature=float(os.environ.get("AGENT_TEMPERATURE", "0.2")),
            system_prompt=os.environ.get(
                "AGENT_SYSTEM_PROMPT",
                "You are a concise, helpful assistant. Use tools when they are clearly needed; "
                "answer directly otherwise. Always cite the tool you called in your final answer "
                "when it materially affected the result.",
            ),
            memory_backend=os.environ.get("AGENT_MEMORY", "inmemory"),
            sessions_table=os.environ.get("AGENT_SESSIONS_TABLE"),
        )
