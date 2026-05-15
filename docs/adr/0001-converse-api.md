# 0001 - Converse API as the core

- Status: **accepted**
- Date: 2026-05-15

## Context

Amazon Bedrock has model-specific APIs and a cross-model Converse API. A starter template should make model swaps possible without rewriting the agent loop.

## Decision

Use the Bedrock Converse API as the core runtime API.

## Consequences

- Tool use is represented through a stable request/response shape.
- The starter can move across Claude, Nova, Llama, and Mistral models supported by Converse.
- Model-specific features can still be added behind configuration later.
