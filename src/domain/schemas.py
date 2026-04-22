from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime

class CooperativeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cooperative_id: str
    cooperative_code: str
    cooperative_name: str
    is_active: bool = True

class RegionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    region_id: str
    region_code: str
    region_name: str
    cooperative_id: str
    is_active: bool = True

class BusinessModelSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    business_model_id: str
    business_model_code: str
    business_model_name: str
    is_active: bool = True

class StoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    store_id: str
    store_code: str
    store_name: str
    region_id: str
    business_model_id: str
    province: Optional[str] = None
    status: str = "active"
    opening_date: Optional[date] = None

class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    product_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    is_active: bool = True

class SalesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    month_id: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    store_id: str
    product_id: int
    classification: str
    quantity_sold: int = Field(..., ge=0)
    sales_amount: float = Field(..., ge=0)

class CustomerCountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    month_id: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    store_id: str
    customer_count: int = Field(..., ge=0)

class GoldSalesCubeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    month_id: str
    cooperative_id: str
    region_id: str
    business_model_id: str
    category: str
    store_id: str
    product_id: int
    classification: str
    total_qty: float
    total_amt: float
    customer_count: float
    avg_unit_price: float
    qty_pi: float
    amt_pi: float
    markdown_qty: float = 0.0
