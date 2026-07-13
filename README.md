# Data Engineering School

A practical, collaborative repository for learning data engineering by building one small data platform incrementally.

## Learning goal

Turn simple source files into trustworthy analytical datasets while learning:

- Git branches, commits, pull requests, and reviews
- Python for ingestion and automation
- SQL for transformation and dimensional modelling
- Data-quality and unit testing
- Pipeline design, idempotency, logging, and CI

## Planned architecture

```text
CSV / JSON sources
        |
        v
Python ingestion
        |
        v
Raw Parquet files
        |
        v
DuckDB + SQL transformations
        |
        v
Curated dimensions and facts
        |
        v
Power BI
```

The first version deliberately contains placeholders. The purpose is to implement them together through issues and pull requests rather than receiving a finished solution.

## Start here

1. Read [`docs/getting-started.md`](docs/getting-started.md).
2. Read [`docs/working-agreement.md`](docs/working-agreement.md).
3. Pick the first exercise from [`docs/learning-path.md`](docs/learning-path.md).
4. Create an issue and a branch before changing code.

## Local setup

Prerequisites:

- Git
- Python 3.12+
- `uv`

```bash
git clone https://github.com/is42day/data-engineering-school.git
cd data-engineering-school
uv sync --dev
uv run pytest
uv run python -m de_school.pipeline
```

The pipeline currently raises a guided `NotImplementedError`. Making the first step run successfully is part of the initial exercise.

## Repository map

```text
src/de_school/       reusable Python pipeline code
sql/                 SQL transformations added over time
tests/               code and data-quality tests
data/source/         small versioned teaching inputs
data/raw/             generated raw outputs, not committed
data/curated/         generated analytical outputs, not committed
docs/                onboarding, decisions, and exercises
.github/              pull-request and issue templates
```

## Core rule

> One issue, one branch, one focused pull request.

Do not optimize for finishing quickly. Optimize for understanding why the pipeline is reliable and how another engineer can safely change it.
