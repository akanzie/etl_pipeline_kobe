from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master regions with FK validation to cooperatives"
)
@dp.expect_or_fail("valid_region_id", "region_id IS NOT NULL")
@dp.expect_or_fail("valid_region_code", "region_code IS NOT NULL")
@dp.expect_or_fail("valid_cooperative_id", "cooperative_id IS NOT NULL")
def master_regions():
    return (
        spark.readStream.table("bronze_regions_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active",
            F.coalesce(F.col("is_active"), F.lit(True)))
        .select(
            "region_id", "region_code", "region_name", "cooperative_id",
            "is_active", "created_at", "updated_at"
        )
    )
