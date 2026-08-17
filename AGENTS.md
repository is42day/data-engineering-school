# Repository Guidelines

## Project Structure & Module Organization

- `src/de_school/` contains reusable Python code. Keep `pipeline.py` as a small orchestration entry point and place ingestion logic in focused modules such as `ingestion/customers.py`.
- `tests/` mirrors source modules; `sql/` gains transformations as exercises introduce them.
- `data/source/` contains small, fictional, versioned inputs. `data/raw/` and `data/curated/` are generated and must not be committed.
- `docs/` contains onboarding, the working agreement, and exercise acceptance criteria. Check `docs/learning-path.md` before implementing a new exercise.

## Build, Test, and Development Commands

Python 3.12+ and `uv` are required.

```bash
uv sync --dev                         # install dependencies
uv run python -m de_school.pipeline   # run the pipeline
uv run pytest                         # run all tests
uv run pytest tests/ingestion/test_customers.py  # run one test module
uv run ruff check .                   # lint the repository
```

Before submitting, run the lint and test commands used by CI.

## Coding Style & Naming Conventions

Use four-space indentation, Python type hints, and `pathlib.Path`. Ruff targets Python 3.12, enforces `E`, `F`, `I`, `B`, and `UP`, and limits lines to 100 characters. Use `snake_case` for modules, functions, and variables; use `PascalCase` for classes. Inject nondeterministic dependencies—for example, pass a clock so tests can freeze timestamps.

## Testing Guidelines

Tests use pytest and follow `test_<behavior>` naming. Cover normal, empty, malformed, and idempotent cases. Use `tmp_path` for generated files and assert content and failure side effects. No coverage threshold is configured; cover each exercise's acceptance criteria.

## Human & Agent Collaboration

Two contributors work here: one with Claude and one with Codex. Treat `AGENTS.md` as shared guidance; keep `CLAUDE.md` limited to Claude-specific behavior and consistent with this file. Before editing, inspect `git status` and the current diff. Use separate issue branches, avoid concurrent edits to the same files, and record handoffs in issues or PRs rather than agent chat. Put durable architecture and data-contract decisions in `docs/`.

## Commit & Pull Request Guidelines

Follow one issue, one short-lived branch, and one focused PR. Name branches like `feature/de-001-customer-ingestion`, `fix/de-004-duplicate-facts`, or `docs/de-002-document-grain`. Prefix commits with the issue ID, for example `DE-001 add ingestion tests`, and prefer several meaningful commits over one large commit.

Complete the PR template: summarize what and why, link the issue (`Closes #123`), list tests run, document data grain/key impacts and generated files, record decisions or limitations, and include one learning plus one open question. Review specific staged files instead of staging the entire tree automatically.
