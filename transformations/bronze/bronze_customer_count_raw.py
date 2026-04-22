from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Raw customer count data ingested from cloud storage"
)
def bronze_customer_count_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "customer_count int")
        .load("/Volumes/workspace/default/raw_data/customer_count/")
    )
