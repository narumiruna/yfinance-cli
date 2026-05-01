# Repository Guidelines

## Project Structure & Module Organization

`src/yfinance_cli/` contains the installable package. Keep CLI wiring in `cli.py`, and add new modules beside it as commands grow instead of letting one file become monolithic. `tests/` contains the pytest suite; mirror package behavior with `test_*.py` files. `.github/workflows/` defines CI, publish, and container automation. `CONTEXT.md` stores product vocabulary, and `MEMORY.md` stores durable implementation preferences.

## Build, Test, and Development Commands

- `uv sync`: install runtime and development dependencies for Python 3.12.
- `uv run yf --help`: run the local CLI entrypoint.
- `uv build`: build the wheel and source distribution locally.
- `just format`: run `ruff format`.
- `just lint`: run `ruff check --fix`.
- `just type`: run `ty check`.
- `just test`: run `pytest -v -s --cov=src tests`.
- `just all`: run the full local quality gate.

If dependencies change, update `uv.lock` with `uv lock`.

## Coding Style & Naming Conventions

Use 4-space indentation, explicit type hints, and small focused modules. Ruff is the primary style gate; the line length is 120. Imports are intentionally single-line because `isort` is configured with `force-single-line = true`. Use `snake_case` for modules, functions, and test files. Keep Typer command names short and CLI-oriented, and stay close to `yfinance` semantics unless a terminal-specific improvement is clearly justified.

## Testing Guidelines

Use `pytest` for unit and CLI tests. Prefer fast, deterministic tests that mock network behavior instead of hitting live Yahoo Finance endpoints. Name files `test_*.py` and group tests by command behavior or output mode. CI collects coverage for `src`, but no numeric minimum is enforced yet; new features should still ship with focused tests.

## Commit & Pull Request Guidelines

The current history is minimal (`Initial commit`, `init commit`), so there is no strict repository-specific commit convention yet. Use short, imperative commit subjects and keep each commit scoped to one logical change. Open pull requests against `main`, and make sure lint, type checks, and tests pass locally first. Include a concise summary, link related issues when relevant, and add example `yf ...` commands or terminal output when you change CLI UX. `CODEOWNERS` assigns the repository to `@narumiruna`, so expect owner review before merge.

## Configuration Notes

Do not commit secrets or local credentials. Keep repository configuration in tracked files such as `pyproject.toml`, `justfile`, and workflow YAML, and avoid ad hoc local-only behavior that is not documented.
