import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database import Base
from src.infrastructure.models import *
from src.application.advanced_etl_service import AdvancedETLService
from datetime import date

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_scd_type_2_logic(db):
    # 1. Setup
    prod = Product(product_id=1, product_name="Test Prod", price=1000)
    db.add(prod)
    db.commit()
    
    service = AdvancedETLService(db)
    
    # 2. Update price first time
    service.update_product_price_scd2(1, 1200)
    
    # Check
    hist = db.query(ProductHistory).filter(ProductHistory.product_id == 1).all()
    assert len(hist) == 1
    assert float(hist[0].price) == 1200
    assert hist[0].is_current == True
    
    # 3. Update price second time
    service.update_product_price_scd2(1, 1500)
    
    # Check
    hist = db.query(ProductHistory).filter(ProductHistory.product_id == 1).order_by(ProductHistory.hist_id).all()
    assert len(hist) == 2
    assert hist[0].is_current == False
    assert float(hist[0].price) == 1200
    assert hist[0].end_date is not None
    
    assert hist[1].is_current == True
    assert float(hist[1].price) == 1500
    assert hist[1].effective_date == date.today()

def test_anomaly_detection(db):
    service = AdvancedETLService(db)
    # Mock data with one extreme outlier
    for i in range(10):
        s = DailySales(month_id="2024-01", store_id=f"S{i}", product_id=1, classification="定番", quantity_sold=10, sales_amount=100)
        db.add(s)
    
    outlier = DailySales(month_id="2024-01", store_id="SOUT", product_id=1, classification="定番", quantity_sold=10, sales_amount=10000)
    db.add(outlier)
    db.commit()
    
    valid_records = service.detect_and_filter_anomalies("2024-01")
    assert len(valid_records) == 10  # Outlier should be filtered out
