"""Main pipeline entry point.

Keep this module small. It should coordinate steps implemented in dedicated modules,
not contain all ingestion and transformation logic itself.
"""

from pathlib import Path

from de_school.ingestion.customers import ingest_customers

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run() -> None:
    """Run the local learning pipeline."""
    ingest_customers(
        PROJECT_ROOT / "data" / "source" / "customers.csv",
        PROJECT_ROOT / "data" / "raw" / "customers.parquet",
    )


if __name__ == "__main__":
    run()
