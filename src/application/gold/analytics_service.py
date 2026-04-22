from sqlalchemy.orm import Session
from sqlalchemy import func
from ...infrastructure.models import (
    DailySales, Store, Region, Product, 
    DailyCustomerCount, GoldSalesCube, 
    InventorySnapshot, GoldMarkdownPerformance
)
from ...core.logging import logger

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def build_sales_cube(self, mode: str = "INCREMENTAL", month_ids: list = None):
        """
        Gold Layer: Xây dựng Sales Cube đa chiều.
        Tương ứng với gold_sales_cube trên Databricks.
        """
        logger.info(f"--- [GOLD] Đang xây dựng Sales Cube (Mode: {mode}) ---")
        try:
            if mode == "FULL_REBUILD":
                self.db.query(GoldSalesCube).delete()
            elif mode == "INCREMENTAL" and month_ids:
                self.db.query(GoldSalesCube).filter(GoldSalesCube.month_id.in_(month_ids)).delete()

            # Logic Aggregation (đã được tối ưu từ CubeService)
            query = self.db.query(
                DailySales.month_id,
                Region.cooperative_id,
                Store.region_id,
                Store.business_model_id,
                func.coalesce(Product.category, '').label('category'),
                DailySales.store_id,
                DailySales.product_id,
                DailySales.classification,
                func.sum(DailySales.quantity_sold).label('total_qty'),
                func.sum(DailySales.sales_amount).label('total_amt'),
                func.coalesce(func.max(DailyCustomerCount.customer_count), 0).label('customer_count')
            ).join(Store, Store.store_id == DailySales.store_id
            ).join(Region, Region.region_id == Store.region_id
            ).join(Product, Product.product_id == DailySales.product_id
            ).outerjoin(DailyCustomerCount, 
                (DailyCustomerCount.month_id == DailySales.month_id) & 
                (DailyCustomerCount.store_id == DailySales.store_id)
            )

            if mode == "INCREMENTAL" and month_ids:
                query = query.filter(DailySales.month_id.in_(month_ids))

            query = query.group_by(
                DailySales.month_id, Region.cooperative_id, Store.region_id,
                Store.business_model_id, Product.category, DailySales.store_id,
                DailySales.product_id, DailySales.classification
            )

            results = query.all()
            cube_entries = []
            for row in results:
                total_qty = float(row.total_qty or 0)
                total_amt = float(row.total_amt or 0)
                cust_count = float(row.customer_count or 0)
                
                entry = GoldSalesCube(
                    month_id=row.month_id,
                    cooperative_id=row.cooperative_id,
                    region_id=row.region_id,
                    business_model_id=row.business_model_id,
                    category=row.category,
                    store_id=row.store_id,
                    product_id=row.product_id,
                    classification=row.classification,
                    total_qty=total_qty,
                    total_amt=total_amt,
                    customer_count=cust_count,
                    avg_unit_price=total_amt / total_qty if total_qty > 0 else 0,
                    qty_pi=total_qty / cust_count if cust_count > 0 else 0,
                    amt_pi=total_amt / cust_count if cust_count > 0 else 0
                )
                cube_entries.append(entry)

            if cube_entries:
                self.db.bulk_save_objects(cube_entries)
                self.db.commit()
                logger.info(f"[GOLD] Đã nạp {len(cube_entries)} bản ghi vào Gold Sales Cube.")
        except Exception as e:
            self.db.rollback()
            logger.error(f"[GOLD] Lỗi khi xây dựng Sales Cube: {str(e)}")
            raise e

    def build_markdown_analysis(self, month_id: str):
        """
        Gold Layer: Phân tích hiệu quả Markdown.
        """
        logger.info(f"--- [GOLD] Đang phân tích Markdown cho tháng {month_id} ---")
        # Logic tương tự như AdvancedETLService...
        pass
