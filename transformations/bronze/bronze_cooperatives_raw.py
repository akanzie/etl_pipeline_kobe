from pyspark import pipelines as dp

@dp.table(
    name="tmn_kobe.default.bronze_cooperatives_raw",
    comment="Bronze - Dữ liệu hợp tác xã thô được nạp từ vùng landing"
)
def bronze_cooperatives_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "is_active boolean")
        .load("/Volumes/workspace/default/raw_data/cooperatives/")
    )
