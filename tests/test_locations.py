import pytest
from fastapi.testclient import TestClient #  FastAPI內建的HTTP客戶端，用於模擬API請求
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base, Location

# 創建測試用的臨時資料庫 - 使用SQLite內存數據庫
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建表格 - 這次不指定具體的表
# 只創建Location表，忽略其他表格
Base.metadata.create_all(bind=engine, tables=[Location.__table__])

# 建立測試客戶端
client = TestClient(app)

# 替換真實數據庫連接為測試數據庫
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 測試前設置和測試後清理
@pytest.fixture(scope="function")
def test_db():
    # 創建測試數據
    db = TestingSessionLocal()
    
    # 新增測試數據
    test_location1 = Location(
        name="測試地點1",
        Latitude="23.5",
        Longitude="121.5",
        Address="測試地址1",
        BriefDescription="測試描述1"
    )
    test_location2 = Location(
        name="測試地點2",
        Latitude="24.5",
        Longitude="122.5",
        Address="測試地址2",
        BriefDescription="測試描述2"
    )
    
    db.add(test_location1)
    db.add(test_location2)
    db.commit()
    
    yield db  # 將db傳給測試函數
    
    # 測試後清理資料
    db.query(Location).delete()
    db.commit()
    db.close()

# 測試 GET /api/locations 成功情況
def test_get_locations_success(test_db):
    # 先確保有測試數據
    locations = test_db.query(Location).all()
    assert len(locations) == 2
    
    # 發送API請求
    response = client.get("/api/locations")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 2
    
    # 檢查返回的數據內容
    assert data["data"][0]["name"] == "測試地點1"
    assert data["data"][0]["latitude"] == "23.5"
    assert data["data"][0]["longitude"] == "121.5"
    assert data["data"][0]["brief_description"] == "測試描述1"
    
    assert data["data"][1]["name"] == "測試地點2"

# 測試 GET /api/locations 沒有數據的情況
def test_get_locations_empty(test_db):
    # 清空所有數據
    test_db.query(Location).delete()
    test_db.commit()
    
    # 發送API請求
    response = client.get("/api/locations")
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "沒有找到任何地點資料"

# 測試指令：pytest -W ignore
