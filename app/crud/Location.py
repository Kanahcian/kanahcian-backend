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
        "BriefDescription": location.brief_description,
        "Photo": location.photo,
        "Tag": location.tag
    }
    new_location = models.Location(**location_data)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

def update_location(db: Session, location_id: int, location: schemas.LocationUpdate):
    loc = db.query(models.Location).filter(models.Location.LocationID == location_id).first()
    if not loc:
        return None
    loc.name = location.name
    loc.Latitude = location.latitude
    loc.Longitude = location.longitude
    loc.Address = location.address
    loc.BriefDescription = location.brief_description
    loc.Photo = location.photo
    loc.Tag = location.tag
    db.commit()
    db.refresh(loc)
    return loc

def delete_location(db: Session, location_id: int):
    loc = db.query(models.Location).filter(models.Location.LocationID == location_id).first()
    if not loc:
        return False
    db.delete(loc)
    db.commit()
    return True
