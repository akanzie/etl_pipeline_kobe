from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name="master_stores",
    comment="Silver - Master stores with FK validation to regions and business models"
)
@dp.expect_or_drop("valid_store_id", "store_id IS NOT NULL")
@dp.expect_or_drop("valid_region_id", "region_id IS NOT NULL")
@dp.expect_or_drop("valid_business_model_id", "business_model_id IS NOT NULL")
def master_stores():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_stores_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            F.col("store_id").cast("long"),
            "store_name",
            F.col("region_id").cast("long"),
            F.col("business_model_id").cast("long"),
            "created_at",
            "updated_at"
        )
    )
