from pyspark import pipelines as dp
from pyspark.sql import functions as F


DATE_COLUMN_CANDIDATES = (
    "date",
    "sale_date",
    "customer_date",
    "count_date",
    "business_date",
)


def _resolve_date_column(columns: list[str]) -> str:
    for column_name in DATE_COLUMN_CANDIDATES:
        if column_name in columns:
            return column_name
    raise ValueError(
        "Không tìm thấy cột thời gian cho bronze_customer_count_raw. "
        "Cần một trong các cột: customer_date, count_date, business_date, "
        "sale_date hoặc date."
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
    name="tmn_kobe.fact.fact_daily_customer_count",
    comment="Silver - Fact lượt khách theo ngày đã chuẩn hóa"
)
@dp.expect_or_fail("valid_sale_date", "sale_date IS NOT NULL")
@dp.expect_or_fail("valid_store_id", "store_id IS NOT NULL")
@dp.expect("valid_customer_count", "customer_count IS NULL OR customer_count >= 0")
def fact_daily_customer_count():
    raw_customer_count = spark.readStream.table("tmn_kobe.default.bronze_customer_count_raw")
    source_date_column = _resolve_date_column(raw_customer_count.columns)

    return (
        raw_customer_count
        .filter(F.col(source_date_column).isNotNull())
        .filter(F.trim(F.col(source_date_column).cast("string")) != "")
        .withColumn("sale_date", _parse_business_date(source_date_column))
        .withColumn("year", F.year(F.col("sale_date")))
        .withColumn("month", F.month(F.col("sale_date")))
        .withColumn("day", F.dayofmonth(F.col("sale_date")))
        .withColumn("created_at", F.current_timestamp())
        .withColumn("updated_at", F.current_timestamp())
        .select(
            "sale_date",
            "year",
            "month",
            "day",
            "store_id",
            "customer_count",
            "created_at",
            "updated_at",
        )
    )
