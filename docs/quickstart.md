# Quickstart

## Install

```bash
git clone git@github.com:fernandofatech/bedrock-agent-starter.git
cd bedrock-agent-starter
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configure Bedrock

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

The AWS principal used locally must have permission for `bedrock:Converse` on the selected model.

## Run locally

```bash
agent chat
```

Try a prompt that exercises tool use:

```text
What time is it in Sao Paulo and what is (123 * 456) - 789?
```

## Run tests

```bash
ruff check .
ruff format --check .
mypy src
pytest -v
```
