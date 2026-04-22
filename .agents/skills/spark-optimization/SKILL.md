---
name: spark-optimization
description: Specialist in Apache Spark performance optimization—partitioning strategies, memory tuning, shuffle reduction, and job profiling for production systems. Use when optimizing Spark jobs, tuning performance, reducing costs, profiling applications, or scaling Spark workloads.
version: 2.0.0
dependencies:
  - senior-data-engineer
tags:
  - spark
  - optimization
  - performance
---
- performance
- distributed-computing

---

# Spark Optimization - Performance Tuning

## Overview

The Spark Optimization skill focuses on diagnosing and fixing performance bottlenecks in Apache Spark jobs. This is a specialized, deep-focus skill for when you have a Spark job that's slow, consuming too much memory, or not scaling efficiently.

Use this skill when:

- A Spark job exceeds its SLA or budget
- You need to debug why a job is slower than expected
- You're optimizing for large-scale data processing
- Shuffles, skew, or memory pressure are causing failures
- You need to choose between partitioning strategies or join algorithms

## Core Capabilities

- **Performance Profiling**: Read Spark UI, identify bottlenecks (shuffle, GC, serialization, I/O)
- **Partitioning Optimization**: Right-size partitions, implement skew handling, partition pruning
- **Join Optimization**: Choose between broadcast, sort-merge, and bucket joins based on data characteristics
- **Memory Tuning**: Optimize executor memory, cache strategy, and GC behavior
- **Serialization**: Configure Kryo, choose columnar formats for large data
- **Caching Strategy**: Identify what to cache, when to cache, and when to spill

## When to Use

## Workflow / Process

### Phase 1: Diagnosis

1. Enable Spark UI and run job to completion
2. Analyze executor usage, task durations, and shuffle size
3. Identify bottleneck: CPU, memory, I/O, or scheduling

### Phase 2: Root Cause Analysis

1. Check for data skew (uneven task durations)
2. Review join strategy (broadcast vs sort-merge vs bucket)
3. Analyze partition count and size
4. Evaluate serialization and format choices

### Phase 3: Optimization

1. Apply targeted fix (e.g., repartition, broadcast join, caching)
2. Measure impact: runtime, memory, cost
3. Iterate if improvements insufficient

### Phase 4: Validation

1. Test with production data volume and characteristics
2. Monitor side effects (new bottlenecks, memory pressure)
3. Document optimization in runbook for future engineers

## Constraints

**Technical Constraints:**

- Cannot fundamentally change data or algorithm (that's architect/pipeline-engineer role)
- Optimizations must not sacrifice correctness or data consistency

**Scope Constraints:**

- In Scope: Spark configuration tuning, query optimization, serialization, caching strategy
- Out of Scope: Infrastructure provisioning, algorithm redesign, non-Spark systems

## Reference Examples

See `examples/` directory for:

- Partitioning strategies and skew handling
- Join algorithm comparisons (broadcast, sort-merge, bucket)
- Memory tuning and caching patterns
- Serialization and format optimization
- Detailed Spark UI analysis walkthroughs

---

**Version History:**

- 1.0 (2026-01-24): Spark-focused optimization skill

    skew_ratio = stats["max"] / stats["avg"]
    print(f"Skew ratio: {skew_ratio:.2f}x (>2x indicates skew)")

```

## Configuration Cheat Sheet

```python
# Production configuration template
spark_configs = {
    # Adaptive Query Execution (AQE)
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",

    # Memory
    "spark.executor.memory": "8g",
    "spark.executor.memoryOverhead": "2g",
    "spark.memory.fraction": "0.6",
    "spark.memory.storageFraction": "0.5",

    # Parallelism
    "spark.sql.shuffle.partitions": "200",
    "spark.default.parallelism": "200",

    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.sql.execution.arrow.pyspark.enabled": "true",

    # Compression
    "spark.io.compression.codec": "lz4",
    "spark.shuffle.compress": "true",

    # Broadcast
    "spark.sql.autoBroadcastJoinThreshold": "50MB",

    # File handling
    "spark.sql.files.maxPartitionBytes": "128MB",
    "spark.sql.files.openCostInBytes": "4MB",
}
```

## Best Practices

### Do's

- **Enable AQE** - Adaptive query execution handles many issues
- **Use Parquet/Delta** - Columnar formats with compression
- **Broadcast small tables** - Avoid shuffle for small joins
- **Monitor Spark UI** - Check for skew, spills, GC
- **Right-size partitions** - 128MB - 256MB per partition

### Don'ts

- **Don't collect large data** - Keep data distributed
- **Don't use UDFs unnecessarily** - Use built-in functions
- **Don't over-cache** - Memory is limited
- **Don't ignore data skew** - It dominates job time
- **Don't use `.count()` for existence** - Use `.take(1)` or `.isEmpty()`

## Resources

- [Spark Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Spark Configuration](https://spark.apache.org/docs/latest/configuration.html)
- [Databricks Optimization Guide](https://docs.databricks.com/en/optimizations/index.html)
