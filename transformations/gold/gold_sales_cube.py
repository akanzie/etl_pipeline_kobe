from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="Gold - Pre-aggregated sales cube for fast analytics",
    cluster_by=["month_id", "cooperative_id", "region_id", "business_model_id"]
)
def gold_sales_cube():
    # Read all required tables
    sales = spark.read.table("fact_daily_sales")
    stores = spark.read.table("master_stores")
    regions = spark.read.table("master_regions")
    products = spark.read.table("master_products")
    customer_count = spark.read.table("fact_daily_customer_count")
    
    # Join facts with masters
    sales_enriched = (
        sales
        .join(stores, sales.store_id == stores.store_id, "inner")
        .join(regions, stores.region_id == regions.region_id, "inner")
        .join(products, sales.product_id == products.product_id, "inner")
        .join(
            customer_count, 
            (sales.month_id == customer_count.month_id) & 
            (sales.store_id == customer_count.store_id),
            "left"
        )
    )
    
    # Aggregate to cube dimensions
    cube = (
        sales_enriched
        .groupBy(
            sales.month_id,
            regions.cooperative_id,
            stores.region_id,
            stores.business_model_id,
            F.coalesce(products.category, F.lit("")).alias("category"),
            sales.store_id,
            sales.product_id,
            sales.classification
        )
        .agg(
            # Total quantities and amounts
            F.sum(sales.quantity_sold).alias("total_qty"),
            F.sum(sales.sales_amount).alias("total_amt"),
            
            # Customer count (take max since it's the same per month+store)
            F.max(customer_count.customer_count).alias("customer_count"),
            
            # Calculated metrics
            (F.sum(sales.sales_amount) / F.nullif(F.sum(sales.quantity_sold), F.lit(0))).alias("avg_unit_price"),
            (F.sum(sales.quantity_sold) / F.nullif(F.max(customer_count.customer_count), F.lit(0))).alias("qty_pi"),
            (F.sum(sales.sales_amount) / F.nullif(F.max(customer_count.customer_count), F.lit(0))).alias("amt_pi"),
            
            # Placeholder for markdown quantity
            F.lit(0).cast("decimal(18,2)").alias("markdown_qty"),
            
            # Timestamps
            F.current_timestamp().alias("created_at"),
            F.current_timestamp().alias("updated_at")
        )
    )
    
    return cube.select(
        "month_id", "cooperative_id", "region_id", "business_model_id", 
        "category", "store_id", "product_id", "classification",
        "total_qty", "total_amt", "customer_count", 
        "avg_unit_price", "qty_pi", "amt_pi", "markdown_qty",
        "created_at", "updated_at"
    )
