# Data Contracts

Producer/consumer agreements using data contracts specification.

## When to Use This Reference

Use when:

- Establishing data contracts between teams
- Defining SLAs for data products
- Documenting data schemas and quality expectations
- Implementing contract-driven data development

---

## Data Contract Specification

```yaml
# contracts/orders_contract.yaml
apiVersion: datacontract.com/v1.0.0
kind: DataContract
metadata:
  name: orders
  version: 1.0.0
  owner: data-platform-team
  contact: data-team@company.com

info:
  title: Orders Data Contract
  description: Contract for order event data from the ecommerce platform
  purpose: Analytics, reporting, and ML features

servers:
  production:
    type: snowflake
    account: company.us-east-1
    database: ANALYTICS
    schema: CORE

terms:
  usage: Internal analytics only
  limitations: PII must not be exposed in downstream marts
  billing: Charged per query TB scanned

schema:
  type: object
  properties:
    order_id:
      type: string
      format: uuid
      description: Unique order identifier
      required: true
      unique: true
      pii: false

    customer_id:
      type: string
      format: uuid
      description: Customer identifier
      required: true
      pii: true
      piiClassification: indirect

    total_amount:
      type: number
      minimum: 0
      maximum: 100000
      description: Order total in USD

    created_at:
      type: string
      format: date-time
      description: Order creation timestamp
      required: true

    status:
      type: string
      enum: [pending, processing, shipped, delivered, cancelled]
      description: Current order status

quality:
  type: SodaCL
  specification:
    checks for orders:
      - row_count > 0
      - missing_count(order_id) = 0
      - duplicate_count(order_id) = 0
      - invalid_count(status) = 0:
          valid values: [pending, processing, shipped, delivered, cancelled]
      - freshness(created_at) < 24h

sla:
  availability: 99.9%
  freshness: 1 hour
  latency: 5 minutes
```

## Contract Versioning

```yaml
# Evolving contracts with semantic versioning
metadata:
  version: 2.0.0  # Breaking change (removed column)
  # version: 1.1.0  # New optional field (minor)
  # version: 1.0.1  # Documentation update (patch)

changelog:
  - version: 2.0.0
    date: 2024-03-01
    changes:
      - Removed deprecated shipping_address field
      - Added structured address object
  - version: 1.1.0
    date: 2024-02-01
    changes:
      - Added optional discount_code field
```

## Contract Validation

```python
# Validate data against contract
from datacontract.cli import DataContract

contract = DataContract.from_file("contracts/orders_contract.yaml")
result = contract.validate(data_source="snowflake://warehouse/orders")

if not result.is_valid():
    for error in result.errors:
        print(f"Validation Error: {error}")
    raise ValueError("Data contract validation failed")
```

## Best Practices

- **Explicit Agreements**: Formalize producer/consumer expectations
- **Version Contracts**: Use semantic versioning for schema changes
- **Document SLAs**: Include availability, freshness, latency guarantees
- **PII Classification**: Mark PII fields and their classification level
- **Quality Specs**: Include validation rules in the contract
- **Change Management**: Review and approve contract changes
