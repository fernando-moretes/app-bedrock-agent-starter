"""Memory backends — in-memory for local dev, DynamoDB for prod."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from agent.config import Settings


class Memory(ABC):
    """Two-method abstraction so the agent doesn't care where history lives."""

    @abstractmethod
    def read(self, session_id: str) -> list[dict[str, Any]]:
        """Return the full message history for ``session_id`` (chronological)."""

    @abstractmethod
    def append(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        """Append messages to the session's history."""

    @classmethod
    def from_env(cls, settings: Settings | None = None) -> Memory:
        s = settings or Settings.from_env()
        if s.memory_backend == "dynamodb":
            if not s.sessions_table:
                raise RuntimeError("AGENT_MEMORY=dynamodb requires AGENT_SESSIONS_TABLE to be set.")
            return DynamoMemory(table_name=s.sessions_table, region=s.region)
        return InMemoryMemory()


class InMemoryMemory(Memory):
    """Process-local memory. Useful for the CLI and tests."""

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}

    def read(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._store.get(session_id, []))

    def append(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        self._store.setdefault(session_id, []).extend(messages)


class DynamoMemory(Memory):
    """Single-table DynamoDB backend: PK=session_id, SK=ts, with optional TTL."""

    def __init__(self, table_name: str, region: str, ttl_seconds: int = 60 * 60 * 24 * 7) -> None:
        import boto3  # imported lazily so local dev doesn't require AWS creds

        self._table = boto3.resource("dynamodb", region_name=region).Table(table_name)
        self._ttl_seconds = ttl_seconds

    def read(self, session_id: str) -> list[dict[str, Any]]:
        from boto3.dynamodb.conditions import Key

        resp = self._table.query(
            KeyConditionExpression=Key("session_id").eq(session_id),
            ScanIndexForward=True,
        )
        return [item["message"] for item in resp.get("Items", [])]

    def append(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        now_ms = int(time.time() * 1000)
        ttl = int(time.time()) + self._ttl_seconds
        with self._table.batch_writer() as bw:
            for i, m in enumerate(messages):
                bw.put_item(
                    Item={
                        "session_id": session_id,
                        "ts": now_ms + i,  # nudge ordering for messages in the same batch
                        "ttl": ttl,
                        "message": m,
                    }
                )
