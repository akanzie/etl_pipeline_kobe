from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Raw stores data ingested from cloud storage"
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
