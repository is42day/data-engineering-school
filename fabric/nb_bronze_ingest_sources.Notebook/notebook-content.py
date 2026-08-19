# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "e22cf5be-75c8-44cb-82f7-9add0c2de5d8",
# META       "default_lakehouse_name": "lh_de_school_dev",
# META       "default_lakehouse_workspace_id": "c6eb89fe-5607-4b68-bfec-3398fa634743",
# META       "known_lakehouses": [
# META         {
# META           "id": "e22cf5be-75c8-44cb-82f7-9add0c2de5d8"
# META         }
# META       ]
# META     },
# META     "environment": {
# META       "environmentId": "5205f40a-bd57-a841-46db-27b74e2cf7f2",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# CELL ********************

import uuid
from datetime import datetime, timezone

from pyspark.sql import functions as F

RUN_ID = str(uuid.uuid4())
INGESTED_AT = datetime.now(timezone.utc)

SOURCE_FILES = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_lines": "order_lines.csv",
}

for table_name, filename in SOURCE_FILES.items():
    raw_df = spark.read.option("header", True).csv(f"Files/{filename}")

    bronze_df = (
        raw_df
        .withColumn("_ingested_at", F.lit(INGESTED_AT))
        .withColumn("_source_name", F.lit(filename))
        .withColumn("_batch_id", F.lit(RUN_ID))
    )

    bronze_df.write.format("delta").mode("overwrite").saveAsTable(f"bronze_{table_name}")
    print(f"bronze_{table_name}: {bronze_df.count()} rows")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
