from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4


def _quote_name(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def quote_table_name(table_name: str) -> str:
    return ".".join(_quote_name(part) for part in table_name.split("."))


def merge_dataframe(
    spark,
    source_df,
    *,
    target_table: str,
    key_columns: Sequence[str],
) -> None:
    if not key_columns:
        raise ValueError("key_columns is required for idempotent MERGE.")

    deduplicated_source = source_df.dropDuplicates(list(key_columns))
    temp_view_name = f"_tmp_upsert_{uuid4().hex}"
    deduplicated_source.createOrReplaceTempView(temp_view_name)

    key_condition = " AND ".join(
        f"target.{_quote_name(column)} <=> source.{_quote_name(column)}"
        for column in key_columns
    )
    merge_sql = f"""
        MERGE INTO {quote_table_name(target_table)} AS target
        USING {_quote_name(temp_view_name)} AS source
        ON {key_condition}
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """

    try:
        spark.sql(merge_sql)
    finally:
        spark.catalog.dropTempView(temp_view_name)
