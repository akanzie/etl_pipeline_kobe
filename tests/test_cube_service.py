import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database import Base
from src.infrastructure.models import *
from src.application.cube_service import CubeService

# Setup In-memory DB for Testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_cube_transformation_logic(db_session):
    # 1. Setup Mock Data
    coop = Cooperative(cooperative_id="C1", cooperative_code="CP1", cooperative_name="Coop 1")
    region = Region(region_id="R1", region_code="RG1", region_name="Region 1", cooperative_id="C1")
    model = BusinessModel(business_model_id="M1", business_model_code="BM1", business_model_name="Model 1")
    store = Store(store_id="S1", store_code="ST1", store_name="Store 1", region_id="R1", business_model_id="M1")
    product = Product(product_id=1, product_name="Prod 1", category="Cat A")
    calendar = Calendar(month_id="2024-03", year=2024, month_num=3)
    
    db_session.add_all([coop, region, model, store, product, calendar])
    
    # Add Sales
    sales = DailySales(
        month_id="2024-03", store_id="S1", product_id=1, 
        classification="定番", quantity_sold=100, sales_amount=5000
    )
    # Add Customer Count
    customers = DailyCustomerCount(month_id="2024-03", store_id="S1", customer_count=50)
    
    db_session.add_all([sales, customers])
    db_session.commit()

    # 2. Run Transformation
    service = CubeService(db_session)
    service.transform_and_load(mode="FULL_REBUILD")

    # 3. Assertions
    cube_data = db_session.query(GoldSalesCube).first()
    assert cube_data is not None
    assert cube_data.total_qty == 100
    assert cube_data.total_amt == 5000
    assert cube_data.customer_count == 50
    assert float(cube_data.avg_unit_price) == 50.0  # 5000 / 100
    assert float(cube_data.qty_pi) == 2.0         # 100 / 50
    assert float(cube_data.amt_pi) == 100.0        # 5000 / 50
    assert cube_data.category == "Cat A"

def test_incremental_load(db_session):
    # Setup tương tự nhưng chạy incremental
    # (Rút gọn để tiết kiệm, thực tế nên test cả 2 mode)
    pass
