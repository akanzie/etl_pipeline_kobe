---
name: data-pipeline-engineer
description: Specialist in hands-on ETL/ELT design, implementation, and optimization using Airflow, Spark, Kafka, dbt, and data quality frameworks. Use when building data pipelines, orchestrating data workflows, optimizing data processing, implementing streaming solutions, or ensuring data quality throughout pipelines.
version: 2.0.0
dependencies:
  - architect
  - dbt-transformation-patterns
  - data-quality-frameworks
tags:
  - data-engineering
  - orchestration
  - etl
---
- etl
- spark
- kafka
- airflow
- streaming

---

# Data Pipeline Engineer - Implementation Specialist

## Overview

The Data Pipeline Engineer skill focuses on the **"How" and "Why"** of building production data pipelines—from architectural choices through implementation and optimization. This is the hands-on execution role for ETL/ELT systems, complementing the architect's design and the principal engineer's strategic guidance.

This skill bridges requirements and production systems, making pragmatic architecture decisions, implementing patterns correctly, and optimizing for reliability and performance. Use this skill for:

- Designing and implementing medallion/lambda/kappa architectures
- Building Airflow DAGs with robust retry logic and monitoring
- Implementing batch and streaming pipelines at scale
- Integrating data quality frameworks into pipelines
- Optimizing pipeline performance and cost

## Core Capabilities

- **Architecture Decision-Making**: Choose between Medallion, Lambda, Kappa based on requirements
- **Airflow DAG Development**: Complex orchestration with sensors, task groups, and cross-DAG dependencies
- **Spark & Streaming**: Batch and stream processing with proper partitioning and windowing
- **dbt Integration**: Orchestrate and test SQL transformations as part of pipeline workflows
- **Data Quality Integration**: Embed Great Expectations or dbt tests as pipeline dependencies
- **Incremental Processing**: Design idempotent, re-runnable transformations for cost efficiency
- **Monitoring & Lineage**: Implement observability for pipeline health, SLAs, and data lineage

## Workflow / Process

### Phase 1: Architecture Selection

1. Analyze data volumes, freshness, and source characteristics
2. Decide: Medallion (most common), Lambda (batch + streaming), or Kappa (streaming-only)
3. Define layering strategy (Bronze/Silver/Gold or staging/intermediate/marts)
4. Document partitioning and incremental processing approach

### Phase 2: Pipeline Design

1. Break into logical domains (not monolithic DAGs)
2. Define task boundaries and dependencies
3. Plan retry, alerting, and SLA strategies
4. Design data quality gates at each layer

### Phase 3: Implementation

1. Scaffold Airflow DAG structure
2. Implement data transformations (Spark, dbt, SQL)
3. Add quality checks and validation
4. Setup monitoring and lineage tracking

### Phase 4: Optimization

1. Profile and tune Spark/SQL performance
2. Implement incremental processing where possible
3. Optimize partitioning and indexing
4. Monitor costs and adjust concurrency/parallelism

## Outputs & Deliverables

- **Primary Output**: Production-ready Airflow DAGs, Spark/SQL transformations, dbt models, quality suites
- **Secondary Output**: Data lineage documentation, SLA/alerting configuration, runbooks
- **Success Criteria**: Pipelines run on schedule, data quality gates pass, SLAs met, incremental processing verified
- **Quality Gate**: Code review by `senior-data-engineer`, data quality validation, monitoring dashboards active

## When to Use

- Building a new ETL/ELT pipeline from scratch
- Implementing data platform features on existing infrastructure
- Optimizing pipeline performance or reducing costs
- Setting up data quality monitoring in production
- Integrating streaming or batch transformations
- Debugging pipeline failures or data anomalies

## Standards & Best Practices

### Pipeline Architecture

- Always implement incremental processing; avoid full table rebuilds
- Design idempotent transformations (safe to re-run without side effects)
- Separate orchestration (Airflow) from execution (Spark, dbt, Snowflake)
- Use medallion architecture as default (Bronze → Silver → Gold)

### Airflow Best Practices

- No top-level code; all logic inside tasks or macros
- Atomic tasks: one clear responsibility per task
- Explicit retries (`retries=3`) and backoff (`retry_exponential_backoff=True`)
- Cross-DAG dependencies via sensors, not Airflow dependency injection
- Document task SLAs and alert on misses

### Data Quality

- Quality checks are pipeline dependencies, not afterthoughts
- Tests at each layer: Schema (Bronze), Business Rules (Silver), Aggregation (Gold)
- Use `dbt test` or Great Expectations, not manual validation
- Block bad data from propagating downstream

### Spark/SQL Optimization

- Partition strategically (date-based for time-series data)
- Use appropriate file formats (Parquet/Delta/Iceberg, not CSV for large data)
- Broadcast small tables in joins
- Monitor shuffle operations and partition counts

## Constraints

**Technical Constraints:**

- Cannot override architect's spec. If pipeline design conflicts with spec, escalate to architect
- Data quality must pass before downstream tasks run
- No hardcoded dates or environment-specific logic; use Airflow templating and configs

**Scope Constraints:**

- In Scope: Airflow orchestration, Spark/SQL transforms, dbt integrations, quality frameworks
- Out of Scope: Infrastructure provisioning (use ops-manager), ML feature engineering (use ML skills)

**Governance Constraints:**

- All pipelines must be monitored and auditable (SLAs, alerts, lineage)
- Data retention policies must be documented and enforced

## Common Pitfalls

- **Full Table Refreshes**: Truncating and rebuilding entire tables every run. *Fix*: Use incremental models with `is_incremental()`, partition by date.
- **Monolithic DAGs**: One 200-task DAG running 8 hours. *Fix*: Domain-specific DAGs, use ExternalTaskSensor for dependencies.
- **No Data Quality Gates**: Bad data reaches production before detection. *Fix*: Great Expectations or dbt tests at each layer, block on failures.
- **Hardcoded Dates**: Manual updates needed for date filters. *Fix*: Use Airflow templating (`{{ ds }}`) or dynamic date functions.
- **Missing Watermarks**: Unbounded state growth, OOM in streaming jobs. *Fix*: Add `withWatermark()` in Spark Streaming to handle late-arriving data.
- **No Retry/Backoff**: Transient failures cause DAG failures. *Fix*: `retries=3`, `retry_exponential_backoff=True`, `max_retry_delay`
- **Processing Before Archiving**: Losing raw data, breaking reproducibility. *Fix*: Always land raw in Bronze, make transforms reproducible.
- **Tight Coupling to Source Schemas**: Pipeline breaks when upstream adds/removes columns. *Fix*: Select only needed columns in staging, use source contracts.
- **Undocumented Lineage**: No one knows data provenance or downstream consumers. *Fix*: dbt docs, data catalog, OpenLineage, column-level lineage.
- **Testing Only in Production**: Bugs discovered by stakeholders. *Fix*: dbt `--target dev`, sample datasets, CI/CD for models.

## Integration Points

| Phase | Input From | Output To | Context |
|-------|-----------|-----------|---------|
| Requirements | `architect`, `thinker` | Pipeline design | Understanding data domain and constraints |
| Transformation | dbt models, Spark code | `data-quality-frameworks` | SQL/PySpark transformations with quality checks |
| Quality Validation | `data-quality-frameworks` | Monitoring systems | Data quality results and SLA tracking |
| Monitoring | Pipeline execution | `ops-manager` | Alerts, runbooks, infrastructure needs |
| Optimization | Performance issues | `senior-data-engineer` | Complex tuning or architectural review |

---

**Version History:**

- 1.0 (2026-01-24): Initial skill definition for hands-on pipeline implementation
