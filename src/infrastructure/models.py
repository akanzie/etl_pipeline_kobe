from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Numeric, Index
from sqlalchemy.sql import func
from .database import Base

class Cooperative(Base):
    __tablename__ = "master_cooperatives"
    cooperative_id = Column(String(50), primary_key=True)
    cooperative_code = Column(String(50), nullable=False, unique=True)
    cooperative_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Region(Base):
    __tablename__ = "master_regions"
    region_id = Column(String(50), primary_key=True)
    region_code = Column(String(50), nullable=False, unique=True)
    region_name = Column(String(255), nullable=False)
    cooperative_id = Column(String(50), ForeignKey("master_cooperatives.cooperative_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class BusinessModel(Base):
    __tablename__ = "master_business_models"
    business_model_id = Column(String(50), primary_key=True)
    business_model_code = Column(String(50), nullable=False, unique=True)
    business_model_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Store(Base):
    __tablename__ = "master_stores"
    store_id = Column(String(50), primary_key=True)
    store_code = Column(String(50), nullable=False, unique=True)
    store_name = Column(String(255), nullable=False)
    region_id = Column(String(50), ForeignKey("master_regions.region_id"), nullable=False)
    business_model_id = Column(String(50), ForeignKey("master_business_models.business_model_id"), nullable=False)
    province = Column(String(100))
    status = Column(String(20), default="active")
    opening_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = "master_products"
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100))
    unit = Column(String(50))
    price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Calendar(Base):
    __tablename__ = "master_calendar"
    month_id = Column(String(7), primary_key=True)  # YYYY-MM
    year = Column(Integer, nullable=False)
    month_num = Column(Integer, nullable=False)
    quarter = Column(Integer)
    fiscal_year = Column(Integer)
    is_closed = Column(Boolean, default=False)

class DailySales(Base):
    __tablename__ = "fact_daily_sales"
    month_id = Column(String(7), ForeignKey("master_calendar.month_id"), primary_key=True)
    store_id = Column(String(50), ForeignKey("master_stores.store_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("master_products.product_id"), primary_key=True)
    classification = Column(String(50), primary_key=True)  # 定番 / 家庭応援 / 特売
    quantity_sold = Column(Integer)
    sales_amount = Column(Numeric(14, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class DailyCustomerCount(Base):
    __tablename__ = "fact_daily_customer_count"
    month_id = Column(String(7), ForeignKey("master_calendar.month_id"), primary_key=True)
    store_id = Column(String(50), ForeignKey("master_stores.store_id"), primary_key=True)
    customer_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class GoldSalesCube(Base):
    __tablename__ = "gold_sales_cube"
    month_id = Column(String(7), ForeignKey("master_calendar.month_id"), primary_key=True)
    cooperative_id = Column(String(50), ForeignKey("master_cooperatives.cooperative_id"), primary_key=True)
    region_id = Column(String(50), ForeignKey("master_regions.region_id"), primary_key=True)
    business_model_id = Column(String(50), ForeignKey("master_business_models.business_model_id"), primary_key=True)
    category = Column(String(100), primary_key=True, default="")
    store_id = Column(String(50), ForeignKey("master_stores.store_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("master_products.product_id"), primary_key=True)
    classification = Column(String(50), primary_key=True)
    
    total_qty = Column(Numeric(18, 2))
    total_amt = Column(Numeric(18, 2))
    customer_count = Column(Numeric(18, 2))
    avg_unit_price = Column(Numeric(18, 2))
    qty_pi = Column(Numeric(18, 2))
    amt_pi = Column(Numeric(18, 2))
    markdown_qty = Column(Numeric(18, 2), default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Indices
Index("idx_sales_store", DailySales.store_id)
Index("idx_sales_product", DailySales.product_id)
Index("idx_cube_main_query", GoldSalesCube.month_id, GoldSalesCube.cooperative_id, GoldSalesCube.region_id, GoldSalesCube.business_model_id, GoldSalesCube.category)
