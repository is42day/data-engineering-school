"""Read a single column of a raw Parquet file back into a set of values.

Used by ingestion steps that validate a foreign key against a parent entity
that has already been ingested (e.g. orders.customer_id against the raw
customers output), so FK checks are always against what actually landed in
the parent step's output rather than its source file.
"""

from pathlib import Path

import pyarrow.parquet as pq


def read_id_set(parquet_path: Path, column: str) -> set[str]:
    """Read one column of a raw Parquet file into a set."""
    return set(pq.read_table(parquet_path, columns=[column]).column(column).to_pylist())
