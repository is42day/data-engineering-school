from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from de_school.ingestion.order_lines import ingest_order_lines

FIXED_CLOCK = lambda: datetime(2024, 1, 1, tzinfo=UTC)  # noqa: E731
KNOWN_ORDER_IDS = {"O001", "O002"}
KNOWN_PRODUCT_IDS = {"P001", "P002"}


def write_csv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_ingest_writes_one_row_per_line_item(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv",
        "order_id,line_number,product_id\nO001,1,P001\nO001,2,P002\n",
    )
    output = tmp_path / "order_lines.parquet"

    ingest_order_lines(
        source,
        output,
        known_order_ids=KNOWN_ORDER_IDS,
        known_product_ids=KNOWN_PRODUCT_IDS,
        clock=FIXED_CLOCK,
    )

    table = pq.read_table(output)
    assert table.num_rows == 2
    assert table.column("line_number").to_pylist() == ["1", "2"]


def test_ingest_drops_exact_duplicate_rows_for_same_key(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv",
        "order_id,line_number,product_id\nO001,1,P001\nO001,1,P001\n",
    )
    output = tmp_path / "order_lines.parquet"

    ingest_order_lines(
        source,
        output,
        known_order_ids=KNOWN_ORDER_IDS,
        known_product_ids=KNOWN_PRODUCT_IDS,
        clock=FIXED_CLOCK,
    )

    table = pq.read_table(output)
    assert table.num_rows == 1


def test_ingest_raises_on_conflicting_rows_for_same_key(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv",
        "order_id,line_number,product_id\nO001,1,P001\nO001,1,P002\n",
    )
    output = tmp_path / "order_lines.parquet"

    with pytest.raises(ValueError, match="conflicting rows"):
        ingest_order_lines(
            source,
            output,
            known_order_ids=KNOWN_ORDER_IDS,
            known_product_ids=KNOWN_PRODUCT_IDS,
            clock=FIXED_CLOCK,
        )

    assert not output.exists()


def test_ingest_adds_ingested_at_from_clock(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv", "order_id,line_number,product_id\nO001,1,P001\n"
    )
    output = tmp_path / "order_lines.parquet"

    ingest_order_lines(
        source,
        output,
        known_order_ids=KNOWN_ORDER_IDS,
        known_product_ids=KNOWN_PRODUCT_IDS,
        clock=FIXED_CLOCK,
    )

    table = pq.read_table(output)
    assert table.column("ingested_at").to_pylist() == [datetime(2024, 1, 1)]


def test_ingest_raises_on_missing_key_value(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv",
        "order_id,line_number,product_id\nO001,1,P001\nO001,,P002\n",
    )
    output = tmp_path / "order_lines.parquet"

    with pytest.raises(ValueError, match="empty"):
        ingest_order_lines(
            source,
            output,
            known_order_ids=KNOWN_ORDER_IDS,
            known_product_ids=KNOWN_PRODUCT_IDS,
            clock=FIXED_CLOCK,
        )

    assert not output.exists()


def test_ingest_raises_on_missing_required_column(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "order_lines.csv", "order_id,product_id\nO001,P001\n")
    output = tmp_path / "order_lines.parquet"

    with pytest.raises(ValueError, match="missing required column"):
        ingest_order_lines(
            source,
            output,
            known_order_ids=KNOWN_ORDER_IDS,
            known_product_ids=KNOWN_PRODUCT_IDS,
            clock=FIXED_CLOCK,
        )


def test_ingest_raises_on_unknown_order_id(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv",
        "order_id,line_number,product_id\nO999,1,P001\n",
    )
    output = tmp_path / "order_lines.parquet"

    with pytest.raises(ValueError, match="not found in orders"):
        ingest_order_lines(
            source,
            output,
            known_order_ids=KNOWN_ORDER_IDS,
            known_product_ids=KNOWN_PRODUCT_IDS,
            clock=FIXED_CLOCK,
        )

    assert not output.exists()


def test_ingest_raises_on_unknown_product_id(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv",
        "order_id,line_number,product_id\nO001,1,P999\n",
    )
    output = tmp_path / "order_lines.parquet"

    with pytest.raises(ValueError, match="not found in products"):
        ingest_order_lines(
            source,
            output,
            known_order_ids=KNOWN_ORDER_IDS,
            known_product_ids=KNOWN_PRODUCT_IDS,
            clock=FIXED_CLOCK,
        )

    assert not output.exists()


def test_ingest_handles_header_only_file(tmp_path: Path) -> None:
    source = write_csv(tmp_path / "order_lines.csv", "order_id,line_number,product_id\n")
    output = tmp_path / "order_lines.parquet"

    ingest_order_lines(
        source,
        output,
        known_order_ids=KNOWN_ORDER_IDS,
        known_product_ids=KNOWN_PRODUCT_IDS,
        clock=FIXED_CLOCK,
    )

    table = pq.read_table(output)
    assert table.num_rows == 0


def test_ingest_is_idempotent_for_a_fixed_clock(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "order_lines.csv", "order_id,line_number,product_id\nO001,1,P001\n"
    )
    output = tmp_path / "order_lines.parquet"

    ingest_order_lines(
        source,
        output,
        known_order_ids=KNOWN_ORDER_IDS,
        known_product_ids=KNOWN_PRODUCT_IDS,
        clock=FIXED_CLOCK,
    )
    first = pq.read_table(output).to_pydict()
    ingest_order_lines(
        source,
        output,
        known_order_ids=KNOWN_ORDER_IDS,
        known_product_ids=KNOWN_PRODUCT_IDS,
        clock=FIXED_CLOCK,
    )
    second = pq.read_table(output).to_pydict()

    assert first == second
