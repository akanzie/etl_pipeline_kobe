from pyspark import pipelines as dp
from pyspark.sql import functions as F


def _normalize_category_name():
    return F.when(
        F.trim(F.coalesce(F.col("category"), F.lit(""))) == F.lit(""),
        F.lit("UNKNOWN"),
    ).otherwise(F.trim(F.col("category")))


def _build_category_id(column):
    return F.pmod(F.xxhash64(column), F.lit(2147483647)).cast("int")


@dp.materialized_view(
    comment="Silver - Master danh mục sản phẩm suy ra từ master_products"
)
def master_categories():
    normalized_categories = (
        spark.read.table("master_products")
        .withColumn("category_name", _normalize_category_name())
        .select("category_name")
        .dropDuplicates()
    )

    return (
        normalized_categories
        .withColumn("category_id", _build_category_id(F.col("category_name")))
        .withColumn("is_active", F.lit(True))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "category_id",
            "category_name",
            "is_active",
            "created_at",
            "updated_at",
        )
    )
