# Purpose:　用於設定 API 請求和回應

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date

class LocationBase(BaseModel):
    name: str
    latitude: str  # 從 lat 改為 latitude 以符合 ORM 模型
    longitude: str  # 從 lon 改為 longitude 以符合 ORM 模型
    address: Optional[str] = None
    brief_description: Optional[str] = None
    photo: Optional[str] = None
    tag: Optional[List[str]] = None


# Input for POST/location
class LocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    brief_description: Optional[str] = None
    photo: Optional[str] = None
    tag: Optional[List[str]] = None

# Input for PUT/location
class LocationUpdate(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    brief_description: Optional[str] = None
    photo: Optional[str] = None
    tag: Optional[List[str]] = None

# Output of GET/location
class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    brief_description: Optional[str] = None
    photo: Optional[str] = None
    tag: Optional[List[str]] = None

# Output of GET/locations
class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: str  # 對應 ORM 的 `Latitude`
    longitude: str  # 對應 ORM 的 `Longitude`
    # address: Optional[str]=None  # `Address` 可能是 NULL，所以加 `None`
    brief_description: Optional[str]=None  # `BriefDescription` 可能是 NULL，所以加 `None`
    photo: Optional[str] = None
    tag: Optional[List[str]] = None

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
    students: List[str] = Field(default_factory=list)
    villagers: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

# Input of GET/villager
class VillagerID(BaseModel):
    villagerid: int

# Output of GET/villager
class VillagerResponse(BaseModel):
    villagerid: int
    name: str
    gender: str
    job: Optional[str]
    url: Optional[str]
    photo: Optional[str]
    locationid: int

# 村民關係模型
class RelationshipBase(BaseModel):
    relationship_id: int
    relative_id: int
    relative_name: str
    relationship_type: str
    role: str

    model_config = ConfigDict(from_attributes=True)

# 村民詳細回應（包含親屬關係）
class VillagerDetailResponse(BaseModel):
    villagerid: int
    name: str
    gender: str
    job: Optional[str] = None
    url: Optional[str] = None
    photo: Optional[str] = None
    locationid: int
    relationships: List[dict] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

# 新增村民請求
class VillagerCreate(BaseModel):
    name: str
    gender: str  # 'M' 或 'F'
    job: Optional[str] = None
    url: Optional[str] = None
    photo: Optional[str] = None
    location_id: int

# 更新村民請求
class VillagerUpdate(BaseModel):
    name: str
    gender: str  # 'M' 或 'F'
    job: Optional[str] = None
    url: Optional[str] = None
    photo: Optional[str] = None
    location_id: int

# 新增家訪記錄請求
class RecordCreate(BaseModel):
    semester: str
    date: date
    photo: Optional[str] = None
    description: Optional[str] = None
    location_id: int
    account_id: int
    student_ids: List[int] = Field(default_factory=list)
    villager_ids: List[int] = Field(default_factory=list)

# 更新家訪記錄請求
class RecordUpdate(BaseModel):
    semester: Optional[str] = None
    date: Optional[date] = None
    photo: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[int] = None
    account_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    villager_ids: Optional[List[int]] = None

# 刪除家訪記錄請求
class RecordDelete(BaseModel):
    record_id: int

# 新增村民親屬關係請求
class RelationshipCreate(BaseModel):
    source_villager_id: int
    target_villager_id: int
    relationship_type_id: int
