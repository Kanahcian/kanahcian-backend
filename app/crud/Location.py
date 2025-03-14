# 負責 Location 的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas

# **取得所有地點**
def get_locations(db: Session):
    return db.query(models.Location).all()

# **新增地點**
def add_location(db: Session, location: schemas.LocationCreate):
    # 將 schema 轉換為與 ORM 模型相符的格式
    location_data = {
        "name": location.name,
        "Latitude": location.latitude,
        "Longitude": location.longitude,
        "Address": location.address,
        "BriefDescription": location.brief_description
    }
    new_location = models.Location(**location_data)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location
