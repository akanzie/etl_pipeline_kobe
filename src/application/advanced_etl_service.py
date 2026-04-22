from sqlalchemy.orm import Session
from sqlalchemy import func
from ..infrastructure.models import (
    Product, ProductHistory, DailySales, 
    InventorySnapshot, GoldMarkdownPerformance
)
from ..core.logging import logger
from datetime import date, timedelta
import statistics

class AdvancedETLService:
    def __init__(self, db: Session):
        self.db = db

    def update_product_price_scd2(self, product_id: int, new_price: float):
        """
        Cập nhật giá sản phẩm theo mô hình SCD Type 2.
        """
        today = date.today()
        logger.info(f"Cập nhật giá SCD2 cho Product {product_id} -> {new_price}")
        
        # 1. Tìm bản ghi hiện tại
        current_record = self.db.query(ProductHistory).filter(
            ProductHistory.product_id == product_id,
            ProductHistory.is_current == True
        ).first()

        if current_record:
            if float(current_record.price) == float(new_price):
                logger.info("Giá không thay đổi, bỏ qua cập nhật SCD2.")
                return
            
            # Đóng bản ghi cũ
            current_record.end_date = today - timedelta(days=1)
            current_record.is_current = False

        # 2. Tạo bản ghi mới
        new_record = ProductHistory(
            product_id=product_id,
            price=new_price,
            effective_date=today,
            is_current=True
        )
        self.db.add(new_record)
        
        # Cập nhật giá ở bảng Master chính (optional, tùy thiết kế)
        product = self.db.get(Product, product_id)
        if product:

            product.price = new_price
            
        self.db.commit()
        logger.info("Hoàn thành cập nhật SCD2.")

    def detect_and_filter_anomalies(self, month_id: str):
        """
        Phát hiện bất thường sử dụng Z-Score (Simple version).
        """
        logger.info(f"Đang kiểm tra bất thường dữ liệu cho tháng {month_id}")
        
        sales_records = self.db.query(DailySales).filter(DailySales.month_id == month_id).all()
        if not sales_records:
            return []

        amounts = [float(s.sales_amount) for s in sales_records]
        if len(amounts) < 2:
            return sales_records

        mean_val = statistics.mean(amounts)
        std_dev = statistics.stdev(amounts)
        
        if std_dev == 0:
            return sales_records

        valid_records = []
        for s in sales_records:
            z_score = abs(float(s.sales_amount) - mean_val) / std_dev
            if z_score > 3:
                logger.warning(f"Phát hiện bất thường: Store {s.store_id}, Prod {s.product_id}, Amount {s.sales_amount} (Z-Score: {z_score:.2f})")
                continue
            valid_records.append(s)
            
        logger.info(f"Đã lọc {len(sales_records) - len(valid_records)} bản ghi bất thường.")
        return valid_records

    def build_markdown_analysis(self, month_id: str):
        """
        Tổng hợp hiệu quả giảm giá (Markdown Performance).
        Kết hợp Sales + Inventory + Classification.
        """
        logger.info(f"Đang xây dựng Markdown Analysis cho tháng {month_id}")
        
        # Xóa dữ liệu cũ
        self.db.query(GoldMarkdownPerformance).filter(GoldMarkdownPerformance.month_id == month_id).delete()

        # Logic: STR = Total Qty Sold / Opening Stock
        # Ta join DailySales với InventorySnapshot
        from ..infrastructure.models import Store, Product
        
        query = self.db.query(
            DailySales.month_id,
            Product.category,
            DailySales.classification,
            func.sum(DailySales.sales_amount).label('total_sales'),
            func.sum(DailySales.quantity_sold).label('total_qty'),
            func.sum(InventorySnapshot.opening_stock).label('total_stock')
        ).join(
            Product, Product.product_id == DailySales.product_id
        ).join(
            InventorySnapshot, 
            (InventorySnapshot.month_id == DailySales.month_id) & 
            (InventorySnapshot.store_id == DailySales.store_id) & 
            (InventorySnapshot.product_id == DailySales.product_id)
        ).filter(
            DailySales.month_id == month_id
        ).group_by(
            DailySales.month_id,
            Product.category,
            DailySales.classification
        )

        results = query.all()
        
        perf_entries = []
        for row in results:
            str_rate = float(row.total_qty) / float(row.total_stock) if row.total_stock and row.total_stock > 0 else 0
            
            # Giả định Impact dựa trên so sánh doanh thu các loại (Logic đơn giản hóa)
            impact = 1.2 if row.classification == '特売' else 1.0
            
            entry = GoldMarkdownPerformance(
                month_id=row.month_id,
                category=row.category,
                classification=row.classification,
                total_sales=row.total_sales,
                avg_sell_through=str_rate,
                markdown_impact=impact
            )
            perf_entries.append(entry)

        if perf_entries:
            self.db.bulk_save_objects(perf_entries)
            self.db.commit()
            logger.info(f"Đã nạp {len(perf_entries)} bản ghi vào Gold Markdown Performance.")
