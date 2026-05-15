"""Tool registry and three sample tools.

`@tool(description=...)` registers a function, derives a JSON schema from its
type hints, and makes it discoverable via ``tool_specs()`` and ``dispatch()``.
"""

from __future__ import annotations

import datetime as _dt
import inspect
import zoneinfo
from collections.abc import Callable
from typing import Any, get_type_hints

_REGISTRY: dict[str, dict[str, Any]] = {}

_PY_TO_JSON: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def tool(description: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that registers a function as an agent tool.

    The function's annotations become the JSON schema for the tool's input.
    Supported parameter types: ``str``, ``int``, ``float``, ``bool``.

    Example:
        @tool(description="Add two numbers.")
        def add(a: int, b: int) -> int:
            return a + b
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(fn)
        hints = get_type_hints(fn)
        properties: dict[str, dict[str, str]] = {}
        required: list[str] = []
        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue
            py_type = hints.get(name, str)
            json_type = _PY_TO_JSON.get(py_type, "string")
            properties[name] = {"type": json_type}
            if param.default is inspect.Parameter.empty:
                required.append(name)
        _REGISTRY[fn.__name__] = {
            "fn": fn,
            "spec": {
                "toolSpec": {
                    "name": fn.__name__,
                    "description": description,
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": properties,
                            "required": required,
                        }
                    },
                }
            },
        }
        return fn

    return decorator


def registered_tools() -> list[str]:
    """Return the names of the registered tools (sorted)."""
    return sorted(_REGISTRY.keys())


def tool_specs() -> list[dict[str, Any]]:
    """Return the tool specs in the shape the Converse API expects."""
    return [entry["spec"] for entry in _REGISTRY.values()]


def dispatch(name: str, arguments: dict[str, Any]) -> Any:
    """Execute the registered tool by name with the given arguments."""
    if name not in _REGISTRY:
        raise KeyError(f"Tool '{name}' is not registered.")
    return _REGISTRY[name]["fn"](**arguments)


# ----- Sample tools ---------------------------------------------------------


@tool(
    description="Evaluate a basic arithmetic expression containing +, -, *, /, parentheses and numbers."
)
def calculator(expression: str) -> float:
    """Compute a basic arithmetic expression.

    The implementation parses with ``ast`` to avoid ``eval`` — only literal
    numbers and the four operators are allowed.
    """
    import ast
    import operator

    binary_operators: dict[type[ast.operator], Callable[[float, float], float]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    unary_operators: dict[type[ast.unaryop], Callable[[float], float]] = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            binary_op = binary_operators.get(type(node.op))
            if binary_op is None:
                raise ValueError(f"Unsupported binary operator: {ast.dump(node.op)}")
            return binary_op(_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            unary_op = unary_operators.get(type(node.op))
            if unary_op is None:
                raise ValueError(f"Unsupported unary operator: {ast.dump(node.op)}")
            return unary_op(_eval(node.operand))
        raise ValueError(f"Unsupported expression node: {ast.dump(node)}")

    return _eval(ast.parse(expression, mode="eval").body)


@tool(
    description="Return the current ISO-8601 datetime in the given IANA timezone (e.g. 'America/Sao_Paulo')."
)
def get_time(tz: str = "UTC") -> str:
    """Return the current datetime as ISO-8601 in the requested timezone."""
    try:
        zone = zoneinfo.ZoneInfo(tz)
    except zoneinfo.ZoneInfoNotFoundError as e:
        raise ValueError(f"Unknown timezone: {tz}") from e
    return _dt.datetime.now(tz=zone).isoformat()


@tool(
    description="Web search — STUB. Replace with a real provider (Brave, Tavily, Serper) before production use."
)
def web_search(query: str, max_results: int = 3) -> list[dict[str, str]]:
    """Stub web search returning canned results.

    Plug in a real provider — Brave Search, Tavily, Serper — by replacing the body.
    """
    _ = max_results
    return [
        {
            "title": f"Stub result for '{query}'",
            "url": "https://example.com/replace-this-tool",
            "snippet": "This is a placeholder. Replace web_search with a real provider.",
        }
    ]
