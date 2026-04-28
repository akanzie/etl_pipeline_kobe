from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.fact.fact_daily_sales"
KEY_COLUMNS = ("sale_date", "store_id", "product_id", "classification")
DATE_COLUMN_CANDIDATES = (
    "sale_date",
    "date",
    "business_date",
    "month_id",
)


def _resolve_date_column(columns: list[str]) -> str:
    for column_name in DATE_COLUMN_CANDIDATES:
        if column_name in columns:
            return column_name
    raise ValueError(
        "Không tìm thấy cột ngày cho bronze_sales_raw. "
        "Cần một trong các cột: sale_date, date, business_date hoặc month_id."
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


def build_fact_daily_sales_dataframe(spark):
    raw_sales = spark.read.table("tmn_kobe.default.bronze_sales_raw")
    source_date_column = _resolve_date_column(raw_sales.columns)

    return (
        raw_sales
        .filter(F.col(source_date_column).isNotNull())
        .filter(F.trim(F.col(source_date_column).cast("string")) != "")
        .withColumn("store_id_long", F.expr("try_cast(store_id as long)"))
        .withColumn("product_id_long", F.expr("try_cast(product_id as long)"))
        .filter(F.col("store_id_long").isNotNull())
        .filter(F.col("product_id_long").isNotNull())
        .withColumn("sale_date", _parse_business_date(source_date_column))
        .filter(F.col("sale_date").isNotNull())
        .filter(F.col("sales_amount") < 1000000)
        .filter(F.col("quantity_sold") > 0)
        .withColumn("year", F.year(F.col("sale_date")))
        .withColumn("month", F.month(F.col("sale_date")))
        .withColumn("day", F.dayofmonth(F.col("sale_date")))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active", F.lit(True))
        .select(
            "sale_date",
            "year",
            "month",
            "day",
            F.col("store_id_long").alias("store_id"),
            F.col("product_id_long").alias("product_id"),
            "classification",
            "quantity_sold",
            "sales_amount",
            "created_at",
            "updated_at",
            "is_active",
        )
    )


def build_master_products_scd2_dataframe(spark):
    return (
        spark.read.table("tmn_kobe.default.bronze_products_raw")
        .select(
            "product_id",
            "product_name",
            "category",
        )
        .withColumn("is_current", F.lit(True))
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_fact_daily_sales_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
