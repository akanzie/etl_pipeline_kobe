# PySpark Transformations

## Mục tiêu
Giữ cho các file trong `transformations/` ngắn, dễ review và nhất quán khi chạy trên Databricks.

## Cấu trúc khuyến nghị cho mỗi file
1. `read`: Đọc nguồn vào bằng `spark.readStream.table(...)` hoặc Auto Loader.
2. `normalize`: Chuẩn hóa kiểu dữ liệu, derive cột thời gian, áp default values.
3. `select`: Chỉ giữ các cột đầu ra thực sự cần cho layer kế tiếp.

## Quy ước thời gian
- Ưu tiên tên cột ngày rõ nghĩa như `sale_date` hoặc `customer_date`.
- `month_id` chỉ là cột dẫn xuất, không phải nguồn thời gian gốc.
- Khi cần aggregate theo ngày, bắt buộc phải giữ `year`, `month`, `day` trong output.

## Quy ước chất lượng dữ liệu
- `@dp.expect_or_fail` dùng cho khóa nghiệp vụ và cột ngày bắt buộc.
- `@dp.expect_or_drop` chỉ dùng cho dữ liệu nhiễu hoặc outlier đã được business chấp nhận loại bỏ.
- Công thức tính KPI phải xử lý an toàn với `NULL` và `0`.

## Gợi ý refactor tiếp theo
- Tách helper dùng chung cho Auto Loader.
- Tách helper chuẩn hóa ngày và audit columns.
- Gom các quy tắc chung vào module riêng nếu Databricks pipeline đã ổn định về import path.
