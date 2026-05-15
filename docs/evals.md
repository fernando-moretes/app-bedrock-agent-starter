# Evals

The starter includes a lightweight eval harness under `tests/evals/`. Each case in `golden.jsonl` describes a prompt and expected observable behavior.

```bash
pytest tests/evals/
```

## When to add evals

- A new tool is added.
- The system prompt changes.
- The memory behavior changes.
- A bug fix protects an important user flow.
- A model migration changes response behavior.

Keep evals small, deterministic, and tied to behavior a user would notice.
