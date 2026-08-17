# Microsoft Fabric Guide

This is the operating guide for the Data Engineering School Fabric migration. It deliberately starts small: the goal is to learn a coherent, deployable data platform, not to introduce every Fabric feature at once.

DE-001 and DE-002 remain local exercises. They teach input grain, validation, duplicate handling, idempotency, focused Python modules, and unit tests. From DE-003 onward, Microsoft Fabric is the runtime and OneLake + Delta is the persistent data layer.

## Target architecture

```text
GitHub repository                         Microsoft Fabric DEV workspace
-----------------                         -----------------------------
src/de_school/  <--- reusable Python ---> Fabric environment (later: wheel)
tests/          <--- local tests -------- notebooks: thin jobs
fabric/         <--- Fabric Git sync ---- lakehouse: Delta tables in OneLake
                                             |
source files / pipeline ingestion ----------> Bronze
                                                |
                                                v
                                             Silver
                                                |
                                                v
                                             Gold
                                                |
                                                v
                                  Direct Lake semantic model -> Power BI
                                                ^
                                  Fabric pipeline orchestrates notebooks
```

Use one lakehouse for this learning project. Separate lakehouses, domains, and multiple compute engines would add operational complexity without improving the lesson.

## Fabric concepts in this project

| Concept | Meaning here |
| --- | --- |
| Capacity | The paid/shared Fabric compute and feature allocation. A workspace must be assigned to the available capacity to use Fabric workloads. Monitor its usage, but do not tune capacity in the first exercise. |
| Workspace | The collaboration and security boundary containing Fabric items. We use separate workspaces for DEV, then TEST and PROD when promotion becomes a learning objective. |
| OneLake | Fabric's unified logical data lake. Fabric items read and write data there; it is not a Git repository. |
| Lakehouse | The item that exposes a `Files` area and a managed `Tables` area in OneLake. `Tables` holds queryable Delta tables. |
| Delta Lake | The table format for the Bronze, Silver, and Gold tables. It provides table semantics suitable for incremental loads, `MERGE`, and history. |
| Notebook | A Spark job authoring surface. A notebook should configure and call a small transformation or check, not become an untestable application. |
| Environment | Versioned Spark runtime, library, and compute configuration shared by notebooks. |
| Data pipeline | Data Factory orchestration of notebook jobs, dependencies, parameters, schedules, and run monitoring. |
| Semantic model / Direct Lake | The Power BI model over Gold Delta tables. Direct Lake reads the OneLake tables without a traditional import refresh. |

For current product details, use the Microsoft Learn pages for [OneLake and lakehouses](https://learn.microsoft.com/fabric/onelake/create-lakehouse-onelake), [notebooks](https://learn.microsoft.com/fabric/data-engineering/notebook-source-control-deployment), [environments](https://learn.microsoft.com/fabric/data-engineering/environment-git-and-deployment-pipeline), [pipeline notebook activities](https://learn.microsoft.com/fabric/data-factory/notebook-activity), and [Fabric CI/CD](https://learn.microsoft.com/fabric/fundamentals/understand-best-practices-fabric-cicd).

## Workspace, naming, and access

Start with only DEV:

```text
Workspace:   de-school-dev
Lakehouse:   lh_de_school_dev
Environment: env_de_school
Pipeline:    pl_de_school
Notebook:    nb_<layer>_<purpose>
```

Examples:

```text
nb_bronze_ingest_sources
nb_silver_build_models
nb_quality_silver
nb_gold_build_star
nb_quality_gold
sm_de_school
```

When needed, add `de-school-test` and `de-school-prod`, each with its own lakehouse and environment: `lh_de_school_test`, `env_de_school_test`, and so on. Do not share one DEV lakehouse across stages: stage separation must include data as well as item definitions.

Give only the people who build the project Member or Contributor access as appropriate, keep workspace Admin access limited, and use Viewer access for report consumers. Record the chosen roles in the DE-FAB-001 issue. Never put passwords, keys, tokens, or personal data in notebooks or Git.

## Git and repository strategy

Connect the DEV workspace to:

```text
Repository: is42day/data-engineering-school
Branch:     main
Git folder: fabric/
```

Fabric controls the precise serialized folders and files beneath `fabric/`; do not pre-create or hand-edit a guessed item layout. Create/configure items in Fabric, synchronize them, and review the generated definitions like source code. Put hand-authored, reusable Python in `src/de_school/` and its tests in `tests/`, not inside Fabric-generated folders.

Git tracks Fabric item definitions and configuration, not lakehouse table data or `Files` contents. Lakehouse metadata, shortcuts, notebooks, environments, pipelines, and supported semantic-model definitions can participate in lifecycle management, but data must be loaded and validated per workspace. See [Lakehouse Git and deployment behavior](https://learn.microsoft.com/fabric/data-engineering/lakehouse-git-deployment-pipelines).

### Branch workflow

Keep the repository agreement unchanged:

1. Create one issue for one bounded outcome.
2. Branch from updated `main`, for example `feature/de-fab-001-platform` or `feature/de-003-silver-models`.
3. Make only the code, docs, and Fabric-definition changes required by that issue.
4. Synchronize Fabric changes to the feature branch, review the diff, and open one focused PR.
5. Merge only after review; then synchronize the DEV workspace with `main`.

Avoid concurrent Fabric edits to the same workspace item. A workspace Git connection has one selected branch at a time, so agree who switches or synchronizes it. Do not use Git sync as a substitute for PR review.

## Bronze, Silver, and Gold design

Use Delta tables in `lh_de_school_<stage>` with a layer prefix, not separate lakehouses:

```text
bronze_customers       bronze_products
bronze_orders          bronze_order_lines

silver_customers       silver_products
silver_orders          silver_order_lines

gold_dim_customer      gold_dim_product
gold_fact_sales
```

| Layer | Responsibility | Rules |
| --- | --- | --- |
| Bronze | Capture source-aligned records and operational metadata. | Preserve source meaning; add ingest timestamp, batch/run identifier, and source name. Do not add reporting calculations. |
| Silver | Produce clean, typed, standardized, source-conformed tables. | Cast types, normalize names/strings, handle invalid records by the agreed policy, and assert keys and relationships. |
| Gold | Produce business-facing dimensions and facts. | Declare grain before coding, document measures and joins, and expose only stable reporting tables to the semantic model. |

For DE-003, `silver_orders` is not a report: it is a trustworthy order-level staging table. For DE-004, `gold_fact_sales` must state its grain explicitly (for example, one row per order line) before a transformation is written.

## Notebook and Python responsibilities

Notebooks should be small, named by their outcome, parameterized where useful, and safe to rerun. A practical initial set is:

```text
nb_bronze_ingest_sources  -> source files to Bronze Delta tables
nb_silver_build_models    -> Bronze to Silver transformations
nb_quality_silver         -> Silver blocking checks
nb_gold_build_star        -> Silver to Gold dimensions and facts
nb_quality_gold           -> Gold blocking checks
```

Prefer Spark SQL for clear relational transformations and PySpark for programmatic ingestion or logic that genuinely needs code. Do not carry DuckDB into Fabric just because it was useful locally; DE-003+ should teach Spark, SQL, Delta, and OneLake.

Keep reusable, deterministic Python outside notebooks in `src/de_school/`, with unit tests in `tests/`. In the first Fabric exercises, notebooks may use only Fabric-native code. When a shared library becomes useful, package the project as a wheel, attach it to `env_de_school`, and test it locally before using it in a notebook. This preserves the principle that notebooks orchestrate and expose transformations while libraries contain reusable logic.

## Orchestration and quality

After the notebooks work independently, `pl_de_school` should run them in this order:

```text
nb_bronze_ingest_sources
        -> nb_silver_build_models
        -> nb_quality_silver
        -> nb_gold_build_star
        -> nb_quality_gold
```

Use pipeline notebook activities to pass explicit parameters such as a source location, `run_id`, or processing date. Start with manual runs, then add a schedule only when there is a real cadence to practise. A pipeline run should fail when a blocking quality notebook fails; it must not continue to Gold after failing Silver checks.

Split testing by feedback loop:

| Where | What belongs there |
| --- | --- |
| Local GitHub CI | `ruff`, `pytest`, pure Python transformation and validation logic, schema/contract fixtures where feasible. |
| Fabric quality notebooks | Checks against the actual Bronze/Silver/Gold Delta tables: non-null keys, uniqueness, accepted values, referential integrity, and row-count sanity. |
| PR/review | Grain, business assumptions, naming, idempotency plan, and whether a check blocks a run or only warns. |

Keep a check's rule close to its layer. For example, `silver_orders.customer_id` reference validity belongs in Silver quality; whether every customer appears in a sales report is not a Bronze ingestion concern. Decide early whether invalid records fail the run, are quarantined, or are accepted with warnings, and document the decision in the task's PR.

## Semantic model and reporting

Create `sm_de_school` only after Gold tables are correct. It should connect to Gold tables using Direct Lake, model the relationships between dimensions and facts, and contain explicitly named measures. Reports consume the semantic model, not Bronze or Silver tables.

Direct Lake is a serving choice, not a replacement for data modelling or data-quality work. Verify its behavior and capacity considerations in the current [Fabric lakehouse tutorial](https://learn.microsoft.com/fabric/data-engineering/tutorial-build-lakehouse) before expanding reporting.

## DEV, TEST, and PROD promotion

Do not create all stages during DE-FAB-001. Add TEST when DE-006 introduces a promotion practice, and add PROD only when there is a genuine audience or operating need.

```text
Feature branch -> reviewed PR -> main / DEV workspace
                                     |
                                     v
                         deployment pipeline: DEV -> TEST -> PROD
```

Use Fabric Git integration for version control and PR review. Use Fabric deployment pipelines to promote tested workspace item definitions between environment workspaces. Keep dependent items (lakehouse, environment, notebooks, pipeline, semantic model) together in each workspace so Fabric can rebind dependencies during deployment. Review each deployment diff and use target-stage rules or configuration only when a real environment-specific value exists.

Deploying a lakehouse creates or promotes its definition, not its table data. Each stage needs its own data loading/refresh process, and target-stage shortcuts may need environment-specific configuration. This is why a successful deployment is not evidence that TEST data is correct.

## What not to introduce yet

Avoid these until a later issue makes the need concrete:

- separate Bronze, Silver, and Gold lakehouses or domain workspaces;
- dbt, Airflow, Dagster, Prefect, Docker, or another orchestration engine;
- a large custom framework around notebooks;
- streaming, eventhouses, real-time intelligence, ML, mirroring, or complex shortcuts;
- a wheel package before code is actually reused by more than one notebook;
- schedules, alerts, service principals, and secret stores before the manual path works;
- production data, personal data, or real secrets in this teaching repository.

## Exact implementation sequence

### DE-FAB-001 — Establish the development platform

1. Create the GitHub issue and branch `feature/de-fab-001-platform`.
2. Confirm the available Fabric capacity and create `de-school-dev` assigned to it.
3. Connect the workspace to this repository, `main`, and the `fabric/` folder. If a feature-branch workflow is being practised in the Fabric UI, switch the binding deliberately and return it to `main` after merge.
4. Create `lh_de_school_dev` and `env_de_school`; select the supported default Spark runtime and record only intentional library/configuration changes.
5. Create a small disposable notebook, attach the lakehouse and environment, write and read a non-sensitive Delta test table, then remove or clearly mark the test table.
6. Synchronize the generated Fabric definitions, review them, and make the focused PR with this guide/learning-path update as the contract.

### DE-003 — Silver staging

1. Add the Bronze ingestion notebook and its source/data contract.
2. Build the four Silver tables with explicit keys, types, and error policy.
3. Add and run Silver quality checks; prove reruns are safe.
4. Synchronize the new item definitions and open one focused PR.

### DE-004 — Gold and reporting

1. Declare the grain of each dimension and fact.
2. Build Gold Delta tables and Gold quality checks.
3. Create `sm_de_school` in Direct Lake mode, relationships, measures, and a small report.

### DE-005 and DE-006 — Incremental processing and lifecycle

1. Add incremental strategy and rerun tests using Delta-aware writes/`MERGE` where needed.
2. Create `pl_de_school` around the established notebook sequence.
3. Add TEST and practise a deployment-pipeline promotion before adding PROD.

At every step, preserve the repository's rule: one issue, one branch, one focused PR. A Fabric feature is finished only when its definition is versioned, its data contract and quality behavior are documented, and another contributor can reproduce the path.
