from src.infrastructure.database import SessionLocal
from src.application.cube_service import CubeService
import sys

def run_demo():
    db = SessionLocal()
    cube_service = CubeService(db)

    print("=== DEMO PIPELINE KOBE SALES ===")
    
    # Cách 1: Full Rebuild (Xóa hết làm lại)
    print("\n[BƯỚC 1] Chạy FULL_REBUILD cho toàn bộ dữ liệu lịch sử...")
    cube_service.transform_and_load(mode="FULL_REBUILD")

    # Cách 2: Incremental Load (Chỉ cập nhật cho tháng cụ thể)
    # Giả sử ta có dữ liệu mới cho tháng 2024-04
    print("\n[BƯỚC 2] Chạy INCREMENTAL cho tháng 2024-04...")
    cube_service.transform_and_load(mode="INCREMENTAL", month_ids=["2024-04"])

    print("\n=== HOÀN THÀNH DEMO ===")
    db.close()

if __name__ == "__main__":
    run_demo()
