from pyspark import pipelines as dp

@dp.table(
    name="bronze_categories_raw",
    comment="Bronze - Dữ liệu categories thô được nạp từ vùng landing"
)
def bronze_categories_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option(
            "cloudFiles.schemaHints",
            "category_id int, category_name string",
        )
        .load("/Volumes/workspace/default/raw_data/categories/")
    )
