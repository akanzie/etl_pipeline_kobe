from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master products with validation"
)
@dp.expect_or_fail("valid_product_id", "product_id IS NOT NULL")
def master_products():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_products_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "product_id",
            "product_name",
            "category",
            "created_at",
            "updated_at"
        )
    )
