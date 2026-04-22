# Modern Data Stack & Tooling

## 1. Data Ingestion: `dlt` (Data Load Tool)

**Philosophy**: "Loading data is a solved problem. Don't reinvent it."

`dlt` automates schema inference, evolution, and normalisation. It moves data from APIs/files/databases to warehouses (Snowflake/BigQuery/DuckDB) with minimal code.

### Getting Started

```bash
# Scaffold a new pipeline
dlt init rest_api duckdb
```

### Built-in Sources

- **REST APIs**: Use `dlt.sources.rest_api` for declarative API configuration.
- **SQL Databases**: Use `dlt.sources.sql_database` for database extraction.
- **Files**: Use `dlt.sources.filesystem` for CSV, Parquet, JSON from local or cloud storage (S3, GCS, Azure).

### Configuration

Configure pipelines via `.dlt/config.toml` and `.dlt/secrets.toml` (must be gitignored). Never hardcode credentials.

### Key Principles

- **Schema Contracts**: Default to `schema_contract="evolve"` for development; use `schema_contract="freeze"` in production.
- **Resource Composition**: Use `@dlt.resource` decorators. Keep resources granular (one per endpoint/table).
- **Incremental Loading**: Use `dlt.sources.incremental` for stateful extraction with automatic checkpointing.
- **State Management**: dlt persists pipeline state automatically; access via `pipeline.state` for custom checkpoints.

**Best Practice**:

```python
import dlt

# dev_mode=True resets schema/state between runs—remove in production
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",
    dataset_name="raw_data",
    dev_mode=True,
)
```

## 2. In-Memory Processing: Arrow-Native Systems

**Philosophy**: "Zero-copy data movement and vectorised execution."

**Apache Arrow** is the standard in-memory format. It allows systems to exchange data without serialisation overhead.

- **Use Arrow for**: Passing data between Python and Rust/C++ components, or between Spark and Pandas (PyArrow).
- **Tooling**:
  - **Polars**: The default choice for single-node data processing in Python. It is built on Arrow/Rust, significantly faster than Pandas, and handles larger-than-RAM datasets via lazy evaluation (`.lazy()`).
  - **PyArrow**: Use directly when interacting with parquet files or dealing with complex nested types that Pandas struggles with.

**Polars Best Practice**:

- Always start with `pl.scan_parquet()` (Lazy) instead of `pl.read_parquet()` (Eager) to enable query optimization.
- Avoid `.apply(lambda x: ...)` which forces Python interpretation. Use native Polars expressions (`pl.col("x").str.parse_int()`).

## 3. Embedded Analytics: DuckDB

**Philosophy**: "OLAP on your laptop (and in your Lambda)."

DuckDB is SQLite for analytics. It runs in-process, has no external dependencies, and vectorises queries.

**Key Capability: Zero-Memory File Reads**

Query Parquet/JSON/CSV files directly from S3/Data Lakes without loading data into memory. Only touched columns and rows are fetched.

```sql
-- Query 100GB Parquet file; only 2024 data and two columns loaded
SELECT user_id, COUNT(*) as events
FROM 's3://bucket/events/year=2024/*.parquet'
GROUP BY user_id;
```

**Use Cases**:

- Ad-hoc queries on cloud data lakes without downloading
- Local data exploration and testing before deploying to large warehouses
- Lightweight transformations in CI/CD pipelines
- Streaming results for large datasets (avoid materialising in memory)

**Integration**: DuckDB speaks Arrow fluently. You can query a Polars dataframe with SQL via DuckDB, or output a DuckDB query result to Polars/Arrow efficiently.

```python
import duckdb
import polars as pl

# Query Polars dataframe with SQL
df = pl.read_parquet("data.parquet")
result = duckdb.from_arrow(df).execute("SELECT * FROM df WHERE value > 100").arrow()

# Convert back to Polars (zero-copy via Arrow)
result_df = pl.from_arrow(result)
```

## 4. Portable Transformations: Ibis

**Philosophy**: "Write once, run anywhere (Pandas, DuckDB, Snowflake, BigQuery)."

Ibis provides a uniform DataFrame API that generates SQL for different backends. It decouples transformation logic from the execution engine.

- **Why use it**: You can write your logic locally using DuckDB as the backend for speed/cost, then switch the backend to Snowflake/BigQuery for production deployment _without changing the transformation code_.
- **Standard**: Use Ibis for defining business logic that needs to be portable across environments (e.g., local dev vs. cloud prod).
