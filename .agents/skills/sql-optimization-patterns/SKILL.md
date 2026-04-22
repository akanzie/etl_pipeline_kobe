---
name: sql-optimization-patterns
description: Specialist in SQL query optimization—index strategies, EXPLAIN analysis, query tuning. Transforms slow queries into fast ones through systematic diagnosis and targeted optimization.
version: 2.0.0
dependencies:
  - senior-data-engineer
tags:
  - sql
  - optimization
  - database
  - performance
  - indexing
---

# SQL Optimization Patterns

Specialist in diagnosing and fixing SQL performance bottlenecks through query plan analysis and indexing strategies.

## When to Use This Skill

Use when:

- SQL queries exceed SLA or performance requirements
- Need to diagnose slow queries using EXPLAIN analysis
- Designing database schemas and indexing strategies for analytics workloads
- Reducing database costs through query efficiency
- Optimizing joins, aggregations, or complex analytical queries
- Investigating full table scans and expensive operations
- Implementing index strategies for high-performance reads
- Performance debugging when queries are slow in production

---

## Core Capabilities

1. **Query Plan Analysis** - Read EXPLAIN output to identify bottlenecks
2. **Indexing Strategies** - Design B-tree, hash, GIN, BRIN indexes for query patterns
3. **Join Optimization** - Choose strategies (nested loop, hash, merge) based on data size
4. **Schema Design** - Denormalization, partitioning, materialized views for analytics
5. **Query Refactoring** - Rewrite slow queries using window functions, CTEs, batch operations
6. **Cost Reduction** - Improve query efficiency to reduce compute costs and resource usage

---

## Reference Guides

For detailed implementation guidance, see:

### [EXPLAIN & Query Plans](references/explain-query-plans.md)

**Use when:** Analyzing slow query performance

Covers:

- Understanding EXPLAIN output across PostgreSQL, MySQL, Snowflake, BigQuery
- Key metrics (Seq Scan, Index Scan, cost, rows, execution time)
- Reading execution plans from bottom-up
- Identifying bottlenecks and cardinality issues

### [Indexing Strategies](references/indexing-strategies.md)

**Use when:** Designing indexes for analytics workloads

Covers:

- Index types (B-tree, hash, GIN, BRIN, covering, partial)
- Selectivity and composite index design
- Partial and expression indexes
- Avoiding over-indexing and unused indexes
- Index maintenance (ANALYZE, VACUUM, reindex)

### [Query Optimization Patterns](references/query-optimization.md)

**Use when:** Rewriting queries for better performance

Covers:

- Eliminating N+1 query problems
- Cursor-based pagination (vs OFFSET)
- Optimizing COUNT and GROUP BY
- Transforming correlated subqueries
- Using CTEs and window functions
- Batch processing patterns

### [Advanced Techniques](references/advanced-techniques.md)

**Use when:** Using advanced database features

Covers:

- Materialized views for pre-computation
- Table partitioning for large tables
- Query hints and optimization control
- Performance monitoring and statistics
- Connection pooling and tuning

---

## Quick Decision Guide

| Problem | Reference |
| :------ | :-------- |
| Query is slow | [EXPLAIN & Query Plans](references/explain-query-plans.md) |
| Need to add indexes | [Indexing Strategies](references/indexing-strategies.md) |
| Rewrite query efficiently | [Query Optimization Patterns](references/query-optimization.md) |
| Advanced optimization | [Advanced Techniques](references/advanced-techniques.md) |

---

## Optimization Workflow

### Phase 1: Diagnosis

1. Capture slow query with `EXPLAIN ANALYZE`
2. Identify bottleneck: sequential scan, expensive join, high cost estimate
3. Understand data volumes and selectivity

### Phase 2: Root Cause Analysis

1. Check for missing indexes on filter/join columns
2. Review join strategy (nested loop vs hash vs merge)
3. Analyze cardinality estimates vs actual rows

### Phase 3: Optimization

1. Add indexes (B-tree, hash, GIN, BRIN as appropriate)
2. Rewrite query to reduce complexity (CTEs, window functions)
3. Consider denormalization or materialized views
4. Measure impact: runtime, cost, resource usage

### Phase 4: Validation

1. Test optimization with production data volume
2. Monitor side effects (index maintenance overhead, storage)
3. Document solution and performance improvement

---

## Best Practices

### Performance Analysis

- ✅ **Establish Baseline**: Measure query runtime, cost, resource usage before optimization
- ✅ **Use EXPLAIN ANALYZE**: Always run with ANALYZE; never guess at performance
- ✅ **Understand Costs**: Lower query cost estimate usually correlates with faster execution
- ✅ **Check Selectivity**: Filters with poor selectivity waste I/O; indexes on selective columns help most

### Indexing Strategy

- ✅ **Index Selective Columns**: Indexes help when filtering/joining on high-cardinality columns
- ✅ **Avoid Over-Indexing**: Every index slows writes; add only indexes that measurably help
- ✅ **Composite Indexes**: Order by selectivity (most selective first) and join key order
- ✅ **Partial Indexes**: Index only relevant subset (e.g., WHERE active = true)

### Query Optimization

- ✅ **Filter Early**: Push WHERE clauses down before joins
- ✅ **Minimize Shuffles**: Avoid sorting/aggregating large result sets; use indexes for ordering
- ✅ **Use Window Functions**: More efficient than self-joins for ranking, running totals
- ✅ **Denormalize Strategically**: Trade write complexity for read speed when appropriate

---

## Common Pitfalls

| Pitfall | Root Cause | Fix |
| :------ | :--------- | :-- |
| Missing index | Obvious filter on non-indexed column | Add index on frequently filtered columns |
| Unused index | Index added but never used | Use EXPLAIN; verify index is selected by planner |
| Indexing without EXPLAIN | Adding indexes blindly | Run EXPLAIN ANALYZE before/after; confirm improvement |
| Bad join order | Joining large table first | Filter before joins; use EXPLAIN to understand order |
| Over-indexing | Every column indexed | Remove unused indexes; focus on high-value queries |
| Stale statistics | Query plan based on old stats | Run VACUUM ANALYZE regularly |

---

## Dependencies

- **senior-data-engineer** - For schema design and performance mentorship
