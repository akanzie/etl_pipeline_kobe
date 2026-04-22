from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Daily sales fact table with FK validation"
)
@dp.expect_or_fail("valid_month_id", "month_id IS NOT NULL")
@dp.expect_or_fail("valid_store_id", "store_id IS NOT NULL")
@dp.expect_or_fail("valid_product_id", "product_id IS NOT NULL")
@dp.expect_or_fail("valid_classification", "classification IS NOT NULL AND classification IN ('定番', '家庭応援', '特売')")
@dp.expect("valid_quantity", "quantity_sold IS NULL OR quantity_sold >= 0")
@dp.expect("valid_amount", "sales_amount IS NULL OR sales_amount >= 0")
def fact_daily_sales():
    return (
        spark.readStream.table("bronze_sales_raw")
        .withColumn("month_id", F.substring(F.col("month_id"), 1, 7))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "month_id",
            "store_id",
            "product_id",
            "classification",
            "quantity_sold",
            "sales_amount",
            "created_at",
            "updated_at"
        )
    )
