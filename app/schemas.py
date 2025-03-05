# Purpose:　用於設定 API 請求和回應

from pydantic import BaseModel, ConfigDict
from typing import Optional

class LocationBase(BaseModel):
    name: str
    lat: float
    lon: float

class LocationCreate(LocationBase):
    pass

# GET/locations
class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: str  # 對應 ORM 的 `Latitude`
    longitude: str  # 對應 ORM 的 `Longitude`
    # address: Optional[str]=None  # `Address` 可能是 NULL，所以加 `None`

    class Config:
        from_attributes = True  # 允許 SQLAlchemy ORM 自動轉換為 Pydantic 模型

