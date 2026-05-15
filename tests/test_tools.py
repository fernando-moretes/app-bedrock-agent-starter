import pytest

from agent.tools import dispatch, registered_tools, tool_specs


def test_three_sample_tools_are_registered() -> None:
    names = registered_tools()
    assert "calculator" in names
    assert "get_time" in names
    assert "web_search" in names


def test_tool_specs_shape_matches_converse_api() -> None:
    specs = tool_specs()
    assert specs
    for spec in specs:
        assert "toolSpec" in spec
        ts = spec["toolSpec"]
        assert "name" in ts
        assert "description" in ts
        assert "inputSchema" in ts
        assert "json" in ts["inputSchema"]


def test_calculator_basic_arithmetic() -> None:
    assert dispatch("calculator", {"expression": "2 + 3"}) == 5.0
    assert dispatch("calculator", {"expression": "(123 * 456) - 789"}) == 55299.0
    assert dispatch("calculator", {"expression": "100 / 4"}) == 25.0
    assert dispatch("calculator", {"expression": "-5 + 2"}) == -3.0


def test_calculator_rejects_non_arithmetic() -> None:
    with pytest.raises(ValueError):
        dispatch("calculator", {"expression": "__import__('os').system('ls')"})


def test_get_time_returns_iso_string() -> None:
    out = dispatch("get_time", {"tz": "UTC"})
    assert isinstance(out, str)
    assert "T" in out  # ISO-8601 separator
    assert out.endswith("+00:00") or out.endswith("Z")


def test_get_time_invalid_tz_raises() -> None:
    with pytest.raises(ValueError):
        dispatch("get_time", {"tz": "Not/AnIANATz"})


def test_web_search_stub_returns_list() -> None:
    out = dispatch("web_search", {"query": "anything"})
    assert isinstance(out, list)
    assert out[0]["title"]
    assert out[0]["url"]


def test_dispatch_unknown_tool_raises() -> None:
    with pytest.raises(KeyError):
        dispatch("does_not_exist", {})
