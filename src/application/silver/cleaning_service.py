from sqlalchemy.orm import Session
from ...infrastructure.models import DailySales
from ...core.logging import logger
import statistics

class CleaningService:
    def __init__(self, db: Session):
        self.db = db

    def clean_and_validate_sales(self, month_id: str):
        """
        Silver Layer: Làm sạch dữ liệu, lọc bỏ các bản ghi bất thường (Anomalies).
        Tương ứng với fact_daily_sales trên Databricks.
        """
        logger.info(f"--- [SILVER] Đang làm sạch dữ liệu tháng {month_id} ---")
        
        sales_records = self.db.query(DailySales).filter(DailySales.month_id == month_id).all()
        if not sales_records:
            logger.warning(f"[SILVER] Không tìm thấy dữ liệu cho tháng {month_id}")
            return []

        amounts = [float(s.sales_amount) for s in sales_records]
        if len(amounts) < 2:
            return sales_records

        mean_val = statistics.mean(amounts)
        std_dev = statistics.stdev(amounts)
        
        if std_dev == 0:
            return sales_records

        valid_records = []
        outliers_count = 0
        for s in sales_records:
            z_score = abs(float(s.sales_amount) - mean_val) / std_dev
            if z_score > 3:
                outliers_count += 1
                continue
            valid_records.append(s)
            
        logger.info(f"[SILVER] Hoàn thành. Đã loại bỏ {outliers_count} bản ghi bất thường.")
        return valid_records
