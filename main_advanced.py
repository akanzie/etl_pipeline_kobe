from src.infrastructure.database import SessionLocal, engine, Base
from src.application.advanced_etl_service import AdvancedETLService
from src.core.logging import logger
import sys

def run_advanced_pipeline():
    # 1. Khởi tạo DB (Bao gồm các bảng mới)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    adv_service = AdvancedETLService(db)

    print("=== ADVANCED PIPELINE KOBE SALES (KOBE-00007) ===")
    
    # MÔ PHỎNG 1: SCD Type 2 (Thay đổi giá sản phẩm)
    logger.info("Mô phỏng SCD Type 2 cho sản phẩm ID=1")
    adv_service.update_product_price_scd2(product_id=1, new_price=5000.0)
    adv_service.update_product_price_scd2(product_id=1, new_price=5500.0)

    # MÔ PHỎNG 2: Phát hiện bất thường (Anomaly Detection)
    logger.info("Đang kiểm tra bất thường cho dữ liệu tháng 2024-03")
    valid_data = adv_service.detect_and_filter_anomalies(month_id="2024-03")
    logger.info(f"Số lượng bản ghi hợp lệ sau khi lọc: {len(valid_data)}")

    # MÔ PHỎNG 3: Markdown Analysis (Sell-through Rate)
    logger.info("Đang tổng hợp Gold Markdown Analysis")
    adv_service.build_markdown_analysis(month_id="2024-03")

    print("\n=== HOÀN THÀNH ADVANCED PIPELINE ===")
    db.close()

if __name__ == "__main__":
    run_advanced_pipeline()
