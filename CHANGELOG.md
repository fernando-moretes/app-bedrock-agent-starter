# Changelog

All notable changes to this project will be documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-15

### Added
- Agent loop using the Bedrock Converse API with tool-use orchestration.
- Tool registry with `@tool` decorator; three sample tools (`calculator`, `get_time`, `web_search` stub).
- Pluggable memory: `InMemoryMemory` and `DynamoMemory`.
- Structured JSON logging and CloudWatch EMF metric helpers.
- `agent chat` CLI for local iteration.
- AWS Lambda handler.
- Terraform IaC skeleton (Lambda + API Gateway + DynamoDB + IAM).
- Pytest suite for tools, agent loop and memory; eval harness over a golden JSONL set.
- MkDocs Material documentation site with per-topic pages and ADRs.
- Next.js landing page deployable to Vercel.
- GitHub Actions CI (lint, type-check, tests) and docs deploy.

[Unreleased]: https://github.com/fernandofatech/bedrock-agent-starter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fernandofatech/bedrock-agent-starter/releases/tag/v0.1.0
