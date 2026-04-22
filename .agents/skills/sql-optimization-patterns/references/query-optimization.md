# Query Optimization Patterns

Practical patterns for rewriting slow queries into fast ones.

## When to Use This Reference

Use when:

- Optimizing N+1 query problems
- Refactoring pagination
- Optimizing aggregations
- Transforming correlated subqueries
- Batch processing

---

## Pattern 1: Eliminate N+1 Queries

**Problem: Executing separate queries for related data**

```python
# Bad: N+1 query anti-pattern
users = db.query("SELECT * FROM users LIMIT 10")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    # Process orders
# Executes 1 query for users + 10 queries for orders = 11 total
```

**Solution: Use JOINs or Batch Loading**

```sql
-- Solution 1: JOIN (single query)
SELECT
    u.id, u.name,
    o.id as order_id, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id IN (1, 2, 3, 4, 5);
-- Returns 1 result set with nested structure

-- Solution 2: Batch query (2 queries total)
SELECT * FROM orders
WHERE user_id IN (1, 2, 3, 4, 5);
-- Then join in application layer
```

```python
# Good: Single query with JOIN or batch load
# Using JOIN
results = db.query("""
    SELECT u.id, u.name, o.id as order_id, o.total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.id IN (1, 2, 3, 4, 5)
""")

# Or batch load
users = db.query("SELECT * FROM users LIMIT 10")
user_ids = [u.id for u in users]
orders = db.query(
    "SELECT * FROM orders WHERE user_id IN (?)",
    user_ids
)
# Group orders by user_id in application
orders_by_user = {}
for order in orders:
    orders_by_user.setdefault(order.user_id, []).append(order)
```

## Pattern 2: Optimize Pagination

**Bad: OFFSET on Large Tables**

```sql
-- Slow for large offsets (must read and skip rows)
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 100000;  -- Very slow!
```

**Good: Cursor-Based Pagination**

```sql
-- Much faster: Use cursor (last seen timestamp)
SELECT * FROM users
WHERE created_at < '2024-01-15 10:30:00'  -- Last cursor
ORDER BY created_at DESC
LIMIT 20;

-- With composite sorting (id breaks ties)
SELECT * FROM users
WHERE (created_at, id) < ('2024-01-15 10:30:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Requires index
CREATE INDEX idx_users_cursor ON users(created_at DESC, id DESC);
```

## Pattern 3: Aggregate Efficiently

**Optimize COUNT Queries**

```sql
-- Bad: Counts all rows (slow on large tables)
SELECT COUNT(*) FROM orders;

-- Good: Use estimates for approximate counts
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'orders';

-- Good: Filter before counting
SELECT COUNT(*) FROM orders
WHERE created_at > NOW() - INTERVAL '7 days';

-- Better: Use index-only scan
CREATE INDEX idx_orders_created ON orders(created_at);
SELECT COUNT(*) FROM orders
WHERE created_at > NOW() - INTERVAL '7 days';
```

**Optimize GROUP BY**

```sql
-- Bad: Group by then filter
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 10;

-- Better: Filter first, then group
SELECT user_id, COUNT(*) as order_count
FROM orders
WHERE status = 'completed'
GROUP BY user_id
HAVING COUNT(*) > 10;

-- Best: Use covering index
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
```

## Pattern 4: Subquery Optimization

**Transform Correlated Subqueries**

```sql
-- Bad: Correlated subquery (runs for each row)
SELECT u.name, u.email,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u;

-- Good: JOIN with aggregation
SELECT u.name, u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name, u.email;

-- Better: Use window functions
SELECT DISTINCT ON (u.id)
    u.name, u.email,
    COUNT(o.id) OVER (PARTITION BY u.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

## Pattern 5: Use CTEs for Clarity

**Common Table Expressions (WITH clause)**

```sql
-- Break complex queries into readable steps
WITH recent_users AS (
    SELECT id, name, email
    FROM users
    WHERE created_at > NOW() - INTERVAL '30 days'
),
user_order_counts AS (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    WHERE created_at > NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT ru.name, ru.email, COALESCE(uoc.order_count, 0) as orders
FROM recent_users ru
LEFT JOIN user_order_counts uoc ON ru.id = uoc.user_id;
```

## Pattern 6: Window Functions

**Avoid self-joins with window functions**

```sql
-- Bad: Self-join for running total
SELECT
    o1.id,
    o1.total,
    SUM(o2.total) as running_total
FROM orders o1
JOIN orders o2 ON o1.id >= o2.id
GROUP BY o1.id, o1.total;

-- Good: Window function (much faster)
SELECT
    id,
    total,
    SUM(total) OVER (ORDER BY id) as running_total
FROM orders;

-- Ranking
SELECT
    user_id,
    total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rank
FROM orders;
```

## Best Practices

- ✅ **Filter Early**: Push WHERE clauses down before joins
- ✅ **Use Batch Loads**: Avoid N+1 queries
- ✅ **Cursor Pagination**: For large result sets
- ✅ **Window Functions**: Over self-joins and subqueries
- ✅ **Avoid OFFSET**: For pagination, use cursors
- ✅ **Test at Scale**: Optimization test with realistic data volume
