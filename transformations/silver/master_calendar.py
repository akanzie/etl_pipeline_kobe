from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master calendar dimension with validation"
)
@dp.expect_or_fail("valid_month_id", "month_id IS NOT NULL AND month_id RLIKE '^[0-9]{4}-[0-9]{2}$'")
@dp.expect_or_fail("valid_year", "year IS NOT NULL")
@dp.expect_or_fail("valid_month_num", "month_num IS NOT NULL AND month_num BETWEEN 1 AND 12")
@dp.expect("valid_quarter", "quarter IS NULL OR quarter BETWEEN 1 AND 4")
def master_calendar():
    return (
        spark.readStream.table("bronze_calendar_raw")
        .withColumn("month_id", F.substring(F.col("month_id"), 1, 7))
        .withColumn("is_closed",
            F.coalesce(F.col("is_closed"), F.lit(False)))
        .select(
            "month_id", "year", "month_num", "quarter", 
            "fiscal_year", "is_closed"
        )
    )
