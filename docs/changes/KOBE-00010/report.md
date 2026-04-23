# Report — KOBE-00010

## 1. Kết quả chính
- Đã đồng bộ pipeline Databricks sang catalog `tmn_kobe`.
- Đã đặt schema mặc định của pipeline là `default` trong `databricks_pipeline_config.json`.
- Đã sửa toàn bộ dataset persisted trong `transformations/` sang tên fully-qualified theo Unity Catalog:
  - Bronze vào `tmn_kobe.default.*`
  - Master vào `tmn_kobe.master.*`
  - Fact và cube vào `tmn_kobe.fact.*`
- Đã đổi tên vật lý của các bảng business để bám theo schema nghiệp vụ:
  - `tmn_kobe.master.products`
  - `tmn_kobe.master.stores`
  - `tmn_kobe.master.regions`
  - `tmn_kobe.master.cooperatives`
  - `tmn_kobe.master.business_models`
  - `tmn_kobe.master.categories`
  - `tmn_kobe.fact.daily_sales`
  - `tmn_kobe.fact.daily_customer_count`
  - `tmn_kobe.fact.sales_cube`

## 2. File thay đổi
- `databricks_pipeline_config.json`
- `transformations/bronze/*.py`
- `transformations/silver/master_business_models.py`
- `transformations/silver/master_cooperatives.py`
- `transformations/silver/master_products.py`
- `transformations/silver/master_regions.py`
- `transformations/silver/master_stores.py`
- `transformations/silver/master_categories.py`
- `transformations/silver/fact_daily_customer_count.py`
- `transformations/silver/fact_daily_sales.py`
- `transformations/gold/gold_sales_cube.py`
- `docs/changes/KOBE-00010/spec-pack.md`
- `docs/changes/KOBE-00010/report.md`
- `docs/changes/KOBE-00010/test-results.md`
- `docs/architecture/medallion_databricks.md`
- `docs/standards/pyspark_transformations.md`

## 3. Tác động nghiệp vụ
- Code pipeline không còn phụ thuộc vào schema mặc định ngầm định của workspace hoặc file pipeline.
- Tên bảng trong code khớp hơn với cấu trúc hiển thị trên Catalog Explorer của `tmn_kobe`.
- Việc tách schema `master` và `fact` giúp downstream query rõ ràng hơn khi phân quyền và khai thác dữ liệu.

## 4. Lưu ý
- Change này chỉ đồng bộ namespace Databricks/PySpark. Các model SQLAlchemy ở `src/` vẫn giữ naming cũ và chưa phản ánh trực tiếp cấu trúc `tmn_kobe.master/*`, `tmn_kobe.fact/*`.
- Logic biến đổi dữ liệu hiện có được giữ nguyên; change này không sửa lại công thức hoặc grain ngoài phần tên vật lý của bảng.
