# 0002 - Tool registry over framework magic

- Status: **accepted**
- Date: 2026-05-15

## Context

Agent frameworks can speed up demos, but they often hide message state, retries, tool schemas, and error handling. This project is a portfolio-grade starter where the architecture should be easy to read.

## Decision

Use a small local tool registry built around a decorator and normal Python functions.

## Consequences

- Tool behavior is straightforward to unit-test.
- The Bedrock tool schema is visible in one place.
- Replacing the registry with LangGraph, Strands Agents, or another framework remains possible because the current boundary is small.
