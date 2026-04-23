from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="tmn_kobe.master.products",
    comment="Silver - Master sản phẩm đã chuẩn hóa"
)
@dp.expect_or_fail("valid_product_id", "product_id IS NOT NULL")
@dp.expect_or_fail("valid_product_name", "product_name IS NOT NULL")
@dp.expect("valid_price", "price IS NULL OR price >= 0")
def master_products():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_products_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active",
            F.coalesce(F.col("is_active"), F.lit(True)))
        .select(
            "product_id", "product_name", "category", "unit", "price",
            "is_active", "created_at", "updated_at"
        )
    )
