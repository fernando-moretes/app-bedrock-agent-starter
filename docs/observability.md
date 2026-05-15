# Observability

Every agent turn emits structured logs and CloudWatch Embedded Metric Format records.

## Log fields

| Field | Purpose |
| --- | --- |
| `session_id` | Correlates all turns for a conversation |
| `turn` | Agent loop turn count |
| `model_id` | Bedrock model used |
| `input_tokens` | Input token count returned by Bedrock |
| `output_tokens` | Output token count returned by Bedrock |
| `tool_calls` | Tools invoked during the turn |
| `duration_ms` | End-to-end latency for the turn |

## Metrics

- `Turns`
- `InputTokens`
- `OutputTokens`
- `Duration`
- `ToolErrors`

Use these for dashboards around cost, latency, reliability, and runaway tool loops.
