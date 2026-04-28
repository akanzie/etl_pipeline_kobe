from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.master.master_regions"
KEY_COLUMNS = ("region_id",)


def build_master_regions_dataframe(spark):
    return (
        spark.read.table("tmn_kobe.default.bronze_regions_raw")
        .filter(F.col("region_id").isNotNull())
        .filter(F.col("cooperative_id").isNotNull())
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            F.col("region_id").cast("long").alias("region_id"),
            "region_name",
            F.col("cooperative_id").cast("long").alias("cooperative_id"),
            "created_at",
            "updated_at",
        )
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_master_regions_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
