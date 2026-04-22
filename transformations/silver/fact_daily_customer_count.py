from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Daily customer count fact table with FK validation"
)
@dp.expect_or_fail("valid_month_id", "month_id IS NOT NULL")
@dp.expect_or_fail("valid_store_id", "store_id IS NOT NULL")
@dp.expect("valid_customer_count", "customer_count IS NULL OR customer_count >= 0")
def fact_daily_customer_count():
    return (
        spark.readStream.table("bronze_customer_count_raw")
        .withColumn("month_id", F.substring(F.col("month_id"), 1, 7))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "month_id",
            "store_id",
            "customer_count",
            "created_at",
            "updated_at"
        )
    )
