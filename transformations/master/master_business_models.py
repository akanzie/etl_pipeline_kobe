from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.master.master_business_models"
KEY_COLUMNS = ("business_model_id",)


def build_master_business_models_dataframe(spark):
    return (
        spark.read.table("tmn_kobe.default.bronze_business_models_raw")
        .filter(F.col("business_model_id").isNotNull())
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            F.col("business_model_id").cast("long").alias("business_model_id"),
            "business_model_name",
            "created_at",
            "updated_at",
        )
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_master_business_models_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
