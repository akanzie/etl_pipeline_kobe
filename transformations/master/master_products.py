from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.master.master_products"
KEY_COLUMNS = ("product_id",)


def build_master_products_dataframe(spark):
    return (
        spark.read.table("tmn_kobe.default.bronze_products_raw")
        .filter(F.col("product_id").isNotNull())
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            F.col("product_id").cast("long").alias("product_id"),
            "product_name",
            "category",
            "created_at",
            "updated_at",
        )
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_master_products_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
