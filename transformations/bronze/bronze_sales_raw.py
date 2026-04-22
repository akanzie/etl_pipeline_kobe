from pyspark import pipelines as dp

@dp.table(
    comment="Bronze - Raw sales data ingested from cloud storage"
)
def bronze_sales_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "product_id int, quantity_sold int, sales_amount decimal(14,2)")
        .load("/Volumes/workspace/default/raw_data/sales/")
    )
