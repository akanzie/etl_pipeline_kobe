# Report — KOBE-00008

## 1. Kết quả chính
- Đã bỏ hẳn `bronze_calendar_raw` và `master_calendar` khỏi pipeline PySpark.
- Đã giữ lại `sale_date` ở `fact_daily_sales` và derive thêm `month_id`, `year`, `month`, `day`.
- Đã chuẩn hóa `fact_daily_customer_count` để ưu tiên grain ngày nếu nguồn có cột ngày, đồng thời vẫn fallback được từ `month_id`.
- Đã sửa `gold_sales_cube` sang aggregate theo ngày và join `customer_count` theo ngày để tránh fan-out dữ liệu từ tháng xuống ngày.
- Đã điều chỉnh `cluster_by` của `gold_sales_cube` còn 4 cột để tương thích giới hạn Liquid clustering của Databricks.

## 2. File thay đổi
- `transformations/bronze/bronze_calendar_raw.py` (xóa)
- `transformations/bronze/bronze_sales_raw.py`
- `transformations/bronze/bronze_customer_count_raw.py`
- `transformations/silver/fact_daily_sales.py`
- `transformations/silver/fact_daily_customer_count.py`
- `transformations/silver/master_calendar.py` (xóa)
- `transformations/gold/gold_sales_cube.py`
- `docs/changes/KOBE-00008/spec-pack.md`
- `docs/architecture/medallion_databricks.md`
- `docs/standards/pyspark_transformations.md`

## 3. Tác động nghiệp vụ
- Gold trên Databricks giờ có đủ `year`, `month`, `day` để phục vụ dashboard và partition/filter linh hoạt hơn.
- Logic mới ưu tiên tính đúng hơn tính “đủ số”. Nếu `customer_count` không có grain ngày, pipeline sẽ không nhân bản KPI theo ngày một cách sai lệch.

## 4. Đề xuất tiếp theo
- Nếu muốn làm đẹp toàn bộ `@transformations`, nên thực hiện một change riêng để gom helper dùng chung cho Auto Loader, default columns và validation patterns.
- Nếu dashboard cần KPI theo ngày thật sự ổn định, upstream của `customer_count` nên bổ sung cột ngày thay vì chỉ gửi `month_id`.
