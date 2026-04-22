from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Raw regions data ingested from cloud storage"
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
