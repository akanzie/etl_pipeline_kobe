from sqlalchemy.orm import Session
from sqlalchemy import text
from ...core.logging import logger

class IngestionService:
    def __init__(self, db: Session):
        self.db = db

    def load_raw_data(self, sql_commands: list):
        """
        Bronze Layer: Nạp dữ liệu thô từ các câu lệnh SQL hoặc file vào Database.
        Tương ứng với các bảng bronze_* trên Databricks.
        """
        logger.info("--- [BRONZE] Bắt đầu quá trình Ingestion ---")
        try:
            for cmd in sql_commands:
                self.db.execute(text(cmd))
            self.db.commit()
            logger.info("[BRONZE] Nạp dữ liệu thô thành công.")
        except Exception as e:
            self.db.rollback()
            logger.error(f"[BRONZE] Lỗi Ingestion: {str(e)}")
            raise e
