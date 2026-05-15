"""Eval harness — replays prompts from golden.jsonl against the live agent.

By default this test is **skipped** unless ``AGENT_EVAL_RUN=1`` is set, because
it costs real Bedrock tokens. Run with:

```bash
AGENT_EVAL_RUN=1 pytest tests/evals/
```
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agent.agent import Agent
from agent.memory import InMemoryMemory

GOLDEN = Path(__file__).parent / "golden.jsonl"


def _load() -> list[dict[str, object]]:
    return [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]


@pytest.mark.skipif(
    os.environ.get("AGENT_EVAL_RUN") != "1",
    reason="set AGENT_EVAL_RUN=1 to run live evals against Bedrock (consumes tokens)",
)
@pytest.mark.parametrize("case", _load(), ids=lambda c: c["name"])
def test_golden_case(case: dict[str, object]) -> None:
    agent = Agent(memory=InMemoryMemory())
    result = agent.run(str(case["prompt"]))

    output_lower = result.output_text.lower()
    for needle in case.get("must_contain", []):  # type: ignore[union-attr]
        assert str(needle).lower() in output_lower, (
            f"output missing '{needle}': {result.output_text}"
        )

    must = set(case.get("must_call_tools", []) or [])  # type: ignore[arg-type]
    if must:
        assert must.issubset(set(result.tool_calls)), (
            f"expected tools {must}, got {result.tool_calls}"
        )

    must_not = set(case.get("must_not_call_tools", []) or [])  # type: ignore[arg-type]
    if must_not:
        assert not (must_not & set(result.tool_calls)), (
            f"unexpected tools called: {must_not & set(result.tool_calls)}"
        )
