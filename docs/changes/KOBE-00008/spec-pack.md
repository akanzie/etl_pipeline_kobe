# Spec Pack — KOBE-00008: Chuẩn hóa trục thời gian cho Gold Databricks

## 1. Thông tin chung
- **Ticket ID**: `KOBE-00008`
- **Mục tiêu**: Sửa logic ETL PySpark ở tầng Gold để bỏ phụ thuộc `master_calendar`, đồng thời đưa trực tiếp `year`, `month`, `day` vào bảng `gold_sales_cube`.
- **Phạm vi**: Chỉ xử lý pipeline Databricks trong `transformations/` và tài liệu đi kèm cho thay đổi này.
- **Trạng thái**: Approved

## 2. Bài toán nghiệp vụ
### 2.1. Vấn đề hiện tại
- `gold_sales_cube` đang tổng hợp theo `month_id`, làm mất trục ngày ngay tại pipeline Databricks.
- `fact_daily_sales` cắt `sale_date` thành `month_id` quá sớm, khiến Gold không còn dữ liệu để phân tích theo ngày.
- `fact_daily_customer_count` join theo `month_id`, có nguy cơ nhân bản `customer_count` khi Gold chuyển sang grain ngày.
- `master_calendar` chỉ đóng vai trò time dimension, không còn cần thiết nếu có thể derive thời gian trực tiếp từ dữ liệu fact.

### 2.2. Yêu cầu thay đổi
- Loại bỏ `bronze_calendar_raw` và `master_calendar` khỏi luồng `@transformations`.
- Chuẩn hóa `sale_date` ở `fact_daily_sales` và derive:
  - `month_id`
  - `year`
  - `month`
  - `day`
- Chuẩn hóa `fact_daily_customer_count` theo cùng nguyên tắc, ưu tiên date thực tế nếu nguồn có cột ngày.
- Sửa `gold_sales_cube` để aggregate theo grain ngày và lưu trực tiếp `year`, `month`, `day`.

## 3. Thiết kế kỹ thuật
### 3.1. Grain dữ liệu mới
- `fact_daily_sales`: grain theo ngày/cửa hàng/sản phẩm/phân loại.
- `fact_daily_customer_count`: grain theo ngày/cửa hàng nếu nguồn có ngày; nếu nguồn chỉ có `month_id` thì chuẩn hóa về ngày đầu tháng để tránh nhân bản dữ liệu.
- `gold_sales_cube`: grain theo ngày + các business dimensions hiện hữu.

### 3.1.1. Chiến lược clustering trên Databricks
- `gold_sales_cube` dùng `cluster_by=["sale_date", "cooperative_id", "region_id", "business_model_id"]`.
- Lý do: Liquid clustering trên Databricks chỉ hỗ trợ tối đa 4 cột clustering.
- Các cột `year`, `month`, `day` vẫn được giữ trong output để phục vụ filter và dashboard, nhưng không dùng trực tiếp trong `cluster_by`.

### 3.2. Quy tắc tính toán Gold
- `total_qty = SUM(quantity_sold)`
- `total_amt = SUM(sales_amount)`
- `customer_count = MAX(customer_count)` trong cùng grain Gold
- `avg_unit_price = total_amt / total_qty`
- `qty_pi = total_qty / customer_count`
- `amt_pi = total_amt / customer_count`
- Chia cho `0` hoặc `NULL` phải trả về `NULL`, không tự nhân bản hoặc suy diễn thêm dữ liệu.

## 4. Open Issues
- **OI-01**: Nguồn `customer_count` hiện tại trong repo local mới thể hiện `month_id`. Nếu dữ liệu vận hành thực tế vẫn theo tháng, các KPI `qty_pi` và `amt_pi` ở grain ngày chỉ có ý nghĩa khi upstream bổ sung cột ngày thực tế.
- **OI-02**: Mô hình SQLAlchemy trong `src/` vẫn đang giữ `master_calendar`. Change này chủ động giới hạn ở Databricks/PySpark theo đúng phạm vi user yêu cầu.

## 5. Phương án làm đẹp `@transformations`
- Chuẩn hóa mỗi file transformation theo 3 khối: `read`, `normalize`, `select`.
- Dùng chung quy ước cột thời gian: `sale_date` hoặc `customer_date`, sau đó derive `month_id`, `year`, `month`, `day`.
- Giữ comment và `@dp.expect*` ở mức ngắn, chỉ mô tả ràng buộc nghiệp vụ.
- Tách helper dùng chung cho Auto Loader, audit columns và safe divide ở change kế tiếp nếu cần refactor rộng toàn bộ Bronze/Silver/Gold.
