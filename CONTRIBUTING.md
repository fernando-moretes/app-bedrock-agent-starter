# Contributing

## Workflow (gitflow)

- `main` — releases only, protected, every commit is tagged.
- `develop` — integration branch; open PRs here.
- `feature/*`, `release/*`, `hotfix/*` — short-lived branches.

```bash
git checkout develop && git pull
git checkout -b feature/short-description
# ...changes...
git push -u origin feature/short-description
```

Open a PR into `develop`. Title follows [Conventional Commits](https://www.conventionalcommits.org).

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## Checks before pushing

```bash
ruff check . && ruff format --check .
mypy src
pytest -v
```

## Adding a tool

1. Add a function in `src/agent/tools.py` decorated with `@tool(description="...")`.
2. Add a test in `tests/test_tools.py`.
3. If the tool is non-trivial, add a page under `docs/tools/`.

The tool registry uses Pydantic to infer the JSON schema from type hints — keep signatures explicit.

## Adding a memory backend

1. Subclass `Memory` in `src/agent/memory.py`.
2. Implement `read(session_id)` and `append(session_id, messages)`.
3. Register the backend in `Memory.from_env()`.

## Reporting issues

Open an issue with: what you ran, what you expected, what happened, environment (Python, AWS region, model id).
