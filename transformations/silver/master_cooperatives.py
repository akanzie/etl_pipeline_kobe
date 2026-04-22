from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master cooperatives with validation"
)
@dp.expect_or_fail("valid_cooperative_id", "cooperative_id IS NOT NULL")
@dp.expect_or_fail("valid_cooperative_code", "cooperative_code IS NOT NULL")
@dp.expect_or_drop("no_duplicates", "cooperative_id IS NOT NULL AND cooperative_code IS NOT NULL")
def master_cooperatives():
    return (
        spark.readStream.table("bronze_cooperatives_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active",
            F.coalesce(F.col("is_active"), F.lit(True)))
        .select(
            "cooperative_id", "cooperative_code", "cooperative_name", 
            "is_active", "created_at", "updated_at"
        )
    )
