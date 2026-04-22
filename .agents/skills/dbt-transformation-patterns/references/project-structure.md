# Example: dbt Project Structure & Models

**Project**: Analytics Engineering Platform  
**Layer Strategy**: Staging → Intermediate → Marts  
**Primary Keys**: Required on all dims  
**Tests**: 100% unique + not_null on PKs  

---

## Project Structure

```
analytics/
├── dbt_project.yml
├── README.md
├── models/
│   ├── staging/
│   │   ├── _stg_sources.yml
│   │   ├── stg_orders.sql
│   │   ├── stg_customers.sql
│   │   └── stg_products.sql
│   ├── intermediate/
│   │   ├── _int_logic.yml
│   │   ├── int_orders_pivoted.sql
│   │   └── int_customer_segments.sql
│   └── marts/
│       ├── _mart_business.yml
│       ├── fct_orders.sql
│       ├── dim_customers.sql
│       ├── dim_products.sql
│       └── dim_dates.sql
├── macros/
│   ├── generate_alias_name.sql
│   └── cents_to_dollars.sql
├── tests/
│   └── unique_order_ids.sql
├── data/
│   └── country_codes.csv
└── seeds/
    └── _seeds.yml
```

---

## Layer 1: Staging (stg_*)

**Purpose**: First stop for raw data  
**Transformation Level**: Minimal  
**Quality Gates**: Schema validation only  
**Tests**: unique + not_null on source IDs

### stg_orders.sql

```sql
{{
    config(
        materialized='view',  -- Fast, no storage cost
        alias='stg_orders'
    )
}}

WITH source_data AS (
    SELECT
        order_id,
        customer_id,
        product_id,
        order_date,
        CAST(total_amount AS DECIMAL(10, 2)) as total_amount,
        status,
        created_at,
        updated_at
    FROM {{ source('ecommerce', 'orders') }}
)

SELECT * FROM source_data
WHERE order_id IS NOT NULL  -- Ensure no nulls
```

**Tests** (`_stg_sources.yml`):

```yaml
version: 2

models:
  - name: stg_orders
    description: "Cleaned source orders"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
      - name: total_amount
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

### stg_customers.sql

```sql
{{
    config(
        materialized='view',
        alias='stg_customers'
    )
}}

WITH source_data AS (
    SELECT
        customer_id,
        email,
        name,
        country,
        CAST(created_at AS DATE) as created_date,
        CAST(updated_at AS DATE) as updated_date
    FROM {{ source('ecommerce', 'customers') }}
)

SELECT * FROM source_data
WHERE customer_id IS NOT NULL
```

---

## Layer 2: Intermediate (int_*)

**Purpose**: Business logic transformation  
**Transformation Level**: Medium  
**Quality Gates**: Business rule validation  
**Tests**: Referential integrity  

### int_orders_pivoted.sql

```sql
{{
    config(
        materialized='table',  -- Persist for performance
        alias='int_orders_pivoted',
        indexes=[
            {'columns': ['order_id', 'order_status']}
        ]
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

orders_with_details AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.email as customer_email,
        c.name as customer_name,
        o.product_id,
        p.name as product_name,
        p.category,
        o.order_date,
        o.total_amount,
        {{ cents_to_dollars('o.total_amount') }} as total_dollars,  -- Macro
        CASE
            WHEN o.status = 'completed' THEN 1
            ELSE 0
        END as is_completed,
        o.status as order_status
    FROM orders o
    LEFT JOIN customers c USING (customer_id)
    LEFT JOIN products p USING (product_id)
)

SELECT * FROM orders_with_details
```

**Tests** (`_int_logic.yml`):

```yaml
models:
  - name: int_orders_pivoted
    columns:
      - name: order_id
        tests:
          - relationships:
              to: ref('stg_orders')
              field: order_id
      - name: customer_id
        tests:
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: product_id
        tests:
          - relationships:
              to: ref('stg_products')
              field: product_id
```

### int_customer_segments.sql

```sql
{{
    config(
        materialized='table',
        alias='int_customer_segments'
    )
}}

WITH customer_metrics AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) as lifetime_orders,
        SUM(total_amount) as lifetime_revenue,
        MAX(order_date) as last_order_date,
        DATE_DIFF(DAY, MAX(order_date), CURRENT_DATE()) as days_since_last_order
    FROM {{ ref('stg_orders') }}
    GROUP BY customer_id
),

segments AS (
    SELECT
        customer_id,
        lifetime_orders,
        lifetime_revenue,
        last_order_date,
        days_since_last_order,
        CASE
            WHEN lifetime_revenue > 10000 THEN 'VIP'
            WHEN lifetime_revenue > 1000 THEN 'Premium'
            WHEN lifetime_orders > 0 THEN 'Active'
            ELSE 'Inactive'
        END as customer_segment
    FROM customer_metrics
)

SELECT * FROM segments
```

---

## Layer 3: Marts (fct_/dim_*)

**Purpose**: Business-ready analytics tables  
**Transformation Level**: Heavy aggregation  
**Quality Gates**: Business metrics validation  
**Tests**: Referential integrity + row count thresholds

### fct_orders.sql

```sql
{{
    config(
        materialized='table',
        alias='fct_orders',
        indexes=[
            {'columns': ['order_date', 'customer_id']},
            {'columns': ['product_id', 'order_status']}
        ]
    )
}}

WITH orders_with_details AS (
    SELECT * FROM {{ ref('int_orders_pivoted') }}
),

final AS (
    SELECT
        order_id as order_pk,
        customer_id as customer_fk,
        product_id as product_fk,
        DATE_TRUNC('day', order_date) as order_date,
        total_amount as total_amount_cents,
        {{ cents_to_dollars('total_amount') }} as total_amount_usd,
        is_completed,
        order_status,
        CURRENT_TIMESTAMP() as dbt_created_at
    FROM orders_with_details
    WHERE order_date >= '2024-01-01'
)

SELECT * FROM final
```

**Tests** (`_mart_business.yml`):

```yaml
models:
  - name: fct_orders
    description: "Order facts for analytics"
    columns:
      - name: order_pk
        tests:
          - unique
          - not_null
      - name: customer_fk
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_pk
      - name: product_fk
        tests:
          - relationships:
              to: ref('dim_products')
              field: product_pk
    meta:
      owner: analytics
      sla_hours: 2
```

### dim_customers.sql

```sql
{{
    config(
        materialized='table',
        alias='dim_customers',
        unique_key='customer_pk',  -- Enables incremental updates
        tags=['dimension']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

segments AS (
    SELECT * FROM {{ ref('int_customer_segments') }}
),

final AS (
    SELECT
        c.customer_id as customer_pk,
        c.email,
        c.name as customer_name,
        c.country,
        c.created_date,
        c.updated_date,
        s.customer_segment,
        s.lifetime_orders,
        s.lifetime_revenue,
        s.days_since_last_order,
        CASE
            WHEN s.days_since_last_order < 30 THEN 'Active'
            WHEN s.days_since_last_order < 90 THEN 'At Risk'
            ELSE 'Inactive'
        END as customer_status,
        CURRENT_TIMESTAMP() as dbt_created_at
    FROM customers c
    LEFT JOIN segments s USING (customer_id)
)

SELECT * FROM final
```

**Tests** (`_mart_business.yml`):

```yaml
models:
  - name: dim_customers
    columns:
      - name: customer_pk
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
```

---

## Macros

### generate_alias_name.sql

```sql
{% macro generate_alias_name(custom_alias_name=none, node=none) -%}
    {%- if custom_alias_name is none -%}
        {{ node.name }}
    {%- else -%}
        {{ custom_alias_name | replace(' ', '_') }}
    {%- endif -%}
{%- endmacro %}
```

### cents_to_dollars.sql

```sql
{% macro cents_to_dollars(cents_column) %}
    ROUND({{ cents_column }} / 100.0, 2)
{% endmacro %}
```

---

## dbt_project.yml

```yaml
name: 'analytics'
version: '1.0.0'

config-version: 2

profile: 'analytics'
model-paths: ['models']
analysis-paths: ['analysis']
test-paths: ['tests']
data-paths: ['data']
macro-paths: ['macros']
snapshot-paths: ['snapshots']
target-path: 'target'
clean-targets:
  - 'target'
  - 'dbt_packages'

require-dbt-version: ['>=1.5.0', '<2.0.0']

models:
  analytics:
    staging:
      materialized: view
      tags: ['staging']
    intermediate:
      materialized: table
      tags: ['intermediate']
    marts:
      materialized: table
      tags: ['marts', 'daily']

seeds:
  country_codes:
    column_types:
      country_code: text
      country_name: text

on-run-start: "{{ run_started_at.isoformat() }} | {{ execute_macros() }}"
on-run-end: "{{ run_ended_at.isoformat() }}"

vars:
  start_date: '2024-01-01'
  currency: 'USD'
```

---

## Testing & Execution

### Run All Models

```bash
dbt run
# Output: 12 created in 0.15s
```

### Run Only Marts

```bash
dbt run -s tag:marts
# Output: 3 created in 0.08s
```

### Run Tests

```bash
dbt test
# 42 tests passed ✓
```

### Incremental Models

```sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='fail'
    )
}}

SELECT * FROM raw_orders

{% if execute %}
    WHERE order_date >= (
        SELECT MAX(order_date) FROM {{ this }}
    )
{% endif %}
```

---

## Best Practices Demonstrated

✅ **Clear naming**: stg_*(staging), int_* (intermediate), fct_/dim_* (facts/dimensions)  
✅ **Layered approach**: Raw → Cleaned → Business logic → Analytics  
✅ **Testing**: Unique + not_null on all PKs, referential integrity between layers  
✅ **Documentation**: YAML files describe each model and column  
✅ **Performance**: Indexes on frequently joined columns, table materialization  
✅ **Incremental processing**: Only new data processed (delta)  
✅ **DRY principle**: Macros for repeated logic (cents_to_dollars)  

---

**Next Step**: Hand off to `data-pipeline-engineer` for orchestration with Airflow.
