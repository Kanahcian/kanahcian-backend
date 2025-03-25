# 負責 Location 的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas

def get_villager_by_id(db: Session, villager_id: int):
    return db.query(models.Villager).filter(models.Villager.VillagerID == villager_id).first()

