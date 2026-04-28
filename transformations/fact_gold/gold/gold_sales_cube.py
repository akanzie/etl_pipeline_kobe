from __future__ import annotations

from pyspark.sql import functions as F

from transformations.upsert_utils import merge_dataframe


TARGET_TABLE = "tmn_kobe.fact.gold_sales_cube"
KEY_COLUMNS = (
    "date",
    "cooperative_id",
    "region_id",
    "business_model_id",
    "category_id",
    "store_id",
    "product_id",
)


def _normalize_category_name():
    return F.when(
        F.trim(F.coalesce(F.col("products.category"), F.lit(""))) == F.lit(""),
        F.lit("UNKNOWN"),
    ).otherwise(F.trim(F.col("products.category")))


def _build_week_key(date_column):
    return F.concat(
        F.date_format(date_column, "yyyy"),
        F.lit("W"),
        F.lpad(F.weekofyear(date_column).cast("string"), 2, "0"),
    )


def build_gold_sales_cube_dataframe(spark):
    sales = spark.read.table("tmn_kobe.fact.fact_daily_sales").alias("sales")
    stores = spark.read.table("tmn_kobe.master.master_stores").alias("stores")
    regions = spark.read.table("tmn_kobe.master.master_regions").alias("regions")
    products = spark.read.table("tmn_kobe.master.master_products").alias("products")
    categories = spark.read.table("tmn_kobe.master.master_categories").alias("categories")

    sales_enriched = (
        sales
        .join(stores, F.col("sales.store_id") == F.col("stores.store_id"), "inner")
        .join(regions, F.col("stores.region_id") == F.col("regions.region_id"), "inner")
        .join(products, F.col("sales.product_id") == F.col("products.product_id"), "inner")
        .join(
            categories,
            _normalize_category_name() == F.col("categories.category_name"),
            "inner",
        )
        .select(
            F.date_format(F.col("sales.sale_date"), "yyyy-MM-dd").alias("date"),
            F.col("regions.cooperative_id").alias("cooperative_id"),
            F.col("stores.region_id").alias("region_id"),
            F.col("stores.business_model_id").alias("business_model_id"),
            F.col("categories.category_id").alias("category_id"),
            F.col("sales.store_id").alias("store_id"),
            F.col("sales.product_id").alias("product_id"),
            _build_week_key(F.col("sales.sale_date")).alias("week"),
            F.date_format(F.col("sales.sale_date"), "yyyy-MM").alias("month"),
            F.col("sales.quantity_sold").alias("quantity_sold"),
            F.col("sales.sales_amount").alias("sales_amount"),
        )
    )

    return (
        sales_enriched
        .groupBy(
            "date",
            "cooperative_id",
            "region_id",
            "business_model_id",
            "category_id",
            "store_id",
            "product_id",
            "week",
            "month",
        )
        .agg(
            F.sum("sales_amount").cast("double").alias("total_amt"),
            F.sum("quantity_sold").cast("int").alias("total_qty"),
        )
        .select(
            "date",
            "cooperative_id",
            "region_id",
            "business_model_id",
            "category_id",
            "store_id",
            "product_id",
            "week",
            "month",
            "total_amt",
            "total_qty",
        )
    )


def run(spark) -> None:
    merge_dataframe(
        spark,
        build_gold_sales_cube_dataframe(spark),
        target_table=TARGET_TABLE,
        key_columns=KEY_COLUMNS,
    )
