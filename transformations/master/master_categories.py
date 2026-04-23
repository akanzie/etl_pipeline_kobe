from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Silver - Master categories dimension"
)
@dp.expect_or_fail("valid_category_id", "category_id IS NOT NULL")
@dp.expect_or_fail("valid_category_name", "category_name IS NOT NULL")
def master_categories():
    # Static category mapping
    categories_data = [
        (1, "Gạo"),
        (2, "Dầu ăn"),
        (3, "Thực phẩm"),
    ]
    
    return (
        spark.createDataFrame(categories_data, ["category_id", "category_name"])
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
    )
