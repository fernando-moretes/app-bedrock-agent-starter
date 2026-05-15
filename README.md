<div align="center">

# bedrock-agent-starter

**A production-shaped starter template for AI agents on Amazon Bedrock. Tools, memory, observability, Terraform IaC, evals. Fork it, set `AWS_PROFILE`, ship a working agent in 30 minutes.**

[![CI](https://github.com/fernandofatech/bedrock-agent-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/fernandofatech/bedrock-agent-starter/actions/workflows/ci.yml)
[![Docs](https://github.com/fernandofatech/bedrock-agent-starter/actions/workflows/docs.yml/badge.svg)](https://fernandofatech.github.io/bedrock-agent-starter/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Bedrock](https://img.shields.io/badge/Amazon-Bedrock-FF9900.svg)](https://aws.amazon.com/bedrock/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-fa6673.svg)](https://www.conventionalcommits.org)

[Docs](https://fernandofatech.github.io/bedrock-agent-starter/) ·
[Landing](https://bedrock-agent-starter.vercel.app) ·
[Quickstart](#quickstart) ·
[Adding a tool](#adding-a-tool) ·
[Deploying](#deploying)

</div>

---

## Why this exists

Bedrock makes it easy to *call a model*. It does not make it easy to ship a real agent: tool registry, multi-turn memory, structured observability, eval harness, IaC, error handling, prompt caching, model fallbacks — all yours to wire up.

This starter wires them up. Opinionated where it should be, replaceable where it shouldn't.

## What you get

- **Agent loop** using the [Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) — stable across Claude / Nova / Llama / Mistral, with first-class tool use.
- **Tool registry** with three working tools (`calculator`, `get_time`, `web_search` stub) and a four-line pattern to add your own.
- **Pluggable memory** — in-memory for local dev, DynamoDB for prod.
- **Structured observability** — JSON logs with `session_id`, `turn`, `model_id`; CloudWatch EMF metrics for tokens, latency, tool calls.
- **Local CLI** (`agent chat`) to iterate without leaving the terminal.
- **AWS Lambda handler** + **API Gateway** wiring via Terraform.
- **Eval harness** with a golden JSONL set and a `pytest`-driven runner.
- **CI** (ruff + mypy + pytest), **docs** (MkDocs Material), **dependency-free static landing**.

## Quickstart

```bash
git clone git@github.com:fernandofatech/bedrock-agent-starter.git
cd bedrock-agent-starter
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Set AWS creds and the model id (Claude Sonnet by default).
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Chat with the agent locally.
agent chat
```

Type a question. Hit Enter. The agent reasons, calls tools, replies.

```
> what time is it in Tokyo, and what is (123 * 456) - 789?

[tool] get_time(tz="Asia/Tokyo") → "2026-05-15T22:41:09+09:00"
[tool] calculator(expression="(123 * 456) - 789") → 55299

It is 22:41 in Tokyo, and (123 × 456) − 789 = 55 299.
```

## Adding a tool

A tool is one decorator + one function:

```python
# src/agent/tools.py
from agent.tools import tool

@tool(description="Translate text between languages using a deterministic table.")
def translate(text: str, source_lang: str, target_lang: str) -> str:
    ...
    return translated
```

The agent picks it up automatically. Pydantic infers the JSON schema from your annotations. Full guide: [docs/adding-a-tool](https://fernandofatech.github.io/bedrock-agent-starter/adding-a-tool/).

## Deploying

```bash
cd terraform
terraform init
terraform apply -var="project=my-agent"
```

Provisioned: Lambda (Python 3.12), API Gateway HTTP API, DynamoDB sessions table, IAM roles, CloudWatch log group. **State backend, tags, naming and IAM boundaries are intentionally left for you.**

## Observability

Every turn emits a structured JSON log line:

```json
{
  "level": "info",
  "session_id": "s_abc...",
  "turn": 3,
  "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "input_tokens": 420,
  "output_tokens": 88,
  "tool_calls": ["calculator"],
  "duration_ms": 1830
}
```

EMF metrics published to CloudWatch namespace `BedrockAgent`:

- `Turns` (Count)
- `InputTokens`, `OutputTokens` (Count)
- `Duration` (Milliseconds)
- `ToolErrors` (Count)

## Evals

```bash
pytest tests/evals/
```

The runner replays the prompts in `tests/evals/golden.jsonl` and checks each expected substring / tool-call against the actual output. Fail on regressions.

## Repo layout

```
.
├── src/agent/           # agent core, tools, memory, observability, CLI, Lambda handler
├── tests/               # unit tests + eval harness
├── terraform/           # IaC skeleton (Lambda, API Gateway, DynamoDB, IAM)
├── docs/                # MkDocs Material (GitHub Pages)
├── frontend/            # dependency-free static landing
└── .github/workflows/   # CI + docs deploy
```

## Roadmap

- [ ] Bedrock Guardrails wiring (off by default).
- [ ] Streaming responses (Converse Stream API).
- [ ] Multi-model fallback (Sonnet → Haiku on throttle).
- [ ] Vector retrieval tool (Bedrock Knowledge Base).
- [ ] OpenTelemetry exporter for traces.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) — Conventional Commits required.

## License

[MIT](LICENSE) © Fernando Francisco Azevedo

## Author

**Fernando Francisco Azevedo** — Solution Architect, AWS & AI focus.
[fernando@moretes.com](mailto:fernando@moretes.com) · [LinkedIn](https://www.linkedin.com/in/fernando-francisco-azevedo/) · [fernando.moretes.com](https://fernando.moretes.com)
