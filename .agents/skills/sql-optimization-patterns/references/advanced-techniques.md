# Advanced Techniques

Advanced SQL optimization: materialized views, partitioning, and monitoring.

## When to Use This Reference

Use when:

- Pre-computing expensive queries
- Splitting large tables
- Setting up query monitoring
- Using advanced database features

---

## Materialized Views

Pre-compute expensive queries and refresh periodically.

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW user_order_summary AS
SELECT
    u.id,
    u.name,
    COUNT(o.id) as total_orders,
    SUM(o.total) as total_spent,
    MAX(o.created_at) as last_order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Add index to materialized view (speeds queries)
CREATE INDEX idx_user_summary_spent ON user_order_summary(total_spent DESC);

-- Refresh materialized view (updates data)
REFRESH MATERIALIZED VIEW user_order_summary;

-- Concurrent refresh (doesn't lock view)
REFRESH MATERIALIZED VIEW CONCURRENTLY user_order_summary;

-- Query materialized view (very fast)
SELECT * FROM user_order_summary
WHERE total_spent > 1000
ORDER BY total_spent DESC;
```

## Table Partitioning

Split large tables for better performance.

```sql
-- Range partitioning by date (PostgreSQL)
CREATE TABLE orders (
    id SERIAL,
    user_id INT,
    total DECIMAL,
    created_at TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Queries automatically use appropriate partition
SELECT * FROM orders
WHERE created_at BETWEEN '2024-02-01' AND '2024-02-28';
-- Only scans orders_2024_q1 partition (faster!)
```

## Query Hints

Control query optimization when planner makes wrong choices.

```sql
-- Force index usage (MySQL)
SELECT * FROM users
USE INDEX (idx_users_email)
WHERE email = 'user@example.com';

-- Force specific join type (PostgreSQL)
SET enable_nestloop = OFF;  -- Force hash or merge join
SET enable_seqscan = OFF;   -- Force index usage
SELECT * FROM large_table WHERE condition;

-- Parallel query
SET max_parallel_workers_per_gather = 4;
SELECT * FROM large_table WHERE condition;
```

## Monitoring & Maintenance

```sql
-- PostgreSQL: View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Find missing indexes
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;

-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Update statistics (improves query planning)
ANALYZE users;
VACUUM ANALYZE users;

-- Reindex corrupted index
REINDEX INDEX idx_users_email;
```

## Performance Tuning

```sql
-- PostgreSQL: Increase work memory for sorts/joins
SET work_mem = '256MB';

-- Increase buffer cache
-- In postgresql.conf: shared_buffers = '256MB'

-- Check table/index sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Analyze I/O statistics
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    heap_blks_read,
    heap_blks_hit
FROM pg_statio_user_tables
WHERE seq_scan > 0
ORDER BY heap_blks_read DESC;
```

## Best Practices

- ✅ **Materialized Views**: For complex aggregations computed nightly
- ✅ **Partitioning**: For very large tables (>1GB)
- ✅ **Query Hints**: Only when planner makes wrong choice
- ✅ **Regular Maintenance**: VACUUM, ANALYZE, reindex
- ✅ **Monitor Slow Queries**: Track performance over time
- ✅ **Connection Pooling**: Reuse database connections
