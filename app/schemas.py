# app/schemas.py - 完整修復版本
# Purpose:　用於設定 API 請求和回應

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date

# ===== Location 相關 Schemas =====
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
    latitude: str  # 對應 ORM 的 `Latitude`
    longitude: str  # 對應 ORM 的 `Longitude`
    address: Optional[str] = None  # `Address` 可能是 NULL
    brief_description: Optional[str] = None  # `BriefDescription` 可能是 NULL
    photo: Optional[str] = None
    tag: Optional[List[str]] = None

    class Config:
        from_attributes = True  # 允許 SQLAlchemy ORM 自動轉換為 Pydantic 模型

# ===== Record 相關 Schemas - 新增 =====

class RecordBase(BaseModel):
    """Record 基礎模型"""
    semester: str
    date: date
    photo: Optional[str] = None
    description: Optional[str] = None
    location_id: int
    account_id: int

class RecordCreate(RecordBase):
    """創建 Record 請求模型"""
    pass

class RecordUpdate(BaseModel):
    """更新 Record 請求模型 - 所有欄位都是可選的"""
    semester: Optional[str] = None
    date: Optional[date] = None
    photo: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[int] = None
    account_id: Optional[int] = None

class RecordResponse(BaseModel):
    """Record 回應模型"""
    record_id: int
    semester: str
    date: date
    photo: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[int] = None  # 允許 NULL
    account_id: Optional[int] = None   # 允許 NULL
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm_record(cls, record):
        """從 ORM Record 物件創建回應模型"""
        return cls(
            record_id=record.RecordID,
            semester=record.Semester or "",  # 防止 NULL
            date=record.Date,
            photo=record.Photo,
            description=record.Description,
            location_id=record.Location,  # 可能是 NULL
            account_id=record.Account     # 可能是 NULL
        )

# ===== 請求參數模型 - 新增 =====

class LocationID(BaseModel):
    """原有的 LocationID 模型（保持兼容性）"""
    locationid: int

class LocationIdParam(BaseModel):
    """新的地點 ID 參數模型"""
    location_id: int

class AccountIdParam(BaseModel):
    """帳號 ID 參數模型"""
    account_id: int

class SemesterParam(BaseModel):
    """學期參數模型"""
    semester: str

# ===== 統計相關模型 - 新增 =====

class RecordStats(BaseModel):
    """Record 統計模型"""
    total_records: int
    records_by_location: Optional[dict] = None
    records_by_semester: Optional[dict] = None

# ===== Villager 相關 Schemas =====

class VillagerID(BaseModel):
    villagerid: int

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

# 新增村民親屬關係請求
class RelationshipCreate(BaseModel):
    source_villager_id: int
    target_villager_id: int
    relationship_type_id: int