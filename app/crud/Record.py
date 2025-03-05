# 負責 Record 的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas

# **取得所有家訪紀錄**
def get_records(db: Session):
    return db.query(models.Record).all()

# **根據位置取得特定家訪紀錄**
def get_record_by_location(db: Session, ID: int):
    return db.query(models.Record).filter(models.Record.Location == ID).order_by(models.Record.Date.desc()).all()

