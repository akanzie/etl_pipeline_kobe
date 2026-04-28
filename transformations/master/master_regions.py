from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master regions with FK validation to cooperatives"
)
@dp.expect_or_fail("valid_region_id", "region_id IS NOT NULL")
@dp.expect_or_fail("valid_cooperative_id", "cooperative_id IS NOT NULL")
def master_regions():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_regions_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "region_id",
            "region_name",
            "cooperative_id",
            "created_at",
            "updated_at"
        )
    )
