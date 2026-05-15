# Adding a tool

Tools are plain Python functions registered with the `@tool` decorator. Type annotations are converted into the JSON schema passed to the Bedrock Converse API.

```python
from agent.tools import tool


@tool(description="Return the status for an internal ticket.")
def get_ticket_status(ticket_id: str) -> str:
    return "open"
```

The tool is automatically included in `tool_specs()` and can be called by the agent through `dispatch()`.

## Checklist for production tools

- Validate all external inputs.
- Use timeouts when calling APIs.
- Return compact, model-readable output.
- Emit useful errors instead of swallowing failures.
- Add unit tests for happy path and failure path.
- Add eval cases if the tool changes agent behavior.

## Replacing the search stub

The default `web_search` tool intentionally returns canned data. Replace it with a real provider such as Brave, Tavily, Serper, or an internal enterprise search API before production use.
