from pyspark import pipelines as dp

@dp.table(
    name="tmn_kobe.default.bronze_products_raw",
    comment="Bronze - Dữ liệu sản phẩm thô được nạp từ vùng landing"
)
def bronze_products_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaHints", "product_id int, price decimal(10,2), is_active boolean")
        .load("/Volumes/workspace/default/raw_data/products/")
    )
