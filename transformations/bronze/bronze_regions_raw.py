from pyspark import pipelines as dp

@dp.table(
    name="tmn_kobe.default.bronze_regions_raw",
    comment="Bronze - Dữ liệu khu vực thô được nạp từ vùng landing"
)
def bronze_regions_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "is_active boolean")
        .load("/Volumes/workspace/default/raw_data/regions/")
    )
