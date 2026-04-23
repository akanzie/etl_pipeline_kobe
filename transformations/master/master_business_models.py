from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master business models with validation"
)
@dp.expect_or_fail("valid_business_model_id", "business_model_id IS NOT NULL")
def master_business_models():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_business_models_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "business_model_id",
            "business_model_name",
            "created_at",
            "updated_at"
        )
    )
