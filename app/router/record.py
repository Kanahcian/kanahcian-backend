# Purpose: 處理 Record 相關 API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud import Record
from ..database import get_db
from .. import schemas

router = APIRouter()

# **取得所有地點**
@router.get("/records", response_model=dict)
def get_all_records(db: Session = Depends(get_db)):
    record_list = Record.get_records(db)

    if not record_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="沒有找到任何地點資料"
        )

    # 這裡的資料格式名是對應　models.py　的 Location
    return {
    "status": "success",
    "data": [
        schemas.RecordResponse(
            recordid=rec.RecordID,  # 保留大寫
            semester=rec.Semester,  # 小寫
            date=rec.Date,  # ORM 是大寫，但 Schema 需要小寫
            photo=rec.Photo,
            description=rec.Description,
            location=rec.Location,
            # villager=rec.Villager,
            account=rec.Account,
        )
        for rec in record_list
    ]
}

# **取得特定地點的家訪紀錄**
@router.post("/records", response_model=dict)
def get_record_by_location(db: Session = Depends(get_db), location: schemas.LocationID = Depends()):
    record_list = Record.get_record_by_location(db, location.locationid)

    if not record_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="沒有找到任何地點資料"
        )

    # 這裡的資料格式名是對應　models.py　的 Record
    return {
    "status": "success",
    "data": [
        schemas.RecordResponse(
            recordid=rec.RecordID,  # 保留大寫
            semester=rec.Semester,  # 小寫
            date=rec.Date,  # ORM 是大寫，但 Schema 需要小寫
            photo=rec.Photo,
            description=rec.Description,
            location=rec.Location,
            # villager=rec.Villager,
            account=rec.Account,
        )
        for rec in record_list
    ]
}