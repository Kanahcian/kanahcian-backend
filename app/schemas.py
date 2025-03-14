# Purpose:　用於設定 API 請求和回應

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date

# Output of GET/locations
class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: str  # 對應 ORM 的 `Latitude`
    longitude: str  # 對應 ORM 的 `Longitude`
    # address: Optional[str]=None  # `Address` 可能是 NULL，所以加 `None`
    brief_description: Optional[str]=None  # `BriefDescription` 可能是 NULL，所以加 `None`

    class Config:
        from_attributes = True  # 允許 SQLAlchemy ORM 自動轉換為 Pydantic 模型

# Input of POST/records
class LocationID(BaseModel):
    locationid: int

# Output of POST/records
class RecordResponse(BaseModel):
    recordid: int
    semester: str
    date: date
    photo: Optional[str] = None
    description: Optional[str] = None
    location: int
    account: str  # 現在表示帳號名稱而非 ID
    students: List[str] = []  # 參與的大學生名單
    villagers: List[str] = []  # 相關的村民名單

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 語法