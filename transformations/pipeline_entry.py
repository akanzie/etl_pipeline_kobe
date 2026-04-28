"""Entrypoint cho Databricks/Lakeflow Bronze pipeline.

Include file này trong pipeline libraries để đăng ký các bảng Bronze.
Không include thư mục trực tiếp vì Databricks chỉ hỗ trợ file hoặc notebook.
"""

# Bronze
from transformations.bronze import bronze_business_models_raw  # noqa: F401
from transformations.bronze import bronze_categories_raw  # noqa: F401
from transformations.bronze import bronze_cooperatives_raw  # noqa: F401
from transformations.bronze import bronze_customer_count_raw  # noqa: F401
from transformations.bronze import bronze_products_raw  # noqa: F401
from transformations.bronze import bronze_regions_raw  # noqa: F401
from transformations.bronze import bronze_sales_raw  # noqa: F401
from transformations.bronze import bronze_stores_raw  # noqa: F401
