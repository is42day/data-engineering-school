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

from pyspark.sql import Row

# --- write: minimal non-sensitive fictional data ---
df = spark.createDataFrame(
    [Row(id=1, label="fabric_connectivity_ok"), Row(id=2, label="fabric_connectivity_ok")]
)
df.write.format("delta").mode("overwrite").saveAsTable("_smoketest")

# --- read back ---
result = spark.read.table("_smoketest")
result.show()
assert result.count() == 2, "round-trip write/read failed"
print("Lakehouse + environment connectivity OK")

# --- clean up ---
spark.sql("DROP TABLE IF EXISTS _smoketest")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
