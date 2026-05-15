from agent.memory import InMemoryMemory


def test_inmemory_starts_empty() -> None:
    m = InMemoryMemory()
    assert m.read("s1") == []


def test_inmemory_append_then_read_returns_chronological() -> None:
    m = InMemoryMemory()
    m.append("s1", [{"role": "user", "content": [{"text": "hi"}]}])
    m.append("s1", [{"role": "assistant", "content": [{"text": "hello"}]}])
    out = m.read("s1")
    assert len(out) == 2
    assert out[0]["role"] == "user"
    assert out[1]["role"] == "assistant"


def test_inmemory_sessions_are_isolated() -> None:
    m = InMemoryMemory()
    m.append("s1", [{"role": "user", "content": [{"text": "a"}]}])
    m.append("s2", [{"role": "user", "content": [{"text": "b"}]}])
    assert len(m.read("s1")) == 1
    assert len(m.read("s2")) == 1
    assert m.read("s1") != m.read("s2")
