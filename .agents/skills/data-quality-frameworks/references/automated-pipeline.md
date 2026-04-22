# Automated Quality Pipeline

Complete implementation of orchestrated data quality checks across tables.

## When to Use This Reference

Use when:

- Building end-to-end quality validation pipelines
- Orchestrating checks across multiple tables
- Generating quality reports
- Blocking pipelines on quality failures

---

## Quality Pipeline Implementation

```python
# quality_pipeline.py
from dataclasses import dataclass
from typing import List, Dict, Any
import great_expectations as gx
from datetime import datetime

@dataclass
class QualityResult:
    table: str
    passed: bool
    total_expectations: int
    failed_expectations: int
    details: List[Dict[str, Any]]
    timestamp: datetime

class DataQualityPipeline:
    """Orchestrate data quality checks across tables"""

    def __init__(self, context: gx.DataContext):
        self.context = context
        self.results: List[QualityResult] = []

    def validate_table(self, table: str, suite: str) -> QualityResult:
        """Validate a single table against expectation suite"""

        checkpoint_config = {
            "name": f"{table}_validation",
            "config_version": 1.0,
            "class_name": "Checkpoint",
            "validations": [{
                "batch_request": {
                    "datasource_name": "warehouse",
                    "data_asset_name": table,
                },
                "expectation_suite_name": suite,
            }],
        }

        result = self.context.run_checkpoint(**checkpoint_config)

        # Parse results
        validation_result = list(result.run_results.values())[0]
        results = validation_result.results

        failed = [r for r in results if not r.success]

        return QualityResult(
            table=table,
            passed=result.success,
            total_expectations=len(results),
            failed_expectations=len(failed),
            details=[{
                "expectation": r.expectation_config.expectation_type,
                "success": r.success,
                "observed_value": r.result.get("observed_value"),
            } for r in results],
            timestamp=datetime.now()
        )

    def run_all(self, tables: Dict[str, str]) -> Dict[str, QualityResult]:
        """Run validation for all tables"""
        results = {}

        for table, suite in tables.items():
            print(f"Validating {table}...")
            results[table] = self.validate_table(table, suite)

        return results

    def generate_report(self, results: Dict[str, QualityResult]) -> str:
        """Generate quality report"""
        report = ["# Data Quality Report", f"Generated: {datetime.now()}", ""]

        total_passed = sum(1 for r in results.values() if r.passed)
        total_tables = len(results)

        report.append(f"## Summary: {total_passed}/{total_tables} tables passed")
        report.append("")

        for table, result in results.items():
            status = "✅" if result.passed else "❌"
            report.append(f"### {status} {table}")
            report.append(f"- Expectations: {result.total_expectations}")
            report.append(f"- Failed: {result.failed_expectations}")

            if not result.passed:
                report.append("- Failed checks:")
                for detail in result.details:
                    if not detail["success"]:
                        report.append(f"  - {detail['expectation']}: {detail['observed_value']}")
            report.append("")

        return "\n".join(report)

# Usage
context = gx.get_context()
pipeline = DataQualityPipeline(context)

tables_to_validate = {
    "orders": "orders_suite",
    "customers": "customers_suite",
    "products": "products_suite",
}

results = pipeline.run_all(tables_to_validate)
report = pipeline.generate_report(results)

# Fail pipeline if any table failed
if not all(r.passed for r in results.values()):
    print(report)
    raise ValueError("Data quality checks failed!")
```

## Integration with Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def run_quality_checks(**context):
    """Airflow task for quality validation"""
    from quality_pipeline import DataQualityPipeline
    import great_expectations as gx

    gx_context = gx.get_context()
    pipeline = DataQualityPipeline(gx_context)

    tables = {
        "orders": "orders_suite",
        "customers": "customers_suite",
    }

    results = pipeline.run_all(tables)
    report = pipeline.generate_report(results)

    # Push report to XCom
    context['task_instance'].xcom_push(key='quality_report', value=report)

    # Fail if any table failed
    if not all(r.passed for r in results.values()):
        raise ValueError("Data quality validation failed")

with DAG(
    'quality_validation',
    default_args={'retries': 0},
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    quality_check = PythonOperator(
        task_id='validate_data_quality',
        python_callable=run_quality_checks,
        provide_context=True,
    )
```

## Best Practices

- **Orchestration**: Run validation as a dependency before downstream tasks
- **Reporting**: Generate comprehensive reports for debugging
- **Blocking**: Fail pipelines on critical quality issues
- **Monitoring**: Track quality metrics over time
- **Alerting**: Notify teams when quality degrades
- **Documentation**: Maintain runbooks for common failures
