"""Main pipeline entry point.

Keep this module small. It should coordinate steps implemented in dedicated modules,
not contain all ingestion and transformation logic itself.
"""

from pathlib import Path

import pyarrow.parquet as pq

from de_school.ingestion.customers import ingest_customers
from de_school.ingestion.orders import ingest_orders
from de_school.ingestion.products import ingest_products

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_id_set(parquet_path: Path, column: str) -> set[str]:
    """Read one column of a raw Parquet file into a set, for FK validation."""
    return set(pq.read_table(parquet_path, columns=[column]).column(column).to_pylist())


def run() -> None:
    """Run the local learning pipeline."""
    customers_path = PROJECT_ROOT / "data" / "raw" / "customers.parquet"

    ingest_customers(
        PROJECT_ROOT / "data" / "source" / "customers.csv",
        customers_path,
    )
    ingest_products(
        PROJECT_ROOT / "data" / "source" / "products.csv",
        PROJECT_ROOT / "data" / "raw" / "products.parquet",
    )
    ingest_orders(
        PROJECT_ROOT / "data" / "source" / "orders.csv",
        PROJECT_ROOT / "data" / "raw" / "orders.parquet",
        known_customer_ids=_read_id_set(customers_path, "customer_id"),
    )


if __name__ == "__main__":
    run()
