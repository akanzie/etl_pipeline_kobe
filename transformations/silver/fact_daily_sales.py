from pyspark import pipelines as dp
from pyspark.sql import functions as F


def _parse_business_date(column_name: str):
    raw_value = F.trim(F.col(column_name).cast("string"))
    return F.coalesce(
        F.to_date(raw_value),
        F.to_date(raw_value, "yyyy-MM-dd"),
        F.to_date(raw_value, "yyyy/MM/dd"),
        F.to_date(F.concat(raw_value, F.lit("-01")), "yyyy-MM-dd"),
    )


@dp.table(
    comment="Silver - Fact doanh số theo ngày đã chuẩn hóa cho Databricks"
)
@dp.expect_or_drop("no_extreme_outliers", "sales_amount < 1000000")
@dp.expect_or_fail("valid_quantity", "quantity_sold > 0")
@dp.expect_or_fail("valid_sale_date", "sale_date IS NOT NULL")
@dp.expect_or_fail("valid_store_id", "store_id IS NOT NULL")
@dp.expect_or_fail("valid_product_id", "product_id IS NOT NULL")
def fact_daily_sales():
    return (
        spark.readStream.table("bronze_sales_raw")
        .withColumn("sale_date", _parse_business_date("sale_date"))
        .withColumn("month_id", F.date_format(F.col("sale_date"), "yyyy-MM"))
        .withColumn("year", F.year(F.col("sale_date")))
        .withColumn("month", F.month(F.col("sale_date")))
        .withColumn("day", F.dayofmonth(F.col("sale_date")))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active", F.lit(True))
        .select(
            "sale_date",
            "month_id",
            "year",
            "month",
            "day",
            "store_id",
            "product_id",
            "classification",
            "quantity_sold",
            "sales_amount",
            "created_at",
            "updated_at",
            "is_active",
        )
    )

@dp.view(
    comment="Silver - View SCD Type 2 đơn giản cho sản phẩm"
)
def master_products_scd2():
    return (
        spark.read.table("master_products")
        .withColumn("is_current", F.lit(True))
    )
