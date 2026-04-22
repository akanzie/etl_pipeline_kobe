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

The composable stack is built on Apache Arrow as the data spine. All tools below are Arrow-native, meaning data passes between them without serialisation overhead.

- **Polars**: Default choice for single-node processing in Python. Built on Arrow/Rust, significantly faster than Pandas, and handles larger-than-RAM datasets via lazy evaluation.
- **DuckDB**: Embedded OLAP database that speaks Arrow fluently. Query Parquet/JSON/CSV files directly from S3, or exchange data with Polars via Arrow.
- **Ibis**: Portable transformation logic using Arrow-compatible backends (DuckDB, Snowflake, BigQuery).

**For deep Arrow knowledge**: See [apache-arrow.md](apache-arrow.md) for ADBC, Flight, PyArrow, IPC, and zero-copy patterns.

### Polars Best Practice

- Always start with `pl.scan_parquet()` (Lazy) instead of `pl.read_parquet()` (Eager) to enable query optimisation.
- Avoid `.apply(lambda x: ...)` which forces Python interpretation. Use native Polars expressions (`pl.col("x").str.parse_int()`).
- Minimise conversions to Pandas; stay in Arrow/Polars for performance.

### DuckDB Integration

DuckDB queries Parquet/JSON/CSV files directly from S3/Data Lakes without loading them first. Results are Arrow tables:

```sql
SELECT * FROM 's3://bucket/*.parquet' WHERE year = 2024
```

Exchange data with Polars via Arrow (zero-copy):

```python
import polars as pl
import duckdb

df = pl.read_parquet("data.parquet")
result = duckdb.from_arrow(df).execute("SELECT COUNT(*) FROM df").arrow_table()
df_result = pl.from_arrow(result)
```

## 3. Portable Transformations: Ibis

**Philosophy**: "Write once, run anywhere (Pandas, DuckDB, Snowflake, BigQuery)."

Ibis provides a uniform DataFrame API that generates SQL for different backends. It decouples transformation logic from the execution engine.

- **Why use it**: You can write your logic locally using DuckDB as the backend for speed/cost, then switch the backend to Snowflake/BigQuery for production deployment _without changing the transformation code_.
- **Standard**: Use Ibis for defining business logic that needs to be portable across environments (e.g., local dev vs. cloud prod).
