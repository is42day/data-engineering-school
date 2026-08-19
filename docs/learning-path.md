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

## DE-FAB-001 — Establish the Microsoft Fabric development platform

**Goal:** Establish the smallest repeatable Fabric foundation before moving DE-003+ execution to Fabric.

Acceptance criteria:

- Create the capacity-assigned `de-school-dev` workspace.
- Connect the workspace to this GitHub repository, branch `main`, using `fabric/` as the Git folder.
- Create `lh_de_school_dev` and `env_de_school` in the workspace.
- Verify that a simple notebook can attach to the lakehouse and environment, write a disposable Delta table, and be committed through Fabric Git integration.
- Create and document workspace roles; do not put secrets or data in Git.
- Record the configured capacity, workspace, lakehouse, environment, and Git binding in the issue/PR.

Read [`docs/microsoft-fabric.md`](microsoft-fabric.md) before starting. It is the architecture and operating guide for all Fabric work.

## DE-003 — Build Fabric Bronze ingestion and Silver staging models

**Goal:** Land the four source files as Bronze Delta tables, then transform Bronze into typed, normalized Silver Delta tables, both through Fabric notebooks.

Acceptance criteria:

- Create a thin `nb_bronze_ingest_sources` notebook (naming per `docs/microsoft-fabric.md`'s `nb_<layer>_<purpose>` convention) attached to `lh_de_school_dev` and `env_de_school`.
- Load `customers.csv`, `products.csv`, `orders.csv`, and `order_lines.csv` from the lakehouse `Files` area into `bronze_customers`, `bronze_products`, `bronze_orders`, and `bronze_order_lines` Delta tables.
- Preserve source-aligned values; add ingest timestamp, batch/run identifier, and source name per row. No reporting calculations in Bronze.
- Create a thin `nb_silver_build_models` notebook attached to `lh_de_school_dev` and `env_de_school`.
- Transform the four `bronze_` tables into corresponding `silver_` tables using Spark SQL and/or PySpark.
- Normalize types and column names without embedding reporting logic.
- Document each table's grain, key, nullable fields, accepted values, and foreign-key expectations.
- Add checks for uniqueness, nulls, foreign-key validity, and accepted values (a `nb_quality_silver` notebook, or checks inline in `nb_silver_build_models` — decide and record which).
- Keep reusable validation code in `src/de_school/`; do not grow one large notebook.
- Decide and document the error policy for invalid Bronze/Silver records (fail the run vs. quarantine vs. accept with warning) — this repo's existing ingestion steps fail fast, but confirm that still holds for Fabric notebooks before assuming it.

## DE-004 — Build the Fabric Gold star schema

Create `gold_dim_customer`, `gold_dim_product`, and `gold_fact_sales`. Document the grain of each model, then create a Direct Lake semantic model and a small Power BI report over the Gold tables.

## DE-005 — Add incremental loading

Process only new or changed orders into Delta tables. Demonstrate an idempotent rerun and use Delta-aware techniques such as `MERGE` where appropriate.

## DE-006 — Orchestrate and promote the Fabric solution

Create `pl_de_school` to run Bronze ingestion, Silver transformation, Silver quality checks, Gold transformation, and Gold quality checks in dependency order. Add `de-school-test`, then practise promotion through a Fabric deployment pipeline. Keep GitHub CI responsible for source-code tests and linting; pipeline-run data checks protect Fabric data.

## Later extensions

- API ingestion with pagination and retry handling
- Package and attach reusable Python code as a wheel through the Fabric environment
- Production workspace and controlled DEV/TEST/PROD promotion
- Secrets management and environment-specific configuration
- Source shortcuts, APIs, and incremental external ingestion
- More advanced orchestration, monitoring, and alerting
