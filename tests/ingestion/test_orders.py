from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from de_school.ingestion.orders import ingest_orders

FIXED_CLOCK = lambda: datetime(2024, 1, 1, tzinfo=UTC)  # noqa: E731
KNOWN_CUSTOMER_IDS = {"C001", "C002"}


def write_csv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_ingest_writes_one_row_per_order(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "orders.csv",
        "order_id,customer_id\nO001,C001\nO002,C002\n",
    )
    output = tmp_path / "orders.parquet"

    ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.num_rows == 2
    assert table.column("order_id").to_pylist() == ["O001", "O002"]


def test_ingest_drops_exact_duplicate_rows(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "orders.csv",
        "order_id,customer_id\nO001,C001\nO001,C001\n",
    )
    output = tmp_path / "orders.parquet"

    ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.num_rows == 1


def test_ingest_adds_ingested_at_from_clock(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "orders.csv", "order_id,customer_id\nO001,C001\n")
    output = tmp_path / "orders.parquet"

    ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.column("ingested_at").to_pylist() == [datetime(2024, 1, 1)]


def test_ingest_raises_on_missing_order_id_value(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "orders.csv",
        "order_id,customer_id\nO001,C001\n,C002\n",
    )
    output = tmp_path / "orders.parquet"

    with pytest.raises(ValueError, match="empty 'order_id'"):
        ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)

    assert not output.exists()


def test_ingest_raises_on_missing_order_id_column(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "orders.csv", "customer_id\nC001\n")
    output = tmp_path / "orders.parquet"

    with pytest.raises(ValueError, match="missing required column"):
        ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)


def test_ingest_raises_on_unknown_customer_id(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "orders.csv",
        "order_id,customer_id\nO001,C001\nO002,C999\n",
    )
    output = tmp_path / "orders.parquet"

    with pytest.raises(ValueError, match="not found in customers"):
        ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)

    assert not output.exists()


def test_ingest_handles_header_only_file(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "orders.csv", "order_id,customer_id\n")
    output = tmp_path / "orders.parquet"

    ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)

    table = pq.read_table(output)
    assert table.num_rows == 0


def test_ingest_is_idempotent_for_a_fixed_clock(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "orders.csv", "order_id,customer_id\nO001,C001\n")
    output = tmp_path / "orders.parquet"

    ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)
    first = pq.read_table(output).to_pydict()
    ingest_orders(source, output, known_customer_ids=KNOWN_CUSTOMER_IDS, clock=FIXED_CLOCK)
    second = pq.read_table(output).to_pydict()

    assert first == second
