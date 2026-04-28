from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="master_regions",
    comment="Silver - Master regions with FK validation to cooperatives"
)
@dp.expect_or_drop("valid_region_id", "region_id IS NOT NULL")
@dp.expect_or_drop("valid_cooperative_id", "cooperative_id IS NOT NULL")
def master_regions():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_regions_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            F.col("region_id").cast("long"),
            "region_name",
            F.col("cooperative_id").cast("long"),
            "created_at",
            "updated_at"
        )
    )
