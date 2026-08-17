# Fabric Workspace Sync

This folder is the Git-integration target for the project's Microsoft Fabric
workspace. It is managed by Fabric's own source control sync (Workspace →
Source control → Commit), not hand-edited the way `sql/` and `src/` are —
expect its contents to be auto-generated Fabric item definitions (Lakehouse,
Warehouse, Notebook, and pipeline items with their accompanying `.platform`
metadata files).

## Scope

- Ingestion (currently `src/de_school/ingestion/`, run locally via
  `uv run python -m de_school.pipeline`) is moving into Fabric notebooks.
- SQL staging/intermediate/marts models (currently documented as the planned
  `sql/` layers in `sql/README.md`) are moving into a Fabric Warehouse as
  T-SQL views, replacing the local DuckDB-based plan.
- Power BI connects directly to the Fabric Warehouse/Lakehouse (Direct Lake)
  instead of a local file-based connection.

`src/de_school/`, `sql/`, and `data/` are unaffected by this migration until
each corresponding exercise is explicitly redone against Fabric — don't
assume they're superseded just because this folder exists.

## Workflow

- This folder is synced from the `fabric/workspace-sync` branch, not `main`
  directly, so Fabric's auto-generated commits go through a normal PR before
  merging — same review discipline as `docs/working-agreement.md` describes
  for hand-written code.
- Treat changes originating here as their own issue/PR, separate from
  ingestion or SQL-layer PRs that touch `src/`, `sql/`, or `tests/`.
