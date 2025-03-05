# 負責 locations 的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas

# **取得所有地點**
def get_locations(db: Session):
    return db.query(models.Location).all()

# **新增地點**
def add_location(db: Session, location: schemas.LocationCreate):
    new_location = models.Location(**location.dict())
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location
