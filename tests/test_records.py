import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date
from sqlalchemy import text

from app.main import app
from app.database import get_db, Base
from app.models import Location, Record, Account, Villager

# 創建測試用的臨時資料庫 - 使用SQLite內存數據庫
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 為了解決schema問題，我們手動定義測試用的關聯表
# 這些表沒有schema設定
students_at_record = Table(
    "Students_at_record", 
    Base.metadata,
    Column("Account", Integer, ForeignKey("Account.AccountID"), primary_key=True),
    Column("Record", Integer, ForeignKey("Record.RecordID"), primary_key=True),
)

villagers_at_record = Table(
    "Villagers_at_record", 
    Base.metadata,
    Column("Villager", Integer, ForeignKey("Villager.VillagerID"), primary_key=True),
    Column("Record", Integer, ForeignKey("Record.RecordID"), primary_key=True),
)

# 創建測試所需的所有表格
# 先創建基本表格
Base.metadata.create_all(bind=engine, tables=[
    Location.__table__,
    Record.__table__,
    Account.__table__,
    Villager.__table__
])

# 再創建關聯表
students_at_record.create(bind=engine)
villagers_at_record.create(bind=engine)

# 建立測試客戶端
client = TestClient(app)

# 1. FastAPI 依賴覆蓋 - 替換資料庫連接
def override_get_db():
    """替換 FastAPI 的資料庫依賴，使用測試資料庫"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 告訴 FastAPI 在測試中使用我們的測試資料庫
app.dependency_overrides[get_db] = override_get_db

# 2. Pytest Fixture - 管理測試資料
# 在 test_db fixture 中修改清理代碼
@pytest.fixture(scope="function")
def test_db():
    """提供測試用的資料庫會話"""
    db = TestingSessionLocal()
    yield db
    
    # 測試後清理所有資料
    # 使用 text() 明確標記 SQL 語句
    db.execute(text("DELETE FROM Villagers_at_record"))
    db.execute(text("DELETE FROM Students_at_record"))
    db.query(Record).delete()
    db.query(Villager).delete()
    db.query(Account).delete()
    db.query(Location).delete()
    db.commit()
    db.close()

# 在 test_data fixture 中修改插入關聯資料的代碼
@pytest.fixture(scope="function")
def test_data(test_db):
    # ... 前面的代碼保持不變 ...
    
    # 建立學生與記錄的關聯 (使用 text() 標記 SQL)
    test_db.execute(text(
        f"INSERT INTO Students_at_record (Account, Record) VALUES ({account1.AccountID}, {record1.RecordID})"
    ))
    test_db.execute(text(
        f"INSERT INTO Students_at_record (Account, Record) VALUES ({account2.AccountID}, {record1.RecordID})"
    ))
    
    # 建立村民與記錄的關聯 (使用 text() 標記 SQL)
    test_db.execute(text(
        f"INSERT INTO Villagers_at_record (Villager, Record) VALUES ({villager1.VillagerID}, {record1.RecordID})"
    ))
    test_db.execute(text(
        f"INSERT INTO Villagers_at_record (Villager, Record) VALUES ({villager2.VillagerID}, {record1.RecordID})"
    ))
    
    test_db.commit()
    
    # 返回測試數據資訊
    return {
        "location": location,
        "accounts": [account1, account2],
        "villagers": [villager1, villager2],
        "records": [record1, record2]
    }

# 測試 POST /api/records 找不到記錄情況
def test_get_records_by_location_not_found(test_db):
    """測試找不到家訪紀錄的情況"""
    # 建立一個不存在家訪紀錄的地點
    new_location = Location(
        name="無記錄地點",
        Latitude="25.0",
        Longitude="121.0",
        Address="測試地址",
        BriefDescription="沒有任何家訪記錄的地點"
    )
    test_db.add(new_location)
    test_db.commit()
    test_db.refresh(new_location)
    
    # 構建請求數據
    request_data = {"locationid": new_location.LocationID}
    
    # 發送POST請求
    response = client.post(f"/api/records?locationid={new_location.LocationID}")
    
    # 檢查狀態碼
    assert response.status_code == 404
    
    # 解析回應內容
    data = response.json()
    assert data["detail"] == "沒有找到任何家訪記錄"

# 測試 POST /api/records 無效ID情況
def test_get_records_by_location_invalid_id():
    """測試使用無效的地點ID"""
    # 使用一個不存在的ID (9999)
    invalid_id = 9999
    
    # 發送POST請求，帶查詢參數
    response = client.post(f"/api/records?locationid={invalid_id}")
    
    # 檢查狀態碼
    assert response.status_code == 404
    
    # 解析回應內容
    data = response.json()
    assert "沒有找到任何家訪記錄" in data["detail"]
