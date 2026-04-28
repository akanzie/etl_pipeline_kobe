from __future__ import annotations

from transformations.fact_gold import fact_daily_customer_count
from transformations.fact_gold import fact_daily_sales
from transformations.fact_gold.gold import gold_sales_cube
from transformations.master import master_business_models
from transformations.master import master_categories
from transformations.master import master_cooperatives
from transformations.master import master_products
from transformations.master import master_regions
from transformations.master import master_stores


def run_master(spark) -> None:
    master_business_models.run(spark)
    master_categories.run(spark)
    master_cooperatives.run(spark)
    master_products.run(spark)
    master_regions.run(spark)
    master_stores.run(spark)


def run_fact(spark) -> None:
    fact_daily_customer_count.run(spark)
    fact_daily_sales.run(spark)


def run_gold(spark) -> None:
    gold_sales_cube.run(spark)


def run_all(spark) -> None:
    run_master(spark)
    run_fact(spark)
    run_gold(spark)
