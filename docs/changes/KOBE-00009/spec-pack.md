# Spec Pack — KOBE-00009: Chuẩn hóa dimension category cho Gold Sales Cube

## 1. Thông tin chung
- **Ticket ID**: `KOBE-00009`
- **Mục tiêu**: Sửa `gold_sales_cube` theo schema business mới, đồng thời bổ sung dimension `master_categories` để thay thế cột `category` dạng text bằng `category_id`.
- **Phạm vi**: Pipeline Databricks/PySpark trong `transformations/` và tài liệu liên quan.
- **Trạng thái**: Approved

## 2. Bài toán nghiệp vụ
### 2.1. Vấn đề hiện tại
- `gold_sales_cube` đang giữ nhiều KPI mở rộng hơn nhu cầu hiện tại.
- Trục phân loại sản phẩm mới chỉ tồn tại dưới dạng text `category` trong `master_products`, chưa có master riêng để dùng như dimension ổn định ở tầng Gold.
- Schema Gold hiện tại chưa có các cột khóa thời gian business dạng `date`, `week`, `month` đúng như mockup người dùng yêu cầu.

### 2.2. Yêu cầu thay đổi
- Sửa schema output của `gold_sales_cube` về đúng tập cột sau:
  - `date`
  - `cooperative_id`
  - `region_id`
  - `business_model_id`
  - `category_id`
  - `store_id`
  - `product_id`
  - `week`
  - `month`
  - `total_amt`
  - `total_qty`
- Bổ sung `master_categories` ở tầng Silver để quản lý `category_id` và `category_name`.
- Không dùng `category` text trực tiếp trong output của Gold.

## 3. Thiết kế kỹ thuật
### 3.1. Grain dữ liệu Gold mới
- Grain logic của `gold_sales_cube` là:
  - `date`
  - `cooperative_id`
  - `region_id`
  - `business_model_id`
  - `category_id`
  - `store_id`
  - `product_id`
- `week` và `month` là thuộc tính dẫn xuất từ `date`, không phải nguồn thời gian gốc.
- `store_id` và `product_id` vẫn được coi là thành phần định danh thực tế của bản ghi Gold để tránh trùng dòng khi aggregate.

### 3.2. Dimension `master_categories`
- Nguồn sinh: `master_products`.
- Khóa tự nhiên: `category_name` sau khi chuẩn hóa `trim` và thay `NULL`/rỗng bằng `UNKNOWN`.
- `category_id` được sinh theo hàm băm xác định để bảo đảm:
  - idempotent giữa các lần chạy pipeline
  - không phụ thuộc thứ tự dữ liệu đến
  - tránh việc gán lại ID khi có category mới xuất hiện

### 3.3. Quy tắc tính toán Gold
- `date = yyyy-MM-dd` từ `sale_date`
- `week = YYYYWww` theo `sale_date`
- `month = yyyy-MM` từ `sale_date`
- `total_amt = SUM(sales_amount)`
- `total_qty = SUM(quantity_sold)`
- Không giữ lại các cột mở rộng ngoài yêu cầu hiện tại như:
  - `classification`
  - `customer_count`
  - `avg_unit_price`
  - `qty_pi`
  - `amt_pi`
  - `markdown_qty`

### 3.4. Chiến lược clustering trên Databricks
- `gold_sales_cube` dùng `cluster_by=["date", "cooperative_id", "region_id", "business_model_id"]`.
- Lý do: tương thích giới hạn 4 cột của Liquid clustering và vẫn ưu tiên trục thời gian cùng các dimension tổ chức chính.

## 4. Open Issues
- **OI-01**: Sơ đồ nghiệp vụ ban đầu mô tả các khóa như `cooperative_id`, `region_id`, `business_model_id`, `store_id` dưới dạng `int`. Repo hiện tại đang dùng khóa kiểu chuỗi cho các master cũ; change này giữ nguyên kiểu dữ liệu hiện hữu để tránh breaking change lan rộng ngoài phạm vi Databricks.
- **OI-02**: `category_id` được sinh bằng hàm băm xác định thay vì surrogate key tăng dần. Cách làm này ổn định cho pipeline nhưng không phù hợp nếu business yêu cầu quản trị mã category theo danh mục master bên ngoài.
- **OI-03**: Các service/model SQLAlchemy trong `src/` chưa được đồng bộ theo schema Gold mới trong change này vì user request đang tập trung vào pipeline Databricks.
