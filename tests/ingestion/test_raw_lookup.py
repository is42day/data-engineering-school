from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from de_school.ingestion.raw_lookup import read_id_set


def test_read_id_set_returns_unique_column_values(tmp_path: Path) -> None:
    table = pa.table({"customer_id": ["C001", "C002", "C001"]})
    path = tmp_path / "customers.parquet"
    pq.write_table(table, path)

    assert read_id_set(path, "customer_id") == {"C001", "C002"}
