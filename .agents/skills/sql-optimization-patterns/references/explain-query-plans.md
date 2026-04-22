# EXPLAIN & Query Plans

Comprehensive guide to reading and analyzing SQL EXPLAIN output.

## When to Use This Reference

Use when:

- Analyzing slow query performance
- Understanding query execution plans
- Identifying bottlenecks (sequential scans, expensive joins)
- Comparing query optimization before/after

---

## Understanding EXPLAIN

Query execution plans reveal exactly how the database executes your query.

### PostgreSQL EXPLAIN

```sql
-- Basic explain (shows plan only)
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- With actual execution stats
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user@example.com';

-- Verbose output with more details
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT u.*, o.order_total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '30 days';
```

### Key Metrics

| Metric | Meaning | Good vs Bad |
| :----- | :------ | :---------- |
| **Seq Scan** | Full table scan | Bad for large tables |
| **Index Scan** | Using index | Good for equality |
| **Index Only Scan** | Using index without table | Best efficiency |
| **Nested Loop** | Join method | Okay for small datasets |
| **Hash Join** | Join method | Good for larger datasets |
| **Merge Join** | Join method | Good for sorted data |
| **Cost** | Estimated work units | Lower is better |
| **Rows** | Estimated rows returned | Compare to actual |
| **Actual Time** | Real execution time (ms) | Lower is better |

### Example EXPLAIN Output

```
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id, u.name;

HashAggregate  (cost=15.20..20.30 rows=100 width=40)
  Group Key: u.id, u.name
  ->  Hash Left Join  (cost=5.00..10.20 rows=500 width=40)
        Hash Cond: (o.user_id = u.id)
        ->  Seq Scan on orders o  (cost=0.00..3.50 rows=500 width=8)
        ->  Hash  (cost=5.00..5.00 rows=100 width=40)
              ->  Seq Scan on users u  (cost=0.00..5.00 rows=100 width=40)
                    Filter: (created_at > (now() - '30 days'::interval))
```

### Reading the Plan

1. **Start at the bottom** - This executes first
2. **Work your way up** - Each node feeds into parent
3. **Look for expensive operations** - Seq Scan, Sort, Hash
4. **Check row estimates** - Compare "Rows" to "Actual Rows"
5. **Identify join strategy** - Nested Loop vs Hash vs Merge
6. **Find the bottleneck** - Usually the node with highest cost

### Interpretation Tips

```sql
-- Seq Scan with filter = bad (should use index)
Seq Scan on users u
  Filter: (created_at > '2024-01-01')

-- Index Scan = good
Index Scan using idx_users_created on users u

-- Index Only Scan = best (doesn't access table)
Index Only Scan using idx_users_email on users

-- Cardinality estimate way off = problem
Filter: (status = 'active')
Rows: 5000 (estimated) vs 45 (actual)
-- Fix: Run ANALYZE to update statistics
```

## Query Plans Across Databases

### MySQL EXPLAIN

```sql
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE email = 'user@example.com';
EXPLAIN FORMAT=TRADITIONAL SELECT * FROM users WHERE email = 'user@example.com';

-- EXPLAIN EXTENDED (MySQL 5.7+)
EXPLAIN EXTENDED SELECT * FROM users WHERE email = 'user@example.com';
SHOW WARNINGS;
```

### Snowflake EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
-- Shows plan without executing

EXPLAIN USING TABULAR SELECT * FROM users WHERE email = 'user@example.com';
-- Better human-readable format
```

### BigQuery EXPLAIN

```sql
EXPLAIN SELECT * FROM project.dataset.users WHERE email = 'user@example.com';
-- Shows estimated bytes, slots, and execution stages
```

## Best Practices

- ✅ **Always EXPLAIN**: Never guess; always verify with EXPLAIN
- ✅ **Use ANALYZE**: Compare estimated vs actual rows
- ✅ **Test with Data**: Estimates wrong? Run ANALYZE statistics
- ✅ **Benchmark Both**: Time before and after optimization
- ✅ **Monitor Production**: Real query patterns may differ from dev
