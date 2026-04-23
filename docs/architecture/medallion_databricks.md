# Medallion Databricks

## Mục tiêu
Tài liệu này mô tả nguyên tắc thiết kế cho pipeline Databricks trong thư mục `transformations/`.

## Quy tắc trục thời gian
- Không dùng bảng `master_calendar` làm time dimension trong DLT/PySpark.
- Tầng Silver phải giữ cột ngày nghiệp vụ gốc (`sale_date`, `customer_date`, hoặc tương đương).
- Các cột `month_id`, `year`, `month`, `day` phải được derive trực tiếp từ cột ngày gốc.
- Tầng Gold chỉ được join theo grain thực tế của dữ liệu thời gian; không được nhân bản dữ liệu tháng xuống ngày.

## Quy tắc aggregate Gold
- Gold ưu tiên grain sát với nghiệp vụ gốc hơn là ép về grain tháng.
- KPI có mẫu số bằng `0` hoặc `NULL` phải trả về `NULL` để tránh tạo chỉ số sai.
- Mọi thay đổi về grain thời gian phải cập nhật `docs/changes/<TICKET>/spec-pack.md` trước khi mở rộng sang layer khác.
- Khi một dimension nghiệp vụ mới chưa có master riêng, được phép suy ra master ở tầng Silver từ khóa tự nhiên đã chuẩn hóa.
- ID của dimension suy ra phải mang tính xác định và idempotent giữa các lần chạy pipeline; không dùng cách đánh số phụ thuộc thứ tự dữ liệu đến.

## Quy tắc namespace Unity Catalog
- Bronze publish vào schema `default` của catalog nghiệp vụ.
- Dimension/master publish vào schema `master`.
- Fact và cube publish vào schema `fact`, trừ khi có đặc tả khác trong `spec-pack`.
- Với dataset persisted, ưu tiên dùng tên fully-qualified `catalog.schema.table` trong cả chiều đọc và ghi để tránh lệ thuộc cấu hình mặc định của pipeline.
