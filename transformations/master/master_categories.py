from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.master.master_categories"
KEY_COLUMNS = ("category_id",)


def build_master_categories_dataframe(spark):
    return (
        spark.read.table("tmn_kobe.default.bronze_categories_raw")
        .filter(F.col("category_id").isNotNull())
        .filter(F.col("category_name").isNotNull())
        .select(
            F.col("category_id").cast("long").alias("category_id"),
            "category_name",
        )
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_master_categories_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
