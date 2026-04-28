from pyspark import pipelines as dp
from pyspark.sql import functions as F


DATE_COLUMN_CANDIDATES = (
    "sale_date",
    "date",
    "business_date",
    "month_id",
)


def _resolve_date_column(columns: list[str]) -> str:
    for column_name in DATE_COLUMN_CANDIDATES:
        if column_name in columns:
            return column_name
    raise ValueError(
        "Không tìm thấy cột ngày cho bronze_sales_raw. "
        "Cần một trong các cột: sale_date, date, business_date hoặc month_id."
    )


def _parse_business_date(column_name: str):
    raw_value = F.trim(F.col(column_name).cast("string"))
    return F.coalesce(
        F.to_date(raw_value),
        F.to_date(raw_value, "yyyy-MM-dd"),
        F.to_date(raw_value, "yyyy/MM/dd"),
        F.to_date(raw_value, "yyyyMMdd"),
        F.to_date(F.concat(raw_value, F.lit("-01")), "yyyy-MM-dd"),
        F.to_date(F.concat(raw_value, F.lit("/01")), "yyyy/MM/dd"),
    )


@dp.table(
    name="tmn_kobe.fact.fact_daily_sales",
    comment="Silver - Fact doanh số theo ngày đã chuẩn hóa"
)
@dp.expect_or_drop("no_extreme_outliers", "sales_amount < 1000000")
@dp.expect_or_fail("valid_quantity", "quantity_sold > 0")
@dp.expect_or_fail("valid_sale_date", "sale_date IS NOT NULL")
@dp.expect_or_fail("valid_store_id", "store_id IS NOT NULL")
@dp.expect_or_fail("valid_product_id", "product_id IS NOT NULL")
def fact_daily_sales():
    raw_sales = spark.readStream.table("tmn_kobe.default.bronze_sales_raw")
    source_date_column = _resolve_date_column(raw_sales.columns)

    return (
        raw_sales
        .filter(F.col(source_date_column).isNotNull())
        .filter(F.trim(F.col(source_date_column).cast("string")) != "")
        # Cast store_id và product_id sang long, filter out giá trị NULL (không hợp lệ)
        .withColumn("store_id_long", F.expr("try_cast(store_id as long)"))
        .withColumn("product_id_long", F.expr("try_cast(product_id as long)"))
        .filter(F.col("store_id_long").isNotNull())
        .filter(F.col("product_id_long").isNotNull())
        .withColumn("sale_date", _parse_business_date(source_date_column))
        .withColumn("year", F.year(F.col("sale_date")))
        .withColumn("month", F.month(F.col("sale_date")))
        .withColumn("day", F.dayofmonth(F.col("sale_date")))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active", F.lit(True))
        .select(
            "sale_date",
            "year",
            "month",
            "day",
            F.col("store_id_long").alias("store_id"),
            F.col("product_id_long").alias("product_id"),
            "classification",
            "quantity_sold",
            "sales_amount",
            "created_at",
            "updated_at",
            "is_active",
        )
    )

@dp.view(
    comment="Silver - View SCD Type 2 đơn giản cho sản phẩm"
)
def master_products_scd2():
    return (
        spark.readStream.table("tmn_kobe.default.bronze_products_raw")
        .select(
            "product_id",
            "product_name",
            "category",
        )
        .withColumn("is_current", F.lit(True))
    )
