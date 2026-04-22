# Data Architecture Patterns

## 1. Batch Processing (The "Standard" ETL/ELT)

**When to use**: End-of-day reporting, complex joins across massive historical datasets, cost-sensitive processing.

**Pattern**:

1. **Ingest**: Raw data lands in "Bronze" / "Raw" layer (S3/GCS) in native format (JSON/CSV).
2. **Load**: Bulk load into Data Warehouse (Snowflake/BigQuery).
3. **Transform**: Use SQL (dbt) to clean ("Silver") and aggregate ("Gold") data.

**Key constraints for Principal Engineers**:

- **Partitioning**: Must partition the raw layer by date/time to control scan costs.
- **Schema Evolution**: What happens when the source JSON adds a field? The ingest process should be robust to additive changes.

## 2. Streaming (The "Kappa" Architecture)

**When to use**: Fraud detection, real-time inventory, operational dashboards (seconds/minutes latency).

**Pattern**:

1. **Event Bus**: Kafka/PubSub acts as the central nervous system.
2. **Stream Processing**: Flink/Spark Streaming/Dataflow processes events in-flight.
3. **Sink**: Data lands in a low-latency store (Redis/Cassandra) for apps and a data lake (Iceberg/Hudi) for analytics.

**Key constraints for Principal Engineers**:

- **Late Data**: How do you handle events arriving 3 hours late? (Watermarking).
- **Exactly-Once**: Is it strictly required? It comes with a performance penalty.

## 3. The Orchestration Pattern (Airflow)

**Guidance**: Airflow is for **orchestration**, not **execution**.

**Anti-Pattern (Do not do)**:

- Pulling 10GB of data into the Airflow Worker's RAM to process with Pandas.

**Best Practice**:

- Airflow Operator triggers a job in a remote system (e.g., `KubernetesPodOperator`, `SnowflakeOperator`, `DatabricksSubmitRunOperator`).
- Airflow waits/polls for completion.

## 4. Backfilling Strategy

**Design principle**: "The present is just a special case of the past."

- Pipelines must use `data_interval_start` / `data_interval_end` or `logical_date` (Airflow 2.10+). Legacy `execution_date` is removed.
- To backfill 1 year of data, run the _same_ code 365 times (in parallel) with different parameters.
- **Never** hardcode `datetime.now()` in transformation logic. Always use the DAG's logical date.
- Use `catchup=True` with appropriate `start_date` and `max_active_runs` to control backfill parallelism.

## 5. Open Table Format (Apache Iceberg)

**When to use**: Lakehouse architectures requiring ACID transactions, schema evolution, and time-travel.

**Key capabilities**:

- **Schema Evolution**: Add, drop, rename columns without rewriting data.
- **Partition Evolution**: Change partitioning strategy without reprocessing historical data.
- **Time-Travel**: Query data as of a specific snapshot for auditing or rollback.
- **Hidden Partitioning**: Partition on derived values (year, month) without exposing to queries.

**Best Practice**: Use Iceberg's merge-on-read for streaming workloads; compact to copy-on-write for batch query performance.
