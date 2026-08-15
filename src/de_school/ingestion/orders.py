"""Ingest the orders CSV source into raw Parquet.

Grain: one row per order_id (exact duplicate rows are dropped; the input
is not expected to contain updates to the same order_id with different
values, so no last-write-wins logic is applied here).
"""

import csv
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

REQUIRED_COLUMN = "order_id"
FK_COLUMN = "customer_id"


def ingest_orders(
    source_path: Path,
    output_path: Path,
    *,
    known_customer_ids: set[str],
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> Path:
    """Read orders.csv, validate, deduplicate, and write raw Parquet.

    Raises ValueError if the required order_id/customer_id columns are
    missing, if any row has a missing/empty order_id, or if any row's
    customer_id is not present in known_customer_ids — invalid rows fail
    the whole ingestion rather than being quarantined.
    """
    with source_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing_columns = [c for c in (REQUIRED_COLUMN, FK_COLUMN) if c not in fieldnames]
        if missing_columns:
            raise ValueError(
                f"{source_path} is missing required column(s): {missing_columns}"
            )

        rows = list(reader)

    bad_rows = [
        i for i, row in enumerate(rows, start=2) if not (row.get(REQUIRED_COLUMN) or "").strip()
    ]
    if bad_rows:
        raise ValueError(
            f"{source_path} has empty '{REQUIRED_COLUMN}' on line(s): {bad_rows}"
        )

    invalid_fk_rows = [
        i
        for i, row in enumerate(rows, start=2)
        if (row.get(FK_COLUMN) or "").strip() not in known_customer_ids
    ]
    if invalid_fk_rows:
        raise ValueError(
            f"{source_path} has '{FK_COLUMN}' not found in customers on line(s): {invalid_fk_rows}"
        )

    deduplicated = list({tuple(row.items()): row for row in rows}.values())

    # Stored as UTC-naive: pyarrow's tz-aware timestamps need the `tzdata`
    # package for zoneinfo lookups, which isn't installed on Windows by default.
    ingested_at = clock().astimezone(UTC).replace(tzinfo=None)
    columns: dict[str, list] = {name: [] for name in fieldnames}
    for row in deduplicated:
        for name in fieldnames:
            columns[name].append(row[name])
    columns["ingested_at"] = [ingested_at] * len(deduplicated)

    schema = pa.schema(
        [(name, pa.string()) for name in fieldnames] + [("ingested_at", pa.timestamp("us"))]
    )
    table = pa.table(columns, schema=schema)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output_path)
    return output_path
