from src.infrastructure.database import SessionLocal, engine, Base
from src.application.bronze.ingestion_service import IngestionService
from src.application.silver.cleaning_service import CleaningService
from src.application.gold.analytics_service import AnalyticsService
from src.core.logging import logger

def run_medallion_pipeline():
    """
    Pipeline chính đồng bộ 100% với kiến trúc Databricks (Bronze -> Silver -> Gold).
    """
    logger.info("========== KHỞI CHẠY MEDALLION PIPELINE (LOCAL) ==========")
    
    # Khởi tạo Database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. BRONZE LAYER: Ingestion
        bronze_service = IngestionService(db)
        # (Giả định chúng ta có danh sách SQL commands từ seed_data hoặc file)
        # Ở đây dùng logic demo nạp dữ liệu thô
        logger.info("[STEP 1] Thực thi Bronze Ingestion...")
        
        # 2. SILVER LAYER: Cleaning & Validation
        silver_service = CleaningService(db)
        logger.info("[STEP 2] Thực thi Silver Cleaning cho tháng 2024-03...")
        silver_service.clean_and_validate_sales(month_id="2024-03")
        
        # 3. GOLD LAYER: Analytics & Aggregation
        gold_service = AnalyticsService(db)
        logger.info("[STEP 3] Thực thi Gold Transformation (Cube Build)...")
        gold_service.build_sales_cube(mode="INCREMENTAL", month_ids=["2024-03"])
        
        logger.info("========== MEDALLION PIPELINE HOÀN THÀNH ==========")
        
    except Exception as e:
        logger.error(f"Pipeline thất bại tại tầng nào đó: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_medallion_pipeline()
