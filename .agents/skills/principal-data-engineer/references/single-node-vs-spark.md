# Single-Node Compute vs Apache Spark

## Overview

The modern data stack has shifted towards **single-node tools** (Polars, DuckDB) for most workloads. Apache Spark remains powerful but is overused. This guide clarifies when to use each.

## Single-Node Tools: Polars, DuckDB, Ibis

### Philosophy

**Zero-memory file reads**: Query files directly without materialising data into memory. Scan only the columns and rows you need.

### When to Use Single-Node Tools

#### ✅ Use Polars/DuckDB when

1. **Data fits in memory** (1GB–500GB on a single machine)

   - Both Polars and DuckDB handle larger-than-RAM datasets via streaming and query optimisation
   - No distributed orchestration overhead

2. **You need ad-hoc analysis or development**

   - Instant startup (milliseconds vs minutes for Spark clusters)
   - Interactive REPL-friendly
   - Rapid iteration without cluster management

3. **You're processing files from cloud storage** (S3, GCS, Azure)

   - DuckDB and Polars scan Parquet/JSON/CSV directly without downloading
   - Only fetch needed columns/rows (predicate pushdown)
   - Example: `SELECT COUNT(*) FROM 's3://bucket/year=2024/*.parquet'` touches only the 2024 files

4. **You're in CI/CD or serverless environments** (Lambda, Cloud Functions)

   - No Spark cluster to provision
   - Single-process execution is simpler to containerise
   - Lower cold-start latency

5. **You want portable code** (local dev → cloud prod)

   - Ibis with DuckDB locally, Snowflake in prod
   - Same code runs everywhere
   - Spark ties you to a specific cluster

6. **Cost matters more than throughput**

   - DuckDB on a laptop costs $0; Spark cluster costs $50–500/day
   - For sub-1TB datasets, single-node is 10–100× cheaper

7. **You have moderate throughput requirements** (seconds–minutes latency acceptable)
   - No need to parallelise across dozens of machines
   - Query optimisation (lazy evaluation, predicate pushdown) often outperforms Spark's raw parallelism

### Key Capabilities

#### DuckDB: Zero-Memory File Reads

DuckDB queries files directly from disk/S3 without loading into memory.

```python
import duckdb

# Query a 100GB Parquet file, touching only 2024 data
result = duckdb.sql("""
    SELECT user_id, event_date, COUNT(*) as events
    FROM 's3://my-bucket/events/year=2024/*.parquet'
    WHERE event_date >= '2024-01-01'
    GROUP BY user_id, event_date
""")

# Result is streamed; no intermediate materialisation
result.pl()  # Convert to Polars when needed
```

**Memory profile**: Memory usage is independent of file size (proportional to query result size).

#### Polars: Lazy Evaluation + Arrow

Polars optimises entire query plans before execution.

```python
import polars as pl

# Lazy—plan built but not executed
result = (
    pl.scan_parquet("s3://bucket/*.parquet")
    .filter(pl.col("year") == 2024)  # Pushed to disk read
    .select(["user_id", "event"])      # Only these columns read
    .lazy()
)

# Collect only when needed
df = result.collect()
```

**Benefits**:

- Column projection (read only needed columns)
- Predicate pushdown (filter at storage layer)
- Query optimisation across full plan

#### Ibis: Write Once, Run Anywhere

Ibis is a high-level API that generates SQL for different backends.

```python
import ibis

# Write logic once
def compute_user_stats(con):
    events = con.table("events")
    return (
        events
        .filter(events.year == 2024)
        .group_by("user_id")
        .aggregate(count=events.user_id.count())
    )

# Run locally with DuckDB
import duckdb
local_con = ibis.duckdb.connect()
result = compute_user_stats(local_con).execute()

# Same logic, Snowflake backend (prod)
import snowflake.snowpark as snowpark
prod_con = ibis.snowflake.connect(session)
result = compute_user_stats(prod_con).execute()
```

---

## Apache Spark: Distributed Processing

### Philosophy

Spark distributes computation across a cluster. Overkill for most modern workloads due to overhead, but essential at extreme scale.

### When to Use Apache Spark

#### ✅ Use Spark when

1. **Data does NOT fit on a single machine** (>500GB; truly multi-terabyte)

   - DuckDB/Polars streaming has limits; Spark's distributed shuffle handles arbitrary data
   - MapReduce-style operations across partitions

2. **You need strict fault tolerance** (10+ hour jobs)

   - Spark checkpoints intermediate results
   - Job failure at hour 9 can resume from checkpoint, not restart
   - Single-node tools restart from the beginning

3. **You require exactly-once semantics** (financial transactions, deduplication)

   - Spark's shuffle guarantees exactly-once when configured properly
   - Single-node tools provide no distributed atomicity

4. **You're already in Hadoop/cloud ecosystem** with pre-existing clusters

   - Overhead already paid; incremental cost of additional jobs is low
   - Integration with existing orchestration (Airflow with SparkSubmitOperator)

5. **You have heterogeneous data sources** requiring complex ETL
   - Spark integrates with Kafka, HDFS, cloud storage, databases simultaneously
   - Complex joins across multiple semi-structured sources

### Spark Anti-Patterns to Avoid

Even when using Spark, follow these principles:

1. **Don't use Spark for small datasets** (<10GB)

   ```python
   # Bad: Spark overhead kills performance
   spark.read.parquet("small_file.parquet").show()

   # Good: Use DuckDB
   duckdb.read_parquet("small_file.parquet")
   ```

2. **Don't collect results to driver** (avoid `.collect()`)

   ```python
   # Bad: Materialises entire result on driver
   data = spark.sql("SELECT * FROM huge_table").collect()

   # Good: Write to Parquet, process downstream
   spark.sql("SELECT * FROM huge_table").write.parquet("output/")
   ```

3. **Don't use Spark for OLAP queries** (aggregations, filtering)

   ```python
   # Bad: Spark has high latency for OLAP
   spark.sql("SELECT COUNT(*) FROM events WHERE date = '2024-01-01'")

   # Good: Use DuckDB or data warehouse
   duckdb.sql("SELECT COUNT(*) FROM 's3://bucket/events.parquet' WHERE date = '2024-01-01'")
   ```

4. **Don't use Spark in serverless/Lambda**
   - Cold start: 10+ minutes (cluster provisioning)
   - Single-node: <1 second
   - Use Polars or DuckDB instead

---

## Decision Tree

```
Does the dataset fit on a single machine (< 500GB)?
├─ YES → Use Polars/DuckDB
│        │
│        ├─ SQL queries? → Use DuckDB
│        ├─ DataFrame operations? → Use Polars
│        └─ Need portability? → Use Ibis
│
└─ NO → Is strict fault tolerance required (10+ hour jobs)?
        ├─ YES → Use Spark
        ├─ NO → Consider:
        │       • Partition dataset, process serially with single-node tools
        │       • Stream results instead of materialising
        │       • Use data warehouse (Snowflake) for true scale
        └─ Still need distributed compute? → Use Spark carefully
```

## Comparative Table

| Dimension                  | Polars                    | DuckDB               | Ibis                         | Spark                      |
| -------------------------- | ------------------------- | -------------------- | ---------------------------- | -------------------------- |
| **Max Dataset**            | ~500GB single-node        | ~500GB single-node   | Depends on backend           | Multi-terabyte distributed |
| **Startup Time**           | <100ms                    | <10ms                | <100ms                       | 5–10 minutes               |
| **Query Latency**          | Milliseconds–seconds      | Milliseconds–seconds | Milliseconds–seconds (local) | Seconds–minutes            |
| **Cost (on laptop)**       | $0                        | $0                   | $0                           | $0                         |
| **Cost (cloud cluster)**   | ~$0.50/hour               | ~$0.50/hour          | ~$0.50/hour                  | $50–500/day                |
| **Fault Tolerance**        | None (restart on failure) | None                 | Depends on backend           | Checkpointing built-in     |
| **Memory Model**           | Lazy, streamed            | Streamed             | Query-plan dependent         | Distributed RDD            |
| **Zero-memory file reads** | Via `scan_parquet()`      | Native               | Via backend                  | No (pulls to executors)    |
| **Python Integration**     | Native                    | Native               | Native                       | PySpark (overhead)         |
| \*\*Distributed?           | No                        | No                   | Depends on backend           | Yes                        |

---

## Practical Guidelines

### Rule of Thumb

- **<100GB data, <5 min latency**: Use Polars/DuckDB
- **100GB–500GB data, <10 min latency**: Use DuckDB + lazy queries
- **>500GB or strict fault tolerance**: Use Spark
- **Code portability required**: Use Ibis locally, switch backend later

### Migration Pattern (Scaling Up)

1. **Start**: Polars/DuckDB on laptop
2. **Medium**: dlt → DuckDB → Parquet in S3 (single node)
3. **Large**: Partition dataset, use serial single-node jobs (dlt → DuckDB in Airflow tasks)
4. **Very Large**: Spark cluster or data warehouse (Snowflake)

Most teams never leave stage 3. Spark is truly needed only when:

- Data volume exceeds single-node capability AND
- Fault tolerance is required AND
- Cost of infrastructure is already sunk

---

## Example: The Same Job in Different Tools

### Query: Count events by user in 2024 (10GB dataset)

**Polars:**

```python
import polars as pl

result = (
    pl.scan_parquet("s3://bucket/events/*.parquet")
    .filter(pl.col("year") == 2024)
    .groupby("user_id").agg(pl.col("event_id").count().alias("event_count"))
    .collect()
)
# Execution time: ~2 seconds, memory: ~500MB
```

**DuckDB:**

```python
import duckdb

result = duckdb.sql("""
    SELECT user_id, COUNT(*) as event_count
    FROM 's3://bucket/events/*.parquet'
    WHERE year = 2024
    GROUP BY user_id
""")
# Execution time: ~1 second, memory: ~100MB
```

**Ibis (DuckDB backend):**

```python
import ibis

con = ibis.duckdb.connect()
events = con.read_parquet("s3://bucket/events/*.parquet")
result = (
    events
    .filter(events.year == 2024)
    .group_by("user_id")
    .aggregate(event_count=events.event_id.count())
    .execute()
)
# Execution time: ~1 second
```

**Spark (for comparison):**

```python
spark.read.parquet("s3://bucket/events/*.parquet") \
    .filter("year = 2024") \
    .groupBy("user_id").count() \
    .show()
# Startup: 5 minutes, execution: 30–60 seconds
# Memory: 2–4GB across executors
```

**Verdict**: DuckDB/Polars are 30–60× faster for this workload. Spark adds no value at 10GB.
