from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.master.master_stores"
KEY_COLUMNS = ("store_id",)


def build_master_stores_dataframe(spark):
    return (
        spark.read.table("tmn_kobe.default.bronze_stores_raw")
        .filter(F.col("store_id").isNotNull())
        .filter(F.col("region_id").isNotNull())
        .filter(F.col("business_model_id").isNotNull())
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            F.col("store_id").cast("long").alias("store_id"),
            "store_name",
            F.col("region_id").cast("long").alias("region_id"),
            F.col("business_model_id").cast("long").alias("business_model_id"),
            "created_at",
            "updated_at",
        )
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_master_stores_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
