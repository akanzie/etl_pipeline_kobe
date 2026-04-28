from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master cooperatives with validation"
)
@dp.expect_or_fail("valid_cooperative_id", "cooperative_id IS NOT NULL")
def master_cooperatives():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_cooperatives_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "cooperative_id",
            "cooperative_name",
            "created_at",
            "updated_at"
        )
    )
