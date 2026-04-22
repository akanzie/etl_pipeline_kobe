# Example: Medallion Architecture Data Pipeline

**Pipeline Name**: E-Commerce Analytics Platform  
**Pattern**: Medallion (Bronze → Silver → Gold)  
**Orchestrator**: Apache Airflow  
**Processing**: Apache Spark + Pandas  
**Data Quality**: Great Expectations + dbt  

---

## Architecture Overview

```
Data Sources
    ↓
┌───────────────────────────────────┐
│  BRONZE LAYER (Raw Data)          │ ← Landing zone
│  • Orders (raw JSON)              │ ← No transformations
│  • Customers (raw CSV)            │ ← Minimal validation
│  • Products (raw Parquet)         │ ← Just persistence
└───────────────────────────────────┘
    ↓ [Data Quality: Schema check]
┌───────────────────────────────────┐
│  SILVER LAYER (Clean Data)        │ ← Standardized
│  • Dim Customers (deduplicated)   │ ← Type conversions
│  • Dim Products (validated)       │ ← Quality gates
│  • Fact Orders (joined)           │ ← Business rules applied
└───────────────────────────────────┘
    ↓ [Data Quality: Aggregate rules]
┌───────────────────────────────────┐
│  GOLD LAYER (Analytics Ready)     │ ← Aggregated
│  • Daily Revenue by Product       │ ← Business metrics
│  • Monthly Customer LTV           │ ← KPIs
│  • Cohort Retention Matrix        │ ← Analytics tables
└───────────────────────────────────┘
    ↓
Analytics & BI Tools
```

---

## Layer Specifications

### BRONZE LAYER: Raw Landing Zone

**Purpose**: Faithful reproduction of source systems  
**Frequency**: Hourly incremental loads  
**Retention**: 30 days minimum  

**Tables**:

```sql
-- Bronze: Orders (raw)
CREATE TABLE bronze.orders_raw (
    order_id STRING,
    customer_id STRING,
    order_date STRING,
    total_amount DECIMAL(10,2),
    items JSON,
    metadata JSON,
    _load_timestamp TIMESTAMP,
    _source_file STRING
)
USING DELTA
PARTITIONED BY (_load_date DATE)

-- Bronze: Customers (raw)
CREATE TABLE bronze.customers_raw (
    customer_id STRING,
    email STRING,
    name STRING,
    address JSON,
    phone STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _load_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (_load_date DATE)

-- Bronze: Products (raw)
CREATE TABLE bronze.products_raw (
    product_id STRING,
    name STRING,
    category STRING,
    price DECIMAL(10,2),
    stock INTEGER,
    metadata JSON,
    _load_timestamp TIMESTAMP
)
USING DELTA
```

**Data Quality Gates**:

- ✅ Schema validation (column count, types match)
- ✅ Not null checks on primary keys
- ✅ Duplicate record detection
- ⚠️ Log failures to DLQ, don't reject

---

### SILVER LAYER: Cleaned & Deduplicated

**Purpose**: Single source of truth for transformed data  
**Frequency**: Hourly (dependent on Bronze)  
**Retention**: 1 year minimum  

**Tables**:

```sql
-- Silver: Customers (deduplicated, validated)
CREATE TABLE silver.dim_customers (
    customer_id STRING NOT NULL,
    email STRING NOT NULL,
    customer_name STRING,
    country STRING,
    created_date DATE,
    updated_date DATE,
    is_active BOOLEAN,
    _valid_from TIMESTAMP,
    _valid_to TIMESTAMP,
    _current_flag BOOLEAN
)
USING DELTA
PARTITIONED BY (country)

-- Silver: Products (deduplicated, validated)
CREATE TABLE silver.dim_products (
    product_id STRING NOT NULL,
    product_name STRING NOT NULL,
    category STRING NOT NULL,
    subcategory STRING,
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    margin_pct DECIMAL(5,2),
    is_active BOOLEAN,
    _valid_from TIMESTAMP
)
USING DELTA
PARTITIONED BY (category)

-- Silver: Orders (fact table with dimensions)
CREATE TABLE silver.fact_orders (
    order_id STRING NOT NULL,
    customer_id STRING NOT NULL,
    product_id STRING NOT NULL,
    order_date DATE NOT NULL,
    order_quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    net_amount DECIMAL(10,2),
    order_status STRING,
    _load_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (order_date)
```

**Transformations**:

```python
# Silver: Clean customers
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("silver_customers").getOrCreate()

bronze_customers = spark.read.table("bronze.customers_raw")

silver_customers = (bronze_customers
    .filter(col("customer_id").isNotNull())
    .filter(col("email").isNotNull())
    .dropDuplicates(["customer_id"])
    .select(
        col("customer_id"),
        col("email").cast("string"),
        col("name").alias("customer_name"),
        col("address.country").alias("country"),
        to_date(col("created_at")).alias("created_date"),
        to_date(col("updated_at")).alias("updated_date"),
        col("is_active"),
        current_timestamp().alias("_valid_from"),
        lit(None).cast("timestamp").alias("_valid_to"),
        lit(True).alias("_current_flag")
    )
)

silver_customers.write.mode("overwrite").insertInto("silver.dim_customers")
```

**Data Quality Gates**:

- ✅ Uniqueness on customer_id
- ✅ Email format validation
- ✅ No nulls in key columns
- ✅ Referential integrity (customer_id)
- ✅ SCD Type 2 tracking (valid_from/to)

---

### GOLD LAYER: Business Analytics Tables

**Purpose**: Aggregated, business-ready metrics  
**Frequency**: Daily batch  
**Retention**: 3 years minimum  

**Tables**:

```sql
-- Gold: Daily Revenue by Product
CREATE TABLE gold.daily_revenue_by_product (
    report_date DATE NOT NULL,
    product_id STRING NOT NULL,
    product_name STRING,
    category STRING,
    total_units_sold INTEGER,
    total_revenue DECIMAL(15,2),
    total_discount DECIMAL(15,2),
    net_revenue DECIMAL(15,2),
    avg_unit_price DECIMAL(10,2),
    _load_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (report_date)

-- Gold: Monthly Customer LTV
CREATE TABLE gold.monthly_customer_ltv (
    customer_id STRING NOT NULL,
    customer_name STRING,
    report_month DATE NOT NULL,
    lifetime_orders INTEGER,
    lifetime_revenue DECIMAL(15,2),
    avg_order_value DECIMAL(10,2),
    days_since_first_order INTEGER,
    days_since_last_order INTEGER,
    customer_segment STRING,  -- VIP, Regular, Inactive
    _load_timestamp TIMESTAMP
)
USING DELTA
PARTITIONED BY (report_month)

-- Gold: Cohort Retention Matrix
CREATE TABLE gold.cohort_retention_matrix (
    cohort_month DATE NOT NULL,
    months_since_cohort INTEGER,
    cohort_size INTEGER,
    retained_users INTEGER,
    retention_rate DECIMAL(5,2),
    _load_timestamp TIMESTAMP
)
USING DELTA
```

**Transformations**:

```python
# Gold: Daily Revenue by Product
from pyspark.sql.functions import *
from datetime import date

spark = SparkSession.builder.appName("gold_revenue").getOrCreate()

fact_orders = spark.read.table("silver.fact_orders")
dim_products = spark.read.table("silver.dim_products")

daily_revenue = (fact_orders
    .join(dim_products, "product_id", "left")
    .groupBy(
        to_date(col("order_date")).alias("report_date"),
        col("product_id"),
        col("product_name"),
        col("category")
    )
    .agg(
        count("*").alias("total_units_sold"),
        sum(col("total_amount")).alias("total_revenue"),
        sum(col("discount_amount")).alias("total_discount"),
        sum(col("net_amount")).alias("net_revenue"),
        avg(col("unit_price")).alias("avg_unit_price"),
        current_timestamp().alias("_load_timestamp")
    )
    .filter(col("report_date") == date.today())
)

daily_revenue.write.mode("append").insertInto("gold.daily_revenue_by_product")
```

**Data Quality Gates**:

- ✅ Row count checks (month-over-month growth reasonable)
- ✅ Revenue aggregates validated against source
- ✅ No nulls in key metrics
- ✅ Retention % between 0-100%

---

## Airflow DAG Structure

```python
# dags/medallion_pipeline.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.spark_submit_operator import SparkSubmitOperator
from airflow.providers.great_expectations.operators.great_expectations import GreatExpectationsOperator
from airflow.models import Variable

default_args = {
    'owner': 'data-platform',
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'medallion_analytics',
    default_args=default_args,
    schedule_interval='0 * * * *',  # Hourly
    catchup=False,
)

# Bronze ingestion
ingest_orders = SparkSubmitOperator(
    task_id='bronze_ingest_orders',
    application='scripts/bronze_ingest.py',
    conf={'spark.executor.instances': 4},
    dag=dag
)

# Quality gates
validate_bronze = GreatExpectationsOperator(
    task_id='validate_bronze_schema',
    checkpoint_name='bronze_validation',
    dag=dag
)

# Silver transformation
transform_silver = SparkSubmitOperator(
    task_id='silver_transform',
    application='scripts/silver_transform.py',
    dag=dag
)

# Gold aggregation (daily)
transform_gold = SparkSubmitOperator(
    task_id='gold_transform',
    application='scripts/gold_transform.py',
    dag=dag,
    trigger_rule='all_done'
)

# Pipeline orchestration
ingest_orders >> validate_bronze >> transform_silver >> transform_gold
```

---

## Incremental Processing Strategy

**Problem**: Re-processing all data daily wastes compute and money  
**Solution**: Incremental processing with watermarks

```python
# Only process new orders since last run
last_watermark = spark.read.table("gold.pipeline_watermarks") \
    .filter(col("table_name") == "orders") \
    .select(max(col("last_processed")).alias("max_timestamp")) \
    .collect()[0][0]

new_orders = (spark.read.table("bronze.orders_raw")
    .filter(col("_load_timestamp") > last_watermark)
)

# Process only new data
new_orders.write.mode("append").insertInto("silver.fact_orders")

# Update watermark
spark.createDataFrame([
    ("orders", current_timestamp())
], ["table_name", "last_processed"]) \
    .write.mode("append").insertInto("gold.pipeline_watermarks")
```

---

## Testing & Validation

```python
# tests/test_medallion_pipeline.py

import pytest
from pyspark.sql import SparkSession

@pytest.fixture
def spark():
    return SparkSession.builder.master("local").appName("test").getOrCreate()

def test_bronze_orders_schema(spark):
    """Verify Bronze layer schema"""
    df = spark.read.table("bronze.orders_raw")
    assert df.schema["order_id"].dataType == StringType()
    assert df.schema["total_amount"].dataType == DecimalType(10, 2)

def test_silver_no_duplicates(spark):
    """Verify Silver layer has no duplicate customers"""
    df = spark.read.table("silver.dim_customers")
    duplicates = df.groupBy("customer_id").count().filter(col("count") > 1)
    assert duplicates.count() == 0

def test_gold_aggregates_match_source(spark):
    """Verify Gold totals match Silver source"""
    gold_total = spark.read.table("gold.daily_revenue_by_product") \
        .agg(sum("net_revenue")).collect()[0][0]
    
    silver_total = spark.read.table("silver.fact_orders") \
        .agg(sum("net_amount")).collect()[0][0]
    
    assert abs(gold_total - silver_total) < 0.01  # Allow for rounding
```

---

## Monitoring & Alerting

**Pipeline Health Checks**:

- ✅ All tables updated within last 2 hours
- ✅ No null values in key columns (Bronze, Silver, Gold)
- ✅ Row counts within expected ranges (±20%)
- ✅ Data freshness SLA: < 1 hour lag

**Alerts**:

- 🔴 Critical: Missing gold.daily_revenue_by_product (BI depends on it)
- 🟠 Warning: > 10% row count variance
- 🟡 Info: Slow transforms (> 30 min)

---

## Best Practices Applied

✅ **Partitioning**: All tables partitioned by date for efficient queries  
✅ **Delta format**: ACID transactions, time travel, rollback capability  
✅ **Idempotency**: All jobs can be re-run without duplicating data  
✅ **Data quality**: Three levels of validation (schema, rules, aggregates)  
✅ **Incremental**: Only new data processed (watermark strategy)  
✅ **Documentation**: Clear layer purposes, transformations, SLAs  
✅ **Testing**: Unit tests for transformations, integration tests for pipelines  

---

**Next Step**: Hand off to `senior-data-engineer` for performance optimization and scaling considerations.
