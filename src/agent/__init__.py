"""Production-shaped starter for AI agents on Amazon Bedrock."""

__version__ = "0.1.0"

from agent.agent import Agent
from agent.memory import DynamoMemory, InMemoryMemory, Memory
from agent.tools import dispatch, registered_tools, tool, tool_specs

__all__ = [
    "Agent",
    "DynamoMemory",
    "InMemoryMemory",
    "Memory",
    "dispatch",
    "registered_tools",
    "tool",
    "tool_specs",
]
