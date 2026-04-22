# Databricks Deployment Guide — KOBE ETL Pipeline

Để chạy pipeline này trên Databricks (sử dụng Unity Catalog), bạn cần thực hiện theo các bước sau:

## 1. Kết nối Git (Databricks Repos)
- Đẩy toàn bộ source code này lên một Git repository (GitHub/GitLab/Azure DevOps).
- Trên Databricks, vào mục **Repos** -> **Add Repo** và dán URL repository của bạn vào. Điều này giúp Databricks truy cập trực tiếp vào các file trong thư mục `transformations/`.

## 2. Tạo Delta Live Tables (DLT) Pipeline
Vào menu **Delta Live Tables** -> **Create Pipeline** và cấu hình như sau:

- **Pipeline name**: `Kobe_Sales_ETL`
- **Product edition**: `Advanced` (Bắt buộc để sử dụng tính năng `@dp.expect` - Data Quality).
- **Pipeline mode**: `Triggered` (Chạy theo lịch/thủ công) hoặc `Continuous` (Chạy liên tục cho streaming).
- **Source code**: Chọn tất cả các file trong thư mục:
  - `transformations/bronze/*.py` (Nếu có)
  - `transformations/silver/*.py`
  - `transformations/gold/*.py`
- **Destination**:
  - **Catalog**: Chọn catalog của bạn trong Unity Catalog (VD: `main`).
  - **Target schema**: Chọn schema mục tiêu (VD: `kobe_sales_analytics`).
- **Storage location**: (Tùy chọn) Đường dẫn trên DBFS/S3/ADLS để lưu trữ metadata.

## 3. Cấu hình Unity Catalog
Đảm bảo rằng Service Principal hoặc User chạy pipeline có quyền:
- `USE CATALOG` trên catalog mục tiêu.
- `USE SCHEMA` và `CREATE TABLE` trên schema mục tiêu.

## 4. Thứ tự thực thi (Lineage)
Databricks DLT sẽ tự động phân tích các hàm `@dp.table` và `@dp.view` để xác định thứ tự chạy:
1. Đọc dữ liệu từ `bronze_*`.
2. Thực hiện làm sạch và validate để tạo `silver_*`.
3. Join và Aggregate để tạo `gold_sales_cube`.

## 5. Lưu ý về Dữ liệu nguồn (Bronze)
- Pipeline hiện tại đang gọi `spark.readStream.table("bronze_customer_count_raw")`.
- Bạn cần đảm bảo các bảng `bronze_*` đã tồn tại trong Unity Catalog trước khi chạy pipeline này.

---
**Mẹo**: Bạn có thể sử dụng **Databricks Asset Bundles (DABs)** nếu muốn tự động hóa việc tạo Pipeline này bằng code (YAML).
