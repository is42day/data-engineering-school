"""Main pipeline entry point.

Keep this module small. It should coordinate steps implemented in dedicated modules,
not contain all ingestion and transformation logic itself.
"""

from pathlib import Path

import pyarrow.parquet as pq

from de_school.ingestion.customers import ingest_customers
from de_school.ingestion.order_lines import ingest_order_lines
from de_school.ingestion.orders import ingest_orders
from de_school.ingestion.products import ingest_products

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_id_set(parquet_path: Path, column: str) -> set[str]:
    """Read one column of a raw Parquet file into a set, for FK validation."""
    return set(pq.read_table(parquet_path, columns=[column]).column(column).to_pylist())


def run() -> None:
    """Run the local learning pipeline."""
    customers_path = PROJECT_ROOT / "data" / "raw" / "customers.parquet"
    products_path = PROJECT_ROOT / "data" / "raw" / "products.parquet"
    orders_path = PROJECT_ROOT / "data" / "raw" / "orders.parquet"

    ingest_customers(
        PROJECT_ROOT / "data" / "source" / "customers.csv",
        customers_path,
    )
    ingest_products(
        PROJECT_ROOT / "data" / "source" / "products.csv",
        products_path,
    )
    ingest_orders(
        PROJECT_ROOT / "data" / "source" / "orders.csv",
        orders_path,
        known_customer_ids=_read_id_set(customers_path, "customer_id"),
    )
    ingest_order_lines(
        PROJECT_ROOT / "data" / "source" / "order_lines.csv",
        PROJECT_ROOT / "data" / "raw" / "order_lines.parquet",
        known_order_ids=_read_id_set(orders_path, "order_id"),
        known_product_ids=_read_id_set(products_path, "product_id"),
    )


if __name__ == "__main__":
    run()
