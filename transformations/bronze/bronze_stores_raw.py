from pyspark import pipelines as dp

@dp.table(
    name="tmn_kobe.default.bronze_stores_raw",
    comment="Bronze - Dữ liệu cửa hàng thô được nạp từ vùng landing"
)
def bronze_stores_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "opening_date date")
        .load("/Volumes/workspace/default/raw_data/stores/")
    )
