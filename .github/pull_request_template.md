## Summary

<!-- One or two sentences describing the change. Link related issues. -->

## Type of change

- [ ] feat - new agent capability, tool, memory backend, or deployment surface
- [ ] fix - bug fix
- [ ] docs - documentation only
- [ ] refactor - internal change with no behavior difference
- [ ] test - adding or fixing tests/evals
- [ ] chore - build, CI, deps

## Test plan

<!-- How did you verify this change? Add commands and outcomes. -->

- [ ] `ruff check . && ruff format --check .`
- [ ] `mypy src`
- [ ] `pytest -v`

## Checklist

- [ ] Title follows [Conventional Commits](https://www.conventionalcommits.org)
- [ ] Target branch is `develop` (or `main` only for hotfixes/releases)
- [ ] Docs updated if behavior or interface changed
- [ ] Evals updated if model/tool behavior changed
- [ ] CHANGELOG updated under `Unreleased`
