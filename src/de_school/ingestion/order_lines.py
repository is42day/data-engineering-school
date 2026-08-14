"""Ingest the order_lines CSV source into raw Parquet.

Grain: one row per (order_id, line_number). Unlike the single-key ingestion
steps, deduplication happens on this composite key rather than the full row:
rows sharing a key that are otherwise identical collapse to one row, but
rows sharing a key with conflicting values are a data-quality error and fail
the whole ingestion rather than being silently resolved (no last-write-wins).
"""

import csv
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

KEY_COLUMNS = ("order_id", "line_number")
FK_COLUMNS = {"order_id": "orders", "product_id": "products"}


def ingest_order_lines(
    source_path: Path,
    output_path: Path,
    *,
    known_order_ids: set[str],
    known_product_ids: set[str],
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> Path:
    """Read order_lines.csv, validate, deduplicate, and write raw Parquet.

    Raises ValueError if a required key/FK column is missing, if any row has
    a missing/empty order_id or line_number, if any row's order_id/product_id
    is not present in known_order_ids/known_product_ids, or if two rows share
    the same (order_id, line_number) key with conflicting values — invalid
    rows fail the whole ingestion rather than being quarantined.
    """
    known_fk_ids = {"order_id": known_order_ids, "product_id": known_product_ids}

    with source_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing_columns = [c for c in KEY_COLUMNS if c not in fieldnames] + [
            c for c in FK_COLUMNS if c not in fieldnames and c not in KEY_COLUMNS
        ]
        if missing_columns:
            raise ValueError(
                f"{source_path} is missing required column(s): {missing_columns}"
            )

        rows = list(reader)

    bad_rows = [
        i
        for i, row in enumerate(rows, start=2)
        if any(not (row.get(col) or "").strip() for col in KEY_COLUMNS)
    ]
    if bad_rows:
        raise ValueError(
            f"{source_path} has empty {KEY_COLUMNS} on line(s): {bad_rows}"
        )

    for column, referenced_table in FK_COLUMNS.items():
        invalid_fk_rows = [
            i
            for i, row in enumerate(rows, start=2)
            if (row.get(column) or "").strip() not in known_fk_ids[column]
        ]
        if invalid_fk_rows:
            raise ValueError(
                f"{source_path} has '{column}' not found in {referenced_table} "
                f"on line(s): {invalid_fk_rows}"
            )

    rows_by_key: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        key = (row["order_id"], row["line_number"])
        rows_by_key.setdefault(key, []).append(row)

    for key, key_rows in rows_by_key.items():
        distinct_rows = {tuple(row.items()) for row in key_rows}
        if len(distinct_rows) > 1:
            raise ValueError(
                f"{source_path} has conflicting rows for order_id/line_number {key}"
            )

    deduplicated = [key_rows[0] for key_rows in rows_by_key.values()]

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
