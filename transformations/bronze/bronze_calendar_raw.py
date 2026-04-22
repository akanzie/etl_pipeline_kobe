from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Raw calendar data ingested from cloud storage"
)
def bronze_calendar_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "month_id string, year int, month_num int, quarter int, fiscal_year int, is_closed boolean")
        .load("/Volumes/workspace/default/raw_data/calendar/")
    )
