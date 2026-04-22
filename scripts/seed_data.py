from sqlalchemy import text
from src.infrastructure.database import engine, SessionLocal, Base
from src.infrastructure.models import *

def seed():
    # Tạo bảng
    print("Đang khởi tạo các bảng...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Xóa dữ liệu cũ nếu có (để seed lại sạch sẽ)
        # Lệnh SQL mẫu từ yêu cầu
        sql_commands = [
            """
            INSERT OR REPLACE INTO master_cooperatives
                (cooperative_id, cooperative_code, cooperative_name, is_active)
            VALUES
                ('C001', 'COOP-HN', 'Hợp tác xã Hà Nội', 1),
                ('C002', 'COOP-HCM', 'Hợp tác xã TP.HCM', 1),
                ('C003', 'COOP-DN', 'Hợp tác xã Đà Nẵng', 1);
            """,
            """
            INSERT OR REPLACE INTO master_regions
                (region_id, region_code, region_name, cooperative_id, is_active)
            VALUES
                ('R001', 'AREA-HN', 'Khu vực Hà Nội', 'C001', 1),
                ('R002', 'AREA-HCM', 'Khu vực TP.HCM', 'C002', 1),
                ('R003', 'AREA-DN', 'Khu vực Đà Nẵng', 'C003', 1);
            """,
            """
            INSERT OR REPLACE INTO master_business_models
                (business_model_id, business_model_code, business_model_name, is_active)
            VALUES
                ('M001', 'SM', 'Cửa hàng nhỏ', 1),
                ('M002', 'GMS', 'Siêu thị tổng hợp', 1),
                ('M003', 'MINI', 'Siêu thị mini', 1);
            """,
            """
            INSERT OR REPLACE INTO master_stores
                (store_id, store_code, store_name, region_id, business_model_id, province, status, opening_date)
            VALUES
                ('S001', 'STORE-HN', 'Cửa hàng Hà Nội', 'R001', 'M001', 'Hà Nội', 'active', '2024-01-01'),
                ('S002', 'STORE-HCM', 'Cửa hàng TP.HCM', 'R002', 'M002', 'TP.HCM', 'active', '2024-01-01'),
                ('S003', 'STORE-DN', 'Cửa hàng Đà Nẵng', 'R003', 'M003', 'Đà Nẵng', 'active', '2024-01-01');
            """,
            """
            INSERT OR REPLACE INTO master_products
                (product_id, product_name, category, unit, price, is_active)
            VALUES
                (1, 'Mì Hảo Hảo Tôm Chua Cay', 'Mì ăn liền', 'Gói', 4500, 1),
                (2, 'Sữa tươi Vinamilk 1L', 'Sữa', 'Hộp', 35000, 1);
            """,
            """
            INSERT OR REPLACE INTO master_calendar
                (month_id, year, month_num, quarter, fiscal_year, is_closed)
            VALUES
                ('2024-03', 2024, 3, 1, 2024, 0),
                ('2024-04', 2024, 4, 2, 2024, 0);
            """,
            """
            INSERT OR REPLACE INTO fact_daily_sales
                (month_id, store_id, product_id, classification, quantity_sold, sales_amount)
            VALUES
                ('2024-03', 'S001', 1, '定番', 650, 2925000),
                ('2024-03', 'S001', 1, '家庭応援', 480, 2160000),
                ('2024-03', 'S001', 1, '特売', 1000, 3950000),
                ('2024-03', 'S002', 1, '定番', 720, 3240000),
                ('2024-03', 'S002', 1, '家庭応援', 510, 2295000),
                ('2024-03', 'S002', 1, '特売', 1020, 4080000),
                ('2024-03', 'S003', 2, '定番', 160, 5600000),
                ('2024-03', 'S003', 2, '家庭応援', 100, 3500000),
                ('2024-03', 'S003', 2, '特売', 240, 7200000),
                ('2024-04', 'S001', 1, '定番', 685, 3082500),
                ('2024-04', 'S001', 1, '家庭応援', 505, 2272500),
                ('2024-04', 'S001', 1, '特売', 1050, 4200000),
                ('2024-04', 'S002', 1, '定番', 760, 3420000),
                ('2024-04', 'S002', 1, '家庭応援', 530, 2385000),
                ('2024-04', 'S002', 1, '特売', 1100, 4400000),
                ('2024-04', 'S003', 2, '定番', 172, 6020000),
                ('2024-04', 'S003', 2, '家庭応援', 109, 3815000),
                ('2024-04', 'S003', 2, '特売', 260, 7800000);
            """,
            """
            INSERT OR REPLACE INTO fact_daily_customer_count
                (month_id, store_id, customer_count)
            VALUES
                ('2024-03', 'S001', 500),
                ('2024-03', 'S002', 620),
                ('2024-03', 'S003', 300),
                ('2024-04', 'S001', 520),
                ('2024-04', 'S002', 640),
                ('2024-04', 'S003', 310);
            """,
            """
            INSERT OR REPLACE INTO fact_inventory_snapshot
                (month_id, store_id, product_id, opening_stock)
            VALUES
                ('2024-03', 'S001', 1, 2000),
                ('2024-03', 'S002', 1, 2500),
                ('2024-03', 'S003', 2, 1000),
                ('2024-04', 'S001', 1, 1500),
                ('2024-04', 'S002', 1, 1800),
                ('2024-04', 'S003', 2, 800);
            """
        ]


        for cmd in sql_commands:
            db.execute(text(cmd))
        
        db.commit()
        print("Seed dữ liệu thành công!")
        
    except Exception as e:
        print(f"Lỗi khi seed dữ liệu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
