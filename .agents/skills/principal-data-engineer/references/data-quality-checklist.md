# Data Quality & Governance Checklist

Use this checklist during design reviews and pre-deployment checks.

## 1. Data Contracts (Open Data Contract Standard)

- [ ] **Contract Exists**: Is there a `datacontract.yaml` defining the schema, SLAs, and ownership?
- [ ] **Contract Validation**: Is `datacontract-cli` integrated into CI to validate contracts?
- [ ] **Breaking Change Process**: Is there a versioning strategy for breaking schema changes?
- [ ] **Nullability**: Are required fields explicitly marked as non-nullable in the contract?

## 2. Ingestion Gates

- [ ] **Validation on Write**: Does the ingestion job fail if data doesn't match the schema?
- [ ] **Dead Letter Queue (DLQ)**: Do bad records go to a DLQ for manual inspection, or are they silently dropped? (Silent drop is rarely acceptable).

## 3. Transformation & Logic

- [ ] **Idempotency**: If I run this job twice for the same `data_interval_start`, do I get duplicate rows? (Use MERGE/upsert or full partition replacement).
- [ ] **Temporal Correctness**: Does the pipeline use `logical_date` or `data_interval_start`? (Never use `datetime.now()`).
- [ ] **Determinism**: Given the same inputs and logical date, does the pipeline produce identical outputs?

## 4. Post-Load Validation (Data Reliability Engineering)

- [ ] **Row Counts**: Did we insert roughly the expected number of rows? (e.g., ±20% of last week's average).
- [ ] **Uniqueness**: Is the Primary Key actually unique?
- [ ] **Referential Integrity**: Do the foreign keys in the Fact table point to existing dimensions?

## 5. Metadata & Lineage

- [ ] **Ownership**: Does the table have a clear `owner` tag in the data contract?
- [ ] **Documentation**: Is there a description for the table and its columns in the catalog?
- [ ] **Lineage Tracking**: Is column-level lineage captured (dbt, OpenLineage)?

## 6. Data Quality with Soda

- [ ] **Soda Checks**: Are `soda_checks.yaml` files defined for critical datasets?
- [ ] **Freshness**: Is `freshness` check configured with SLA thresholds?
- [ ] **Anomaly Detection**: Are `anomaly_score` checks enabled for key metrics?
- [ ] **Pipeline Integration**: Are Soda scans executed as part of the DAG (post-load validation)?
