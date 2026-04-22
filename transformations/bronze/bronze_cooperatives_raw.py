from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Raw cooperatives data ingested from cloud storage"
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
