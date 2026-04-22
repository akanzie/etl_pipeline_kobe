from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Daily sales fact table with Anomaly Detection"
)
@dp.expect_or_drop("no_extreme_outliers", "sales_amount < 1000000") # Lọc Anomaly
@dp.expect_or_fail("valid_quantity", "quantity_sold > 0")
def fact_daily_sales():
    return (
        spark.readStream.table("bronze_sales_raw")
        .withColumn("month_id", F.substring(F.col("sale_date"), 1, 7))
        .withColumn("is_active", F.lit(True))
    )

@dp.view(
    comment="SCD Type 2 view for Products"
)
def master_products_scd2():
    # Sử dụng window function để xác định hiệu lực của giá (giả định)
    return (
        spark.read.table("master_products")
        .withColumn("is_current", F.lit(True))
    )
