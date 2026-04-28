from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.fact.fact_daily_customer_count"
KEY_COLUMNS = ("sale_date", "store_id")
DATE_COLUMN_CANDIDATES = (
    "date",
    "sale_date",
    "customer_date",
    "count_date",
    "business_date",
)


def _resolve_date_column(columns: list[str]) -> str:
    for column_name in DATE_COLUMN_CANDIDATES:
        if column_name in columns:
            return column_name
    raise ValueError(
        "Không tìm thấy cột thời gian cho bronze_customer_count_raw. "
        "Cần một trong các cột: customer_date, count_date, business_date, "
        "sale_date hoặc date."
    )


def _parse_business_date(column_name: str):
    raw_value = F.trim(F.col(column_name).cast("string"))
    return F.coalesce(
        F.to_date(raw_value),
        F.to_date(raw_value, "yyyy-MM-dd"),
        F.to_date(raw_value, "yyyy/MM/dd"),
        F.to_date(raw_value, "yyyyMMdd"),
        F.to_date(F.concat(raw_value, F.lit("-01")), "yyyy-MM-dd"),
        F.to_date(F.concat(raw_value, F.lit("/01")), "yyyy/MM/dd"),
    )


def build_fact_daily_customer_count_dataframe(spark):
    raw_customer_count = spark.read.table("tmn_kobe.default.bronze_customer_count_raw")
    source_date_column = _resolve_date_column(raw_customer_count.columns)

    return (
        raw_customer_count
        .filter(F.col(source_date_column).isNotNull())
        .filter(F.trim(F.col(source_date_column).cast("string")) != "")
        .withColumn("store_id_long", F.expr("try_cast(store_id as long)"))
        .withColumn("sale_date", _parse_business_date(source_date_column))
        .filter(F.col("sale_date").isNotNull())
        .filter(F.col("store_id_long").isNotNull())
        .filter((F.col("customer_count").isNull()) | (F.col("customer_count") >= 0))
        .withColumn("year", F.year(F.col("sale_date")))
        .withColumn("month", F.month(F.col("sale_date")))
        .withColumn("day", F.dayofmonth(F.col("sale_date")))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "sale_date",
            "year",
            "month",
            "day",
            F.col("store_id_long").alias("store_id"),
            F.col("customer_count").cast("int").alias("customer_count"),
            "created_at",
            "updated_at",
        )
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_fact_daily_customer_count_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
