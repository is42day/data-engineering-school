# Learning Path

Each exercise should become a GitHub issue before implementation. Copy the relevant section into the issue and refine it together.

## DE-001 — Ingest customers from CSV

**Goal:** Learn the repository workflow and implement the first repeatable ingestion step.

Acceptance criteria:

- Add a small `customers.csv` teaching dataset under `data/source/`.
- Create `src/de_school/ingestion/customers.py`.
- Read the CSV and validate that `customer_id` is present and non-empty.
- Remove exact duplicate rows.
- Add an `ingested_at` timestamp in UTC.
- Write `data/raw/customers.parquet`.
- Add focused unit tests.
- Update the pipeline entry point to call the ingestion step.

Open decisions to discuss together:

- Which library should read the CSV: Python standard library, PyArrow, DuckDB, or pandas?
- Should invalid rows fail the whole pipeline or be quarantined?
- How should timestamps be made testable?

## DE-002 — Ingest orders

Add customers, products, orders, and order-line inputs. Define the grain of every file before coding. Include at least one invalid foreign key and decide how to handle it.

## DE-003 — Build staging SQL models

Create SQL that normalizes types and column names without embedding reporting logic. Add tests for uniqueness, nulls, and accepted values.

## DE-004 — Build a star schema

Create `dim_customer`, `dim_product`, and `fact_sales`. Document the grain of each model and connect the output to Power BI.

## DE-005 — Add incremental loading

Process only new or changed orders. Demonstrate that rerunning the same batch does not duplicate facts.

## DE-006 — Extend CI with data-quality checks

CI already runs `ruff check` and `pytest` on every pull request (`.github/workflows/ci.yml`). Extend it to also fail on data-quality problems: run the checks from DE-003/DE-004 (uniqueness, nulls, accepted values) as part of the workflow, not just locally. Decide what should block a merge versus what should only warn.

## Later extensions

- API ingestion with pagination and retry handling
- dbt migration for SQL transformations
- orchestration with Dagster, Prefect, or Airflow
- Docker development environment
- deployment to Azure or Databricks
- secrets management and environment-specific configuration
