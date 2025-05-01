# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine, event
# from sqlalchemy.orm import sessionmaker

# from app.main import app
# from app.database import get_db
# from app.models import Base, Location

# # 使用真正的內存數據庫，但使用特殊的連接字符串確保共享同一個連接
# SQLALCHEMY_DATABASE_URL = "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# # 創建測試會話
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 創建表格
# Base.metadata.create_all(bind=engine, tables=[Location.__table__])

# # 確保內存數據庫連接
# conn = engine.connect()

# # 建立測試客戶端
# client = TestClient(app)

# # 明確替換數據庫依賴
# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[get_db] = override_get_db

# # 測試前設置和測試後清理的 fixture
# @pytest.fixture(scope="function")
# def test_db():
#     """提供測試用的資料庫會話，並在測試後清理資料"""
#     db = TestingSessionLocal()
#     yield db
    
#     # 測試後清理資料
#     db.query(Location).delete()
#     db.commit()
#     db.close()

# # 設置測試資料的 fixture
# @pytest.fixture(scope="function")
# def test_locations(test_db):
#     """創建測試地點數據"""
#     # 確保沒有舊數據
#     test_db.query(Location).delete()
#     test_db.commit()
    
#     # 新增測試數據
#     test_location1 = Location(
#         name="測試地點1",
#         Latitude="23.5",
#         Longitude="121.5",
#         Address="測試地址1",
#         BriefDescription="測試描述1"
#     )
#     test_location2 = Location(
#         name="測試地點2",
#         Latitude="24.5",
#         Longitude="122.5",
#         Address="測試地址2",
#         BriefDescription="測試描述2"
#     )
    
#     test_db.add(test_location1)
#     test_db.add(test_location2)
#     test_db.commit()
    
#     # 請求另一個連接來確認數據存在
#     db2 = TestingSessionLocal()
#     db_locations = db2.query(Location).all()
#     print(f"測試數據庫中的地點數量 (另一個連接): {len(db_locations)}")
#     db2.close()
    
#     # 返回測試數據
#     return [test_location1, test_location2]

# # 測試 GET /api/locations 成功情況# 測試 GET /api/locations 成功情況 - 使用修補(monkey patching)
# def test_get_locations_success(test_locations, monkeypatch):
#     """測試成功獲取地點列表"""
#     # 修補Location.get_locations函數，直接返回我們添加的測試數據
#     from app.crud import Location as LocationCrud
    
#     def mock_get_locations(db):
#         return test_locations
    
#     monkeypatch.setattr(LocationCrud, "get_locations", mock_get_locations)
    
#     # 發送 API 請求
#     response = client.get("/api/locations")
    
#     assert response.status_code == 200
    
#     data = response.json()
#     assert data["status"] == "success"
#     assert len(data["data"]) == 2
    
#     # 檢查返回的數據內容
#     assert data["data"][0]["name"] == "測試地點1"
#     assert data["data"][0]["latitude"] == "23.5"
#     assert data["data"][0]["longitude"] == "121.5"
#     assert data["data"][0]["brief_description"] == "測試描述1"
    
#     assert data["data"][1]["name"] == "測試地點2"

# # 測試 GET /api/locations 沒有數據的情況
# def test_get_locations_empty(test_db):
#     """測試沒有地點數據時的響應"""
#     # 確保資料庫中沒有地點數據
#     test_db.query(Location).delete()
#     test_db.commit()
    
#     # 發送 API 請求
#     response = client.get("/api/locations")
#     assert response.status_code == 404
    
#     data = response.json()
#     assert data["detail"] == "沒有找到任何地點資料"

# # 清理全局資源
# def teardown_module():
#     """模組結束時清理資源"""
#     conn.close()



# # 測試指令：pytest -W ignore
