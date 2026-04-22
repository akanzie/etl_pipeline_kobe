from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master stores with FK validation to regions and business models"
)
@dp.expect_or_fail("valid_store_id", "store_id IS NOT NULL")
@dp.expect_or_fail("valid_store_code", "store_code IS NOT NULL")
@dp.expect_or_fail("valid_region_id", "region_id IS NOT NULL")
@dp.expect_or_fail("valid_business_model_id", "business_model_id IS NOT NULL")
def master_stores():
    return (
        spark.readStream.table("bronze_stores_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("status",
            F.coalesce(F.col("status"), F.lit("active")))
        .select(
            "store_id", "store_code", "store_name", "region_id", 
            "business_model_id", "province", "status", "opening_date",
            "created_at", "updated_at"
        )
    )
