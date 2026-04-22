---
name: data-quality-frameworks
description: Specialist in data quality validation frameworks—Great Expectations, dbt tests, data contracts. Builds comprehensive data quality gates into pipelines for reliability and trust.
version: 2.0.0
dependencies:
  - data-pipeline-engineer
  - dbt-transformation-patterns
tags:
  - quality
  - validation
  - testing
  - contracts
---

# Data Quality Frameworks

Expert in embedding quality validation into data pipelines as a dependency, not an afterthought.

## When to Use This Skill

Use when:

- Building comprehensive data quality validation into pipelines
- Setting up Great Expectations suites and automated checkpoints
- Creating dbt test suites (schema tests, relationship tests, custom tests)
- Establishing data contracts between producer and consumer teams
- Monitoring data quality metrics, SLAs, and anomalies
- Debugging data quality failures or regressions
- Implementing layer-based validation (Bronze schema, Silver business rules, Gold aggregations)
- Blocking bad data from proceeding downstream

---

## Core Capabilities

1. **Great Expectations** - Build expectation suites, checkpoints, automated validation
2. **dbt Testing** - Schema, relationship, and custom test strategies
3. **Data Contracts** - Producer/consumer agreements (ODCS, datacontract-cli)
4. **Quality Monitoring** - Continuous validation, metrics tracking, alerting
5. **Debugging** - Root-cause analysis of data quality anomalies
6. **Layer-Based Validation** - Schema (Bronze), rules (Silver), aggregation checks (Gold)

---

## Framework References

For detailed implementation guidance, see:

### [Great Expectations](references/great-expectations.md)

**Use when:** Building GE validation suites and checkpoints

Covers:

- Building comprehensive expectation suites
- Checkpoint configuration and automation
- Running validations and handling failures
- Integration patterns and alerting

### [dbt Testing](references/dbt-testing.md)

**Use when:** Creating dbt test suites

Covers:

- Schema tests (unique, not_null, accepted_values, relationships)
- Custom generic tests (reusable across models)
- Singular tests (specific business rules)
- Test coverage best practices

### [Data Contracts](references/data-contracts.md)

**Use when:** Establishing producer/consumer agreements

Covers:

- Data contract specification format
- Schema definitions with PII classification
- Quality expectations and SLA definitions
- Contract versioning and evolution
- Validation against contracts

### [Automated Quality Pipeline](references/automated-pipeline.md)

**Use when:** Orchestrating end-to-end quality validation

Covers:

- Building orchestrated quality pipelines
- Multi-table validation workflows
- Quality reporting and metrics
- Integration with Airflow/orchestrators
- Blocking pipelines on failures

---

## Quick Decision Guide

| Goal | Reference |
| :--- | :-------- |
| Build GE validation suite | [Great Expectations](references/great-expectations.md) |
| Add dbt tests to models | [dbt Testing](references/dbt-testing.md) |
| Define producer/consumer contract | [Data Contracts](references/data-contracts.md) |
| Orchestrate multi-table validation | [Automated Quality Pipeline](references/automated-pipeline.md) |

---

## Quality Strategy

### Layer-Based Testing

- **Bronze (Schema)**: Validate schema, data types, null constraints
- **Silver (Business Rules)**: Test foreign keys, categorical values, ranges
- **Gold (Aggregations)**: Verify aggregation logic, metric calculations

### Test Pyramid

- **Most tests**: Single column validations (fast, focused)
- **Fewer tests**: Cross-table relationships (slower, broader)
- **Blocking vs Warning**: Block bad data; warn on minor issues

### Best Practices

**Do's:**

- ✅ Test early - Validate source data before transformations
- ✅ Test incrementally - Add tests as you find issues
- ✅ Document expectations - Clear descriptions for each test
- ✅ Alert on failures - Integrate with monitoring
- ✅ Version contracts - Track schema changes

**Don'ts:**

- ❌ Don't test everything - Focus on critical columns
- ❌ Don't ignore warnings - They often precede failures
- ❌ Don't skip freshness - Stale data is bad data
- ❌ Don't hardcode thresholds - Use dynamic baselines
- ❌ Don't test in isolation - Test relationships too

---

## Common Pitfalls & Fixes

| Pitfall | Fix |
| :------ | :-- |
| Testing only prod | Run tests on dev first: `dbt test --target dev` |
| Generic thresholds | Tailor tests to data characteristics |
| No alerting | Integrate with monitoring; block failures |
| Outdated expectations | Review and refresh expectations quarterly |
| Too many tests | Focus on business-critical quality dimensions |
| Ignoring false positives | Configure expectations to handle edge cases |

---

## Dependencies

- **data-pipeline-engineer** - For pipeline orchestration and debugging
- **dbt-transformation-patterns** - For dbt project integration
- **ops-manager** - For monitoring dashboards and alerting (out of scope for this skill)
