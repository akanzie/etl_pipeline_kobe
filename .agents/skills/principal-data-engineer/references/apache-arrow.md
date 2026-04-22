# Apache Arrow: The Data Spine

## Philosophy

Apache Arrow is not just a serialisation format—it is a data spine that eliminates serialisation overhead between systems. It enables **zero-copy data movement** and **polyglot interoperability** at near-native speeds.

## Why Arrow Matters

**Traditional data passing**: Python object → JSON/Parquet serialisation → wire format → deserialisation → C++ object. Each serialisation/deserialisation step is a CPU bottleneck and memory copy.

**Arrow approach**: Both systems reference the same in-memory representation. No conversion. Single memory layout understood by all languages (C++, Python, Rust, Go, Java).

**Impact**: 10–100× faster data movement, dramatically lower memory usage, reduced CPU utilisation.

## Core Components

### 1. Arrow In-Memory Format (IPC)

The Arrow columnar in-memory format is standardised, language-agnostic, and zero-copy.

- **Column-Oriented**: Perfect for analytical workloads (scanning subsets of columns, vectorised operations).
- **Standardised Layout**: Every system (Python, Rust, C++, etc.) interprets the same bytes identically.
- **Zero-Copy**: No serialisation needed when passing between processes/systems that both understand Arrow.

**When to use**: Any time you need to move data between different systems or languages without serialisation overhead.

### 2. PyArrow

Python bindings for Apache Arrow. Use PyArrow when you need:

- **Direct control over schema and columnar layout**
- **Conversion between Arrow tables and Pandas/Polars** (lossless, efficient)
- **Parquet I/O with fine-grained control**
- **Complex nested types** (structs, lists, unions)
- **IPC and Flight interoperability**

**Key APIs**:

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Create an Arrow table directly
table = pa.table({
    "user_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"]
})

# Convert from Pandas (efficient, handles nullability better)
import pandas as pd
df = pd.DataFrame({"col": [1, 2, None]})
arrow_table = pa.Table.from_pandas(df)

# Write/read Parquet with schema control
pq.write_table(table, "data.parquet")
table = pq.read_table("data.parquet")

# Convert to Polars (preserves Arrow layout, zero-copy)
import polars as pl
df_polars = pl.from_arrow(table)
```

### 3. Arrow Flight

High-performance RPC framework for streaming Arrow data across networks.

- **Streaming Protocol**: Unlike REST/gRPC which serialize JSON, Flight streams Arrow columnar data directly.
- **Low Latency**: Native support for batched data transfer.
- **Use Cases**: Data warehouse query results, cross-service data sharing, microservice communication.

**When to use**:

- Streaming query results from a data warehouse to a consuming service
- Real-time data distribution between services
- Replacing REST APIs for data transfer with 10–100× speedup

**Example**:

```python
import pyarrow.flight as flight

# Server (data warehouse or service)
class MyFlightServer(flight.FlightServerBase):
    def do_get(self, context, ticket):
        table = pa.table({"id": [1, 2, 3], "value": [10, 20, 30]})
        return flight.RecordBatchStream(table)

# Client
client = flight.connect("grpc://localhost:8081")
reader = client.do_get(flight.Ticket(b"my_query"))
table = reader.read_all()
```

### 4. Arrow ADBC (Arrow Database Connectivity)

Standardised API for connecting to SQL databases, analogous to JDBC or ODBC but optimised for Arrow.

- **Zero-Copy Result Transfer**: Query results come back as Arrow tables, not as rows.
- **Unified Interface**: Same API for PostgreSQL, Snowflake, DuckDB, BigQuery, etc.
- **Performance**: Direct Arrow-to-warehouse communication without intermediate serialisation.

**When to use**: Querying any ADBC-compliant database and receiving results as Arrow tables.

**Example**:

```python
import adbc_driver_postgresql.dbapi

# Connect to PostgreSQL
conn = adbc_driver_postgresql.dbapi.connect("postgresql://user:pass@localhost/db")
cursor = conn.cursor()

# Execute and get Arrow table (zero-copy)
cursor.execute("SELECT * FROM large_table LIMIT 1000000")
table = cursor.fetch_arrow_table()  # Returns PyArrow table directly
```

### 5. Arrow PyCapsule Interface

A C data interface for zero-copy sharing of Arrow data between Python libraries without going through serialisation.

- **Language**: Defined in PEP 3118 (Python C API)
- **Use Case**: Polars, DuckDB, Pandas, PyArrow all implement this interface
- **Benefit**: Libraries can exchange Arrow data without knowing about each other

**When to use**: Automatically—most Arrow-aware libraries use this under the hood. Example:

```python
import polars as pl
import pyarrow as pa

# Polars internally returns Arrow via PyCapsule interface
df = pl.read_parquet("data.parquet")  # Polars
arrow_table = df.to_arrow()  # Zero-copy via PyCapsule

# Back to Polars (zero-copy)
df2 = pl.from_arrow(arrow_table)
```

### 6. Parquet Integration

Parquet is the standard columnar storage format, and Arrow is the native in-memory representation for Parquet.

- **Read Parquet**: Use PyArrow to read Parquet files into Arrow tables (respects predicates, column selection, streaming).
- **Write Parquet**: Write from any Arrow-compatible source with full control over compression, schema.

**Best practices**:

```python
import pyarrow.parquet as pq

# Read entire table
table = pq.read_table("data.parquet")

# Read with filtering (pushed to storage, only needed columns)
table = pq.read_table(
    "data.parquet",
    filters=[("year", "==", 2024)],
    columns=["id", "name"]
)

# Stream Parquet (memory-efficient for large files)
reader = pq.ParquetFile("data.parquet")
for batch in reader.iter_batches(batch_size=10000):
    process(batch)  # batch is a RecordBatch (Arrow)

# Write with compression and metadata
pq.write_table(
    table,
    "output.parquet",
    compression="snappy",
    use_dictionary=True,
)
```

## Arrow in the Composable Data Stack

### Ingestion Layer (dlt → Arrow)

`dlt` naturally outputs to Arrow tables (or Parquet files, which are Arrow columnar). This is the first stage of the data spine.

```python
import dlt

pipeline = dlt.pipeline(destination="duckdb")
load_result = pipeline.run(source_data)
# Result is Arrow-backed (DuckDB native format)
```

### Processing Layer (Polars, DuckDB, Ibis)

All three operate natively on Arrow columnar data:

- **Polars**: Built on Arrow/Rust. Every operation is vectorised. No Pandas conversion needed.
- **DuckDB**: Queries Parquet/Arrow directly. Results are Arrow tables.
- **Ibis**: Generates SQL for DuckDB, receives Arrow results.

```python
import polars as pl
import duckdb as db

# Polars (Arrow-native)
df = pl.read_parquet("data.parquet")
result = df.filter(pl.col("value") > 100).select(["id", "value"])

# DuckDB (Arrow-native)
conn = db.connect()
arrow_result = conn.execute("SELECT * FROM 'data.parquet'").arrow()

# Ibis with DuckDB backend (Arrow results)
import ibis
con = ibis.duckdb.connect()
result_table = con.execute(ibis.table({"id": "int64", "value": "int64"}))
```

### 5. DuckDB: Zero-Memory File Reads

DuckDB is an embedded OLAP database that queries files directly from disk or cloud storage without loading data into memory.

**Key Feature: Columnar Projection and Predicate Pushdown**

When you query a Parquet file, DuckDB reads only the columns and rows you need. This is a fundamental difference from loading entire files into memory.

```python
import duckdb

# Query 100GB Parquet file; only 2024 data and 2 columns are read
result = duckdb.sql("""
    SELECT user_id, COUNT(*) as events
    FROM 's3://bucket/events/year=2024/*.parquet'
    WHERE event_date >= '2024-01-01'
    GROUP BY user_id
""").arrow_table()

# result is a PyArrow table—zero-copy exchange
```

**Memory Profile**: Memory usage is bounded by the query result size, not the source data size. A 1TB file query can use <1GB memory if the result is small.

**Integration with Arrow**:

- DuckDB natively outputs to Arrow tables (`.arrow_table()`)
- DuckDB consumes Arrow input (`duckdb.from_arrow(table)`)
- Zero-copy exchange via PyCapsule interface with Polars

**Use Cases**:

- Ad-hoc analytics on S3 data lakes without downloading
- Streaming large result sets to prevent memory spikes
- CI/CD pipelines processing large files with minimal footprint
- Replacing custom Spark jobs for OLAP queries

**Example: Streaming Large Results**

```python
import duckdb

# Stream results in batches
result = duckdb.sql("""
    SELECT * FROM 's3://bucket/huge_dataset/*.parquet'
""")

# Fetch in chunks to avoid materialising entire result
while True:
    batch = result.fetch_arrow_batch()
    if batch is None:
        break
    process_batch(batch)  # Process each batch without holding full result
```

## Output Layer (Flight, ADBC, Parquet)

Arrow is the output format:

- **Flight**: Stream Arrow tables to consumers
- **ADBC**: Receive query results as Arrow tables
- **Parquet**: Store Arrow tables in Parquet format

## Performance Principles

### 1. Stay in Arrow Format

Every conversion to Pandas or Python objects is a performance cliff.

**Bad**:

```python
# Converts Arrow → Pandas → iterates rows (slow)
for index, row in df.iterrows():
    process(row)
```

**Good**:

```python
# Stays in Arrow, vectorised (fast)
result = df.with_columns(pl.col("value").apply(fn))
```

### 2. Lazy Evaluation

Polars lazy mode (`pl.scan_parquet()`, `.lazy()`) delays execution until `.collect()`, allowing query optimisation.

```python
# Lazy—queries only read needed columns, filters pushed down
df = (
    pl.scan_parquet("data.parquet")
    .filter(pl.col("year") == 2024)
    .select(["id", "name"])
    .collect()
)
```

### 3. Zero-Copy Boundaries

Arrow enables zero-copy when boundaries align:

- **Python ↔ DuckDB**: Both Arrow-aware; zero-copy via PyCapsule
- **Python ↔ Flight**: Arrow-native protocol; zero-copy across network
- **Polars ↔ DuckDB**: Both Arrow-aware; zero-copy via PyCapsule

When boundaries _don't_ align (e.g., Pandas), serialisation occurs.

### 4. Streaming for Large Datasets

Use record batch iteration to avoid materialising entire tables:

```python
reader = pq.ParquetFile("huge_file.parquet")
for batch in reader.iter_batches(batch_size=100000):
    # batch is a RecordBatch (Arrow)
    process_batch(batch)
```

## Testing and Validation

Arrow tables support equality and schema validation:

```python
import pyarrow as pa

table1 = pa.table({"id": [1, 2, 3]})
table2 = pa.table({"id": [1, 2, 3]})

assert table1.equals(table2)
assert table1.schema == table2.schema
```

## Integration Checklist

When designing data pipelines:

- [ ] **Ingestion**: Does dlt output Arrow/Parquet?
- [ ] **Processing**: Are you using Polars/DuckDB (Arrow-native) or converting to Pandas?
- [ ] **Transfer**: For cross-service data, is Flight ADBC an option?
- [ ] **Storage**: Parquet files are Arrow columnar; use column selection and filtering.
- [ ] **Conversion**: Minimise Arrow → Pandas conversions; if needed, use `to_pandas(types_mapper=...)`
- [ ] **Testing**: Use `.equals()` for Arrow table assertions.
