from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..infrastructure.models import (
    DailySales, Store, Region, Product, 
    DailyCustomerCount, GoldSalesCube
)
from datetime import datetime

from ..core.logging import logger

class CubeService:
    def __init__(self, db: Session):
        self.db = db

    def transform_and_load(self, mode: str = "INCREMENTAL", month_ids: list = None):
        """
        Thực hiện biến đổi dữ liệu từ Fact/Master sang Gold Cube.
        """
        try:
            logger.info(f"Bắt đầu chạy Cube Transformation (Mode: {mode})")

            if mode == "FULL_REBUILD":
                logger.info("Đang thực hiện FULL_REBUILD: Xóa toàn bộ Gold Cube.")
                self.db.query(GoldSalesCube).delete()
            elif mode == "INCREMENTAL" and month_ids:
                logger.info(f"Đang thực hiện INCREMENTAL cho các tháng: {month_ids}")
                self.db.query(GoldSalesCube).filter(GoldSalesCube.month_id.in_(month_ids)).delete()


            # Query kết hợp (Aggregation logic)
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
            ).join(
                Store, Store.store_id == DailySales.store_id
            ).join(
                Region, Region.region_id == Store.region_id
            ).join(
                Product, Product.product_id == DailySales.product_id
            ).outerjoin(
                DailyCustomerCount, 
                (DailyCustomerCount.month_id == DailySales.month_id) & 
                (DailyCustomerCount.store_id == DailySales.store_id)
            )

            if mode == "INCREMENTAL" and month_ids:
                query = query.filter(DailySales.month_id.in_(month_ids))

            query = query.group_by(
                DailySales.month_id,
                Region.cooperative_id,
                Store.region_id,
                Store.business_model_id,
                Product.category,
                DailySales.store_id,
                DailySales.product_id,
                DailySales.classification
            )

            results = query.all()
            
            cube_entries = []
            for row in results:
                total_qty = float(row.total_qty or 0)
                total_amt = float(row.total_amt or 0)
                cust_count = float(row.customer_count or 0)
                
                avg_unit_price = total_amt / total_qty if total_qty > 0 else 0
                qty_pi = total_qty / cust_count if cust_count > 0 else 0
                amt_pi = total_amt / cust_count if cust_count > 0 else 0
                
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
                    avg_unit_price=avg_unit_price,
                    qty_pi=qty_pi,
                    amt_pi=amt_pi,
                    markdown_qty=0
                )
                cube_entries.append(entry)

            if cube_entries:
                self.db.bulk_save_objects(cube_entries)
                self.db.commit()
                logger.info(f"Đã nạp {len(cube_entries)} bản ghi vào Gold Sales Cube.")
            else:
                logger.warning("Không có dữ liệu mới để nạp.")

            logger.info("Hoàn thành Cube Transformation thành công.")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Lỗi nghiêm trọng trong quá trình nạp Cube: {str(e)}")
            raise e


