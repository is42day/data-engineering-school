# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A teaching repository for learning data engineering by incrementally building one small data platform (CSV/JSON sources → Python ingestion → raw Parquet → DuckDB/SQL transformations → curated dimensions/facts → Power BI). The codebase is built incrementally: DE-001 (customer CSV ingestion) is implemented; SQL models and later exercises are not yet started. Exercises are defined incrementally in `docs/learning-path.md` (DE-001 through DE-006+), and each one is meant to be implemented via its own GitHub issue and branch, not delivered as a finished solution. When asked to "implement the pipeline" or similar, check `docs/learning-path.md` for the current exercise's acceptance criteria rather than designing the whole thing at once — don't scaffold SQL layers or later exercises' code ahead of the exercise that calls for them.

## Commands

```bash
uv sync --dev                       # install dependencies (Python 3.12+, uv required)
uv run pytest                       # run all tests
uv run pytest tests/test_file.py::test_name   # run a single test
uv run ruff check .                 # lint
uv run python -m de_school.pipeline # run the pipeline entry point
```

CI (`.github/workflows/ci.yml`) runs `uv sync --dev`, `uv run ruff check .`, and `uv run pytest` on every PR — match this locally before considering work done.

## Architecture

- `src/de_school/pipeline.py` is the orchestration entry point only (`run()`, called from `__main__`). It calls into dedicated step modules under `de_school.ingestion` rather than containing ingestion/transformation logic itself — extend it by adding calls to new step functions, not inline logic.
- Each ingestion step lives in its own module under `src/de_school/ingestion/` (e.g. `customers.py::ingest_customers`) and follows the pattern established by DE-001: takes explicit `source_path`/`output_path` `Path` arguments, accepts a `clock` callable (default `datetime.now(UTC)`) injected as a keyword-only argument so tests can freeze time, validates required columns/values and raises `ValueError` to fail the whole step fast rather than quarantining bad rows (an open decision per exercise — check `docs/learning-path.md` before assuming this for new steps), deduplicates exact-duplicate rows, and writes Arrow/Parquet output via `pyarrow`. Timestamps are stored UTC-naive (tz stripped after conversion) because pyarrow's tz-aware timestamps need the `tzdata` package for zoneinfo lookups, which isn't installed on Windows by default.
- `sql/` is organized in layers, added only as real models are introduced (don't scaffold all three upfront): `sql/staging/` (source-aligned cleanup, type normalization), `sql/intermediate/` (reusable joins/business calculations), `sql/marts/` (dimensions and facts consumed by Power BI). Every SQL model should document its purpose, expected grain, primary/natural key, key assumptions, and expected data-quality checks.
- `data/source/` holds small, committed, fictional teaching inputs (never real customer/employee/company data). `data/raw/` and `data/curated/` are generated outputs and are gitignored — never commit into them.
- Ruff config selects `E, F, I, B, UP` rules at line-length 100, targeting py312 (see `pyproject.toml`).

## Workflow expectations (from docs/working-agreement.md)

- One GitHub issue → one short-lived branch → one focused PR. Branches: `feature/de-001-...`, `fix/de-004-...`, `docs/de-002-...`. Commits are prefixed with the issue id, e.g. `DE-001 add customer CSV reader`.
- Prefer several small, meaningful commits over one large commit.
- Don't stage with a blanket `git add .`/`git add -A` — review what's being staged (this is explicit repo guidance, not just general caution).
- The PR template (`.github/pull_request_template.md`) expects: what/why, test commands run, data impact (input/output grain, keys affected, generated files), decisions/assumptions a reviewer can't infer from the code, and a learning note + open question.

## Review questions this repo cares about

When implementing or reviewing a pipeline step, these are the standing questions from `docs/getting-started.md`:

- What is the grain of the output?
- What happens when the input is empty or malformed?
- Can the step be run twice safely (idempotency)?
- Which assumptions are business rules vs. incidental implementation choices?
- How do we know the result is correct?
- What should be logged when it fails?
