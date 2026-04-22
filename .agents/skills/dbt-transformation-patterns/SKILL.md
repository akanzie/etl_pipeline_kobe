---
name: dbt-transformation-patterns
description: Expert in dbt (data build tool) for SQL-first analytics engineering—model organization, incremental strategies, testing, documentation, and lineage management. Use when building dbt projects, designing transformation models, implementing incremental strategies, testing data quality, or managing dbt documentation.
version: 2.0.0
dependencies:
  - data-pipeline-engineer
  - data-quality-frameworks
tags:
  - dbt
  - transformations
  - analytics
---
- sql
- analytics
- transformations

---

# dbt Transformation Patterns

## Overview

The dbt Transformation Patterns skill focuses on **building production-grade analytics transformations with dbt**—from project structure through testing and documentation. This is a specialized, deep-focus skill for analytics engineers and data engineers implementing SQL transformations.

Use this skill when:

- Building or restructuring a dbt project
- Implementing incremental models for large datasets
- Setting up testing and documentation
- Optimizing dbt model organization and materialization
- Creating reusable macros and transformations

## Core Capabilities

- **Project Architecture**: Organize models into staging, intermediate, and marts layers
- **Incremental Strategies**: Choose delete+insert, merge, or insert-overwrite based on warehouse and data patterns
- **Testing Framework**: Design comprehensive test suites (schema, data quality, relationships)
- **Documentation**: Generate and maintain dbt docs, column-level lineage, model descriptions
- **Macro Development**: Build DRY, reusable SQL macros for common transformations
- **Performance Tuning**: Optimize dbt DAG, materialization strategy, and warehouse execution

## When to Use

## When to Use

- Building a new dbt project or restructuring an existing one
- Implementing incremental models for large fact/event tables
- Setting up automated testing and data quality validation
- Optimizing dbt performance (compile time, execution time, DAG structure)
- Creating reusable macros for transformations
- Establishing documentation and lineage standards

## Workflow / Process

### Phase 1: Project Structure

1. Define source system definitions and mappings
2. Design layer strategy (staging → intermediate → marts)
3. Establish naming conventions and materialization strategy

### Phase 2: Model Development

1. Build staging models (1:1 with sources, light cleaning)
2. Create intermediate models (business logic, joins)
3. Build mart models (final dimension and fact tables)

### Phase 3: Testing & Documentation

1. Add column and model tests
2. Define data quality expectations
3. Generate and validate dbt docs

### Phase 4: Optimization

1. Tune materialization (view vs table vs ephemeral vs incremental)
2. Optimize incremental strategies for full-refresh vs run speed
3. Monitor dbt run time and warehouse costs

## Standards & Best Practices

### Project Organization

- **Staging**: 1:1 with sources, minimal transformations, documented column lineage
- **Intermediate**: Business logic, joins, aggregations; ephemeral unless reused
- **Marts**: Final analytics tables (dimensions and facts), fully tested
- **Naming**: `stg_` (staging), `int_` (intermediate), `dim_`/`fct_` (marts)

### Testing Strategy

- **Schema Tests**: Column-level (not null, unique) on all key columns
- **Relationship Tests**: Foreign key integrity to upstream models
- **Custom Tests**: Business rule validation (amounts >= 0, statuses in enum)
- **Test Coverage**: Goal is 100% on dimensions and facts; 80%+ on staging

### Incremental Models

- **Use for**: Tables > 1M rows where full refresh becomes expensive
- **Delete+Insert**: Default; good for append-only data
- **Merge**: Best for tables with updates to existing rows
- **Insert Overwrite**: Partition-based; efficient for time-series data

### Common Pitfalls

- **Raw → Mart in One Model**: Creates tech debt. Always stage data first.
- **Hardcoded Dates**: Use `{{ var() }}` for parameters, not hardcoded filters.
- **Duplicate Logic**: Extract repeated SQL to macros, not copy-paste.
- **No Testing**: Prevents bugs from propagating downstream. Test aggressively.
- **Ignoring Source Freshness**: Data staleness breaks analytics. Monitor it.
- **Over-Materialization**: Materialize as table only when necessary (marts, heavy joins).
- **Not Using Incremental**: Full refresh becomes expensive; incremental catches late arrivals.

## Constraints

**Technical Constraints:**

- Cannot modify source system definitions without architect approval
- All models must pass testing before deployment
- Incremental strategies must handle late-arriving and updated data correctly

**Scope Constraints:**

- In Scope: Model development, SQL transformations, dbt macros, testing, documentation
- Out of Scope: Data pipeline orchestration (use data-pipeline-engineer), source system setup (use architect)

## Integration Points

| Phase | Input From | Output To | Context |
|-------|-----------|-----------|---------|
| Requirements | `architect`, `data-pipeline-engineer` | Model design | Understanding data domain and staging inputs |
| Source Definitions | `data-pipeline-engineer` | Staging models | Raw data from pipelines becomes transformed |
| Quality Validation | `data-quality-frameworks` | dbt tests | Data quality expectations embedded in tests |
| Documentation | Model metadata | Analytics tools (Tableau, Looker) | dbt docs provide lineage and column descriptions |
| Optimization | Performance issues | `senior-data-engineer` | Complex tuning or architectural redesign |

## Reference Examples

See `examples/` directory for:

- Complete project structure (staging/intermediate/marts)
- Source definitions and freshness monitoring
- Incremental model implementations
- Testing suites (schema, relationships, custom)
- Macro examples (DRY transformations)
- dbt commands reference

---

**Version History:**

- 1.0 (2026-01-24): dbt-focused analytics engineering skill
