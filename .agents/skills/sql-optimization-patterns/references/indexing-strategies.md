# Indexing Strategies

Comprehensive guide to index types, design, and best practices.

## When to Use This Reference

Use when:

- Designing indexes for analytics workloads
- Choosing between B-tree, hash, GIN, BRIN indexes
- Creating composite indexes
- Optimizing specific query patterns

---

## Index Types

```sql
-- Standard B-Tree index (default)
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index (index subset of rows)
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Covering index (include additional columns)
CREATE INDEX idx_users_email_covering ON users(email)
INCLUDE (name, created_at);

-- Full-text search index
CREATE INDEX idx_posts_search ON posts
USING GIN(to_tsvector('english', title || ' ' || body));

-- JSONB index
CREATE INDEX idx_metadata ON events USING GIN(metadata);
```

## Index Design Principles

### Selectivity Matters

```sql
-- Good: Index on selective column
CREATE INDEX idx_users_status ON users(status);
-- Why? Only 2-3 values ('active', 'inactive', 'suspended') = high selectivity

-- Bad: Index on low-selectivity column
CREATE INDEX idx_orders_completed ON orders(is_completed);
-- Why? Usually 50/50 split = low selectivity, limited benefit

-- Good: Composite index ordered by selectivity
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- user_id more selective than status, so put first
```

### Composite Index Order

```sql
-- Columns should be ordered:
-- 1. Equality conditions (WHERE column =)
-- 2. Range conditions (WHERE column >)
-- 3. Sorting (ORDER BY)

-- Query pattern
WHERE user_id = 123 AND created_at > '2024-01-01' ORDER BY created_at DESC

-- Correct index order
CREATE INDEX idx_orders ON orders(user_id, created_at);
-- user_id (=) first, created_at (range) second
```

### Partial Indexes

```sql
-- Index only "active" rows (saves space, speeds inserts)
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- Query that uses the index
SELECT * FROM users
WHERE status = 'active' AND email = 'user@example.com';

-- Query that CAN'T use the index (filter not in index condition)
SELECT * FROM users
WHERE status = 'inactive' AND email = 'user@example.com';
```

## Avoiding Indexing Problems

### Over-Indexing

```sql
-- Bad: Too many indexes slow down all writes
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created ON users(created_at);
CREATE INDEX idx_users_updated ON users(updated_at);
-- Each INSERT/UPDATE/DELETE now updates all 4 indexes!

-- Better: Only index columns frequently filtered
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created ON users(created_at);
-- Keep name and updated_at unindexed unless needed
```

### Unused Indexes

```sql
-- Find unused indexes (PostgreSQL)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Drop unused indexes
DROP INDEX idx_users_name;
```

### Index Not Being Used

```sql
-- Common problem: Function in WHERE prevents index use
-- Index: ON users(email)
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
-- Doesn't use index!

-- Solution 1: Create functional index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Solution 2: Use exact match without function
SELECT * FROM users WHERE email = 'USER@EXAMPLE.COM';

-- Solution 3: Normalize data in application
```

## Index Maintenance

```sql
-- PostgreSQL: Update statistics (indexes use stats)
ANALYZE users;
ANALYZE VERBOSE users;

-- PostgreSQL: Vacuum (reclaim space)
VACUUM ANALYZE users;
VACUUM FULL users;  -- Reclaim space (locks table)

-- PostgreSQL: Reindex corrupted or bloated index
REINDEX INDEX idx_users_email;
REINDEX TABLE users;

-- Monitor index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Best Practices

- ✅ **Selectivity First**: Index on columns with high selectivity
- ✅ **Composite Order**: Equality → Range → Sorting
- ✅ **Partial Indexes**: When filtering on same condition repeatedly
- ✅ **Covering Indexes**: Include columns for index-only scans
- ✅ **Avoid Over-Indexing**: Every index slows writes
- ✅ **Monitor Indexes**: Drop unused indexes regularly
- ✅ **Update Statistics**: Run ANALYZE after bulk changes
