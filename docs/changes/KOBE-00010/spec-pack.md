# Spec Pack — KOBE-00010: Đồng bộ namespace Unity Catalog `tmn_kobe`

## 1. Thông tin chung
- **Ticket ID**: `KOBE-00010`
- **Mục tiêu**: Đồng bộ pipeline Databricks để publish và đọc dữ liệu đúng theo catalog `tmn_kobe` và các schema con đang dùng thực tế.
- **Phạm vi**: `databricks_pipeline_config.json`, toàn bộ `transformations/`, và tài liệu sống liên quan đến quy ước namespace Databricks.
- **Trạng thái**: Approved

## 2. Bài toán nghiệp vụ
### 2.1. Vấn đề hiện tại
- Các file transformation hiện đang dùng tên bảng không fully-qualified, nên vị trí publish phụ thuộc vào cấu hình mặc định của pipeline.
- `databricks_pipeline_config.json` đang để `target` là `kobe_sales_catalog`, không phản ánh đúng catalog/schema Unity Catalog đang được sử dụng thực tế.
- Catalog Explorer đang tổ chức dữ liệu dưới catalog `tmn_kobe` với các schema như `default`, `master`, `fact`, nhưng code chưa bám theo cấu trúc này.

### 2.2. Yêu cầu thay đổi
- Cập nhật pipeline để mọi bảng Databricks được publish/read theo đúng namespace `tmn_kobe`.
- Dùng tên fully-qualified trong `@dp.table`, `@dp.materialized_view` và `spark.read.table(...)` cho các dataset persisted.
- Chuẩn hóa tên vật lý bảng theo schema nghiệp vụ thay vì giữ prefix layer trong tên bảng.

## 3. Thiết kế kỹ thuật
### 3.1. Cấu hình mặc định pipeline
- `catalog = tmn_kobe`
- `target = default`

### 3.2. Mapping dataset
#### Bronze
- `tmn_kobe.default.bronze_business_models_raw`
- `tmn_kobe.default.bronze_cooperatives_raw`
- `tmn_kobe.default.bronze_customer_count_raw`
- `tmn_kobe.default.bronze_products_raw`
- `tmn_kobe.default.bronze_regions_raw`
- `tmn_kobe.default.bronze_sales_raw`
- `tmn_kobe.default.bronze_stores_raw`

#### Master
- `tmn_kobe.master.business_models`
- `tmn_kobe.master.cooperatives`
- `tmn_kobe.master.products`
- `tmn_kobe.master.regions`
- `tmn_kobe.master.stores`
- `tmn_kobe.master.categories`

#### Fact
- `tmn_kobe.fact.daily_sales`
- `tmn_kobe.fact.daily_customer_count`
- `tmn_kobe.fact.sales_cube`

### 3.3. Quy tắc đặt tên
- Schema thể hiện domain nghiệp vụ: `default`, `master`, `fact`.
- Tên bảng vật lý không lặp lại prefix schema.
- Các dataset persisted phải dùng tên fully-qualified để tránh phụ thuộc vào schema mặc định của file hoặc pipeline.
- Temporary view trong pipeline có thể giữ tên nội bộ nếu không publish ra Unity Catalog.

## 4. Open Issues
- **OI-01**: Change này chỉ đồng bộ nhánh Databricks/PySpark. Các model/service local trong `src/` chưa được sửa theo namespace mới vì không phải nguồn lưu trữ Unity Catalog.
- **OI-02**: Giả định bảng Gold đích là `tmn_kobe.fact.sales_cube`. Nếu workspace thực tế đang yêu cầu tên khác, cần đổi lại ở một change tiếp theo.
- **OI-03**: Change này không can thiệp tới các schema khác trong catalog như `auth`, `config`, `menu` vì chưa có transformation nào publish vào đó.
