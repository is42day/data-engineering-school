from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from de_school.ingestion.products import ingest_products

FIXED_CLOCK = lambda: datetime(2024, 1, 1, tzinfo=UTC)  # noqa: E731


def write_csv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_ingest_writes_one_row_per_product(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "products.csv",
        "product_id,product_name\nP001,Wireless Mouse\nP002,Mechanical Keyboard\n",
    )
    output = tmp_path / "products.parquet"

    ingest_products(source, output, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.num_rows == 2
    assert table.column("product_id").to_pylist() == ["P001", "P002"]


def test_ingest_drops_exact_duplicate_rows(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "products.csv",
        "product_id,product_name\nP001,Wireless Mouse\nP001,Wireless Mouse\n",
    )
    output = tmp_path / "products.parquet"

    ingest_products(source, output, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.num_rows == 1


def test_ingest_adds_ingested_at_from_clock(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "products.csv", "product_id,product_name\nP001,Wireless Mouse\n")
    output = tmp_path / "products.parquet"

    ingest_products(source, output, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.column("ingested_at").to_pylist() == [datetime(2024, 1, 1)]


def test_ingest_raises_on_missing_product_id_value(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "products.csv",
        "product_id,product_name\nP001,Wireless Mouse\n,Mechanical Keyboard\n",
    )
    output = tmp_path / "products.parquet"

    with pytest.raises(ValueError, match="empty 'product_id'"):
        ingest_products(source, output, clock=FIXED_CLOCK)

    assert not output.exists()


def test_ingest_raises_on_missing_product_id_column(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "products.csv", "product_name\nWireless Mouse\n")
    output = tmp_path / "products.parquet"

    with pytest.raises(ValueError, match="missing required column"):
        ingest_products(source, output, clock=FIXED_CLOCK)


def test_ingest_handles_header_only_file(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "products.csv", "product_id,product_name\n")
    output = tmp_path / "products.parquet"

    ingest_products(source, output, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.num_rows == 0


def test_ingest_is_idempotent_for_a_fixed_clock(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "products.csv", "product_id,product_name\nP001,Wireless Mouse\n")
    output = tmp_path / "products.parquet"

    ingest_products(source, output, clock=FIXED_CLOCK)
    first = pq.read_table(output).to_pydict()
    ingest_products(source, output, clock=FIXED_CLOCK)
    second = pq.read_table(output).to_pydict()

    assert first == second
