from pyspark import pipelines as dp
from pyspark.sql import functions as F


def _safe_divide(numerator, denominator):
    return F.when(
        denominator.isNull() | (denominator == F.lit(0)),
        F.lit(None).cast("decimal(18,2)"),
    ).otherwise((numerator / denominator).cast("decimal(18,2)"))


@dp.materialized_view(
    comment="Gold - Cube doanh số theo ngày phục vụ Databricks SQL",
    cluster_by=["year", "month", "day", "cooperative_id", "region_id", "business_model_id"]
)
def gold_sales_cube():
    sales = spark.read.table("fact_daily_sales").alias("sales")
    stores = spark.read.table("master_stores").alias("stores")
    regions = spark.read.table("master_regions").alias("regions")
    products = spark.read.table("master_products").alias("products")
    customer_count = spark.read.table("fact_daily_customer_count").alias("customer_count")

    sales_enriched = (
        sales
        .join(stores, F.col("sales.store_id") == F.col("stores.store_id"), "inner")
        .join(regions, F.col("stores.region_id") == F.col("regions.region_id"), "inner")
        .join(products, F.col("sales.product_id") == F.col("products.product_id"), "inner")
        .join(
            customer_count,
            (F.col("sales.store_id") == F.col("customer_count.store_id"))
            & (F.col("sales.sale_date") == F.col("customer_count.customer_date")),
            "left",
        )
        .select(
            F.col("sales.sale_date").alias("sale_date"),
            F.col("sales.month_id").alias("month_id"),
            F.col("sales.year").alias("year"),
            F.col("sales.month").alias("month"),
            F.col("sales.day").alias("day"),
            F.col("regions.cooperative_id").alias("cooperative_id"),
            F.col("stores.region_id").alias("region_id"),
            F.col("stores.business_model_id").alias("business_model_id"),
            F.coalesce(F.col("products.category"), F.lit("")).alias("category"),
            F.col("sales.store_id").alias("store_id"),
            F.col("sales.product_id").alias("product_id"),
            F.col("sales.classification").alias("classification"),
            F.col("sales.quantity_sold").alias("quantity_sold"),
            F.col("sales.sales_amount").alias("sales_amount"),
            F.col("customer_count.customer_count").alias("customer_count"),
        )
    )

    aggregated = (
        sales_enriched
        .groupBy(
            "sale_date",
            "month_id",
            "year",
            "month",
            "day",
            "cooperative_id",
            "region_id",
            "business_model_id",
            "category",
            "store_id",
            "product_id",
            "classification",
        )
        .agg(
            F.sum("quantity_sold").cast("decimal(18,2)").alias("total_qty"),
            F.sum("sales_amount").cast("decimal(18,2)").alias("total_amt"),
            F.max("customer_count").cast("decimal(18,2)").alias("customer_count"),
        )
    )

    cube = (
        aggregated
        .withColumn("avg_unit_price", _safe_divide(F.col("total_amt"), F.col("total_qty")))
        .withColumn("qty_pi", _safe_divide(F.col("total_qty"), F.col("customer_count")))
        .withColumn("amt_pi", _safe_divide(F.col("total_amt"), F.col("customer_count")))
        .withColumn("markdown_qty", F.lit(0).cast("decimal(18,2)"))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
    )

    return cube.select(
        "sale_date",
        "month_id",
        "year",
        "month",
        "day",
        "cooperative_id",
        "region_id",
        "business_model_id",
        "category",
        "store_id",
        "product_id",
        "classification",
        "total_qty",
        "total_amt",
        "customer_count",
        "avg_unit_price",
        "qty_pi",
        "amt_pi",
        "markdown_qty",
        "created_at",
        "updated_at",
    )
