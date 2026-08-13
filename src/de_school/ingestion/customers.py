"""Ingest the customers CSV source into raw Parquet.

Grain: one row per customer_id (exact duplicate rows are dropped; the input
is not expected to contain updates to the same customer_id with different
values, so no last-write-wins logic is applied here).
"""

import csv
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

REQUIRED_COLUMN = "customer_id"


def ingest_customers(
    source_path: Path,
    output_path: Path,
    *,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> Path:
    """Read customers.csv, validate, deduplicate, and write raw Parquet.

    Raises ValueError if the required customer_id column is missing, or if
    any row has a missing/empty customer_id — invalid rows fail the whole
    ingestion rather than being quarantined.
    """
    with source_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if REQUIRED_COLUMN not in fieldnames:
            raise ValueError(
                f"{source_path} is missing required column '{REQUIRED_COLUMN}'"
            )

        rows = list(reader)

    bad_rows = [
        i for i, row in enumerate(rows, start=2) if not (row.get(REQUIRED_COLUMN) or "").strip()
    ]
    if bad_rows:
        raise ValueError(
            f"{source_path} has empty '{REQUIRED_COLUMN}' on line(s): {bad_rows}"
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
