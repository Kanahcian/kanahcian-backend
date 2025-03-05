# Purpose: 處理 Record 相關 API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud import Location
from ..database import get_db
from .. import schemas

from typing import List
router = APIRouter()

# **取得家訪紀錄**
# @router.post("/records", response_model=List[schemas.RecordResponse], status_code=status.HTTP_200_OK)
# def get_record(record: schemas.RecordQuery, db: Session = Depends(get_db)):
    # 查詢是否有該 BuildingID 的記錄（可能有多筆）
    # records = db.query(models.Record).filter(models.Record.building_id == record.building_id).all()
    
    # if not records:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="沒有找到對應的記錄"
    #     )

    # Dummy data
    # records = [
    #     {
    #         "id": 1,
    #         "semester": "1101",
    #         "date": "2021-09-01",
    #         "description": "家訪記錄"
    #     },
    #     {
    #         "id": 2,
    #         "semester": "1101",
    #         "date": "2021-09-02",
    #         "description": "家訪記錄"
    #     }
    # ]

    # # 回傳查詢到的所有記錄，格式為 List of Dictionaries
    # return [
    #     {
    #         "record_id": rec["id"],
    #         "semester": rec["semester"],
    #         "date": rec["date"],
    #         "description": rec["description"]
    #     }
    #     for rec in records
    # ]

