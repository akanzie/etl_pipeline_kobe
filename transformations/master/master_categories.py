from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="master_categories",
    comment="Silver - Master categories dimension"
)
@dp.expect_or_fail("valid_category_id", "category_id IS NOT NULL")
@dp.expect_or_fail("valid_category_name", "category_name IS NOT NULL")
def master_categories():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_categories_raw")
        .select(
            F.col("category_id").cast("long"),
            "category_name",
        )
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
    )
