# Spec Pack — KOBE-00006: ETL Pipeline Kobe Sales

## 1. Thông tin chung
- **Ticket ID**: KOBE-00006
- **Mục tiêu**: Xây dựng pipeline dữ liệu chuẩn hóa theo trục ngang/dọc, phân tầng Master - Fact - Gold Cube cho hệ thống quản lý bán hàng Kobe.
- **Người thực hiện**: Antigravity (SDD Agent)
- **Trạng thái**: Draft

## 2. Đặc tả yêu cầu
### 2.1. Cấu trúc dữ liệu (Schema)
Hệ thống tuân thủ quy tắc đặt tên:
- `master_*`: Bảng danh mục.
- `fact_*`: Bảng sự kiện (grain theo tháng `YYYY-MM`).
- `gold_*`: Bảng tổng hợp (pre-aggregated) phục vụ query nhanh.

#### Trục quan hệ chính:
- `master_stores` -> `master_regions` (Area)
- `master_regions` -> `master_cooperatives` (Coop)
- `master_stores` -> `master_business_models`

### 2.2. Danh sách bảng
| Layer | Tên bảng | Mô tả |
|-------|----------|-------|
| Master | `master_cooperatives` | Danh sách Hợp tác xã |
| Master | `master_regions` | Danh sách Khu vực |
| Master | `master_business_models` | Mô hình kinh doanh |
| Master | `master_stores` | Danh sách Cửa hàng |
| Master | `master_products` | Danh sách Sản phẩm |
| Master | `master_calendar` | Trục thời gian (Tháng) |
| Fact | `fact_daily_sales` | Doanh thu theo tháng/cửa hàng/sản phẩm/phân loại |
| Fact | `fact_daily_customer_count`| Lượt khách theo tháng/cửa hàng |
| Gold | `gold_sales_cube` | Cube tổng hợp đa chiều (OLAP) |

## 3. Thiết kế kỹ thuật
### 3.1. Tech Stack
- **Ngôn ngữ**: Python 3.14+
- **Database Engine**: SQLAlchemy (sử dụng SQLite cho môi trường local/test).
- **Validation**: Pydantic v2.
- **Architecture**: Layered Architecture.

### 3.2. Cấu trúc thư mục (Dự kiến)
```text
src/
├── domain/                # Pydantic models (Entities)
├── infrastructure/        # Database connection, Repositories
├── application/           # ETL Logic, Services
└── core/                  # Config, Logging, Exceptions
scripts/
└── seed_data.py           # Script khởi tạo schema và data mẫu
main.py                    # Entry point chạy pipeline
```

### 3.3. Quy trình ETL
1. **Khởi tạo**: Tạo schema database dựa trên đặc tả SQL.
2. **Load Master**: Nạp dữ liệu vào các bảng `master_*`.
3. **Load Fact**: Nạp dữ liệu vào `fact_daily_sales` và `fact_daily_customer_count`.
4. **Build Gold**: Chạy query aggregate để đổ dữ liệu vào `gold_sales_cube`.

## 4. Kế hoạch triển khai (Implementation Plan)

### Bước 1: Thiết lập môi trường và Infrastructure
- [ ] Cấu trúc folder `src/`.
- [ ] File `src/infrastructure/database.py` quản lý engine và session.
- [ ] File `src/infrastructure/models.py` định nghĩa SQLAlchemy Base models.

### Bước 2: Định nghĩa Domain Models
- [ ] Tạo các Pydantic models tương ứng với Schema trong `src/domain/`.

### Bước 3: Xây dựng Application Services
- [ ] `MasterService`: Quản lý nạp dữ liệu danh mục.
- [ ] `SalesService`: Quản lý nạp dữ liệu Fact.
- [ ] `CubeService`: Chạy logic tổng hợp Gold Cube.

### Bước 4: Viết script Seed và Testing
- [ ] Script `scripts/seed_data.py` thực thi SQL mẫu từ yêu cầu.
- [ ] Viết Unit Test cho logic tổng hợp Cube.

## 5. Phụ lục: SQL Schema (Source of Truth)
```sql
-- (Nội dung SQL từ USER_REQUEST)
-- [Bản đầy đủ sẽ được cập nhật sau khi approve]
```

## 6. Kết quả thực hiện
- **Cấu trúc Source Code**: Hoàn thành Layered Architecture tại `src/`.
- **Chế độ nạp dữ liệu**: 
  - `FULL_REBUILD`: Đã test và chạy thành công (nạp 18 bản ghi mẫu).
  - `INCREMENTAL`: Đã test và chạy thành công cho tháng cụ thể (nạp 9 bản ghi tháng 2024-04).
- **Transformations**: 
  - Đã đối soát giữa bản **PySpark** (`transformations/gold/gold_sales_cube.py`) và bản **SQLAlchemy** (`src/application/cube_service.py`).
  - Cả hai đều sử dụng công thức chuẩn:
    - `avg_unit_price = SUM(sales_amount) / SUM(quantity_sold)`
    - `qty_pi = SUM(quantity_sold) / MAX(customer_count)`
    - `amt_pi = SUM(sales_amount) / MAX(customer_count)`
  - Logic `@transformations` hiện tại đã **ổn** và sẵn sàng cho Production.

## 7. Hướng dẫn chạy
```powershell
$env:PYTHONPATH="."; $env:PYTHONIOENCODING="utf-8"
# Seed dữ liệu mẫu
python scripts/seed_data.py
# Chạy pipeline demo
python main.py
```

