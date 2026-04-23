from pyspark import pipelines as dp

@dp.table(
    name="tmn_kobe.default.bronze_sales_raw",
    comment="Bronze - Dữ liệu bán hàng thô được nạp từ vùng landing"
)
def bronze_sales_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option(
            "cloudFiles.schemaHints",
            "sale_date date, product_id int, quantity_sold int, sales_amount decimal(14,2)",
        )
        .load("/Volumes/workspace/default/raw_data/sales/")
    )
