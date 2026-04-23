from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Dữ liệu lượt khách thô được nạp từ vùng landing"
)
def bronze_customer_count_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "month_id date, customer_count int")
        .load("/Volumes/workspace/default/raw_data/customer_count/")
    )
