# Purpose:　用於設定 API 請求和回應

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class LocationBase(BaseModel):
    name: str
    lat: float
    lon: float

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
    photo: str
    description: str
    location: int
    # villager: int
    account: int

    class Config:
        from_attributes = True  # 允許 SQLAlchemy ORM 自動轉換為 Pydantic 模型