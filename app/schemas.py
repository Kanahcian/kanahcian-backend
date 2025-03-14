# Purpose:　用於設定 API 請求和回應

from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class LocationBase(BaseModel):
    name: str
    latitude: str  # 從 lat 改為 latitude 以符合 ORM 模型
    longitude: str  # 從 lon 改為 longitude 以符合 ORM 模型
    address: Optional[str] = None
    brief_description: Optional[str] = None

class LocationCreate(LocationBase):
    pass

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
    account: str
    students: List[str] = []
    villagers: List[str] = []

    class Config:
        from_attributes = True  # 允許 SQLAlchemy ORM 自動轉換為 Pydantic 模型