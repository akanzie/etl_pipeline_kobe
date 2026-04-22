# Spec Pack — KOBE-00007: Advanced Sales Analytics & Anomaly Detection

## 1. Thông tin chung
- **Ticket ID**: KOBE-00007
- **Mục tiêu**: Nâng cấp pipeline với tính năng theo dõi lịch sử giá (SCD Type 2), phân tích hiệu quả giảm giá và phát hiện dữ liệu bất thường.
- **Trạng thái**: Draft

## 2. Đặc tả yêu cầu nâng cao
### 2.1. SCD Type 2 cho Master Products
- Cần theo dõi sự thay đổi giá sản phẩm theo thời gian để tính toán chính xác biên lợi nhuận tại thời điểm bán.
- Bảng: `master_products_hist` (product_id, price, effective_date, end_date, is_current).

### 2.2. Phân tích Sell-through Rate (STR)
- Công thức: `STR = (Số lượng bán) / (Tồn kho đầu kỳ)`.
- Yêu cầu bảng: `fact_inventory_snapshot` (month_id, store_id, product_id, opening_stock).

### 2.3. Phát hiện dữ liệu bất thường (Anomaly Detection)
- Áp dụng Z-Score cho `sales_amount` trong tầng Silver.
- Các bản ghi có `|Z-Score| > 3` sẽ bị đánh dấu là `is_anomaly = True` và loại khỏi bảng Gold.

## 3. Thiết kế Schema mới
```sql
CREATE TABLE master_products_hist (
    hist_id         INTEGER PRIMARY KEY,
    product_id      INT NOT NULL,
    price           DECIMAL(10,2),
    effective_date  DATE,
    end_date        DATE,
    is_current      BOOLEAN DEFAULT TRUE
);

CREATE TABLE fact_inventory_snapshot (
    month_id        VARCHAR(7),
    store_id        VARCHAR(50),
    product_id      INT,
    opening_stock   INT,
    PRIMARY KEY (month_id, store_id, product_id)
);

CREATE TABLE gold_markdown_performance (
    month_id        VARCHAR(7),
    category        VARCHAR(100),
    markdown_type   VARCHAR(50),
    total_sales     DECIMAL(18,2),
    sell_through    DECIMAL(5,2),
    elasticity      DECIMAL(5,2)
);
```

## 4. Kế hoạch triển khai
- [ ] Cập nhật SQLAlchemy Models.
- [ ] Viết `SCDService` để quản lý lịch sử giá.
- [ ] Viết `QualityService` để tính toán Z-Score và lọc anomaly.
- [ ] Cập nhật `CubeService` để tích hợp STR và Price History.
