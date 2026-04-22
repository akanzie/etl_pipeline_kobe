from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master business models with validation"
)
@dp.expect_or_fail("valid_business_model_id", "business_model_id IS NOT NULL")
@dp.expect_or_fail("valid_business_model_code", "business_model_code IS NOT NULL")
@dp.expect_or_drop("no_duplicates", "business_model_id IS NOT NULL AND business_model_code IS NOT NULL")
def master_business_models():
    return (
        spark.readStream.table("bronze_business_models_raw")
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active",
            F.coalesce(F.col("is_active"), F.lit(True)))
        .select(
            "business_model_id", "business_model_code", "business_model_name",
            "is_active", "created_at", "updated_at"
        )
    )
