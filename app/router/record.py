# Purpose: 處理 Record 相關 API

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import logging

from ..crud import Record
from ..database import get_db, engine
from .. import schemas, models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Record"])

# **取得所有地點**
# @router.get("/records", response_model=dict)
# def get_all_records(db: Session = Depends(get_db)):
#     record_list = Record.get_records(db)

#     if not record_list:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="沒有找到任何地點資料"
#         )

#     # 這裡的資料格式名是對應　models.py　的 Location
#     return {
#     "status": "success",
#     "data": [
#         schemas.RecordResponse(
#             recordid=rec.RecordID,  # 保留大寫
#             semester=rec.Semester,  # 小寫
#             date=rec.Date,  # ORM 是大寫，但 Schema 需要小寫
#             photo=rec.Photo,
#             description=rec.Description,
#             location=rec.Location,
#             # villager=rec.Villager,
#             account=rec.Account,
#         )
#         for rec in record_list
#     ]
# }

# **取得特定地點的家訪紀錄**
# @router.post("/records", response_model=dict)
# def get_record_by_location(db: Session = Depends(get_db), location: schemas.LocationID = Depends()):
#     record_list = Record.get_record_by_location(db, location.locationid)

#     if not record_list:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="沒有找到任何地點資料"
#         )

#     # 這裡的資料格式名是對應　models.py　的 Record
#     return {
#     "status": "success",
#     "data": [
#         schemas.RecordResponse(
#             recordid=rec.RecordID,  # 保留大寫
#             semester=rec.Semester,  # 小寫
#             date=rec.Date,  # ORM 是大寫，但 Schema 需要小寫

# **取得特定地點的家訪紀錄（包含大學生和村民名單）**
@router.post("/records", response_model=dict)
def get_record_by_location(db: Session = Depends(get_db), location: schemas.LocationID = Depends()):
    """
    根據地點 ID 獲取所有相關的家訪記錄，包含參與的大學生和村民名單
    
    Args:
        db (Session): 資料庫連線
        location (schemas.LocationID): 包含地點 ID 的請求物件
    
    Returns:
        dict: 包含狀態和完整家訪資料的回應
    """
    try:
        # 使用詳細查詢函數
        record_list = Record.get_record_by_location_with_details(db, location.locationid)
        
        # logger.info(f"查詢到 {len(record_list)} 條記錄")
        
        if not record_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="沒有找到任何家訪記錄"
            )

        return {
            "status": "success",
            "data": record_list
        }
        
    except HTTPException:
        # 重新拋出已捕獲的 HTTPException
        raise
    except Exception as e:
        logger.exception(f"處理請求時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"伺服器內部錯誤: {str(e)}"
        )

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_record(
    record_data: schemas.RecordCreate,
    db: Session = Depends(get_db)
):
    """
    創建新的家訪記錄
    
    Args:
        record_data (schemas.RecordCreate): 家訪記錄數據
        db (Session): 資料庫連線
        
    Returns:
        dict: 包含狀態和創建的家訪記錄
    """
    try:
        # 創建家訪記錄
        db_record = Record.create_record(db, record_data)
        
        # 獲取完整的記錄信息
        record_info = db.query(
            models.Record,
            models.Account.Name.label('AccountName')
        ).join(
            models.Account, models.Record.Account == models.Account.AccountID
        ).filter(
            models.Record.RecordID == db_record.RecordID
        ).first()
        
        if not record_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="創建記錄時發生錯誤"
            )
            
        record, account_name = record_info
        
        # 獲取學生和村民名單
        students = Record.get_students_by_record(db, record.RecordID)
        villagers = Record.get_villagers_by_record(db, record.RecordID)
        
        return {
            'status': 'success',
            'data': {
                'recordid': record.RecordID,
                'semester': record.Semester,
                'date': record.Date,
                'photo': record.Photo,
                'description': record.Description,
                'location': record.Location,
                'account': account_name,
                'students': [s['name'] for s in students],
                'villagers': [v['name'] for v in villagers]
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.exception(f"創建記錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建記錄時發生錯誤: {str(e)}"
        )

# **更新家訪記錄**
@router.put("/update/{record_id}", response_model=dict)
def update_existing_record(
    record_id: int,
    record_data: schemas.RecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新家訪記錄
    
    Args:
        record_id (int): 要更新的家訪記錄ID
        record_data (schemas.RecordUpdate): 要更新的家訪記錄數據
        db (Session): 資料庫連線
        
    Returns:
        dict: 包含狀態和更新後的家訪記錄
    """
    # 檢查記錄是否存在
    db_record = db.query(models.Record).filter(models.Record.RecordID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到ID為 {record_id} 的家訪記錄"
        )
    
    try:
        # 更新家訪記錄
        updated_record = Record.update_record(db, record_id, record_data)
        
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新記錄時發生錯誤"
            )
        
        # 獲取完整的記錄信息
        record_info = db.query(
            models.Record,
            models.Account.Name.label('AccountName')
        ).join(
            models.Account, models.Record.Account == models.Account.AccountID
        ).filter(
            models.Record.RecordID == record_id
        ).first()
        
        if not record_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新記錄時發生錯誤"
            )
            
        record, account_name = record_info
        
        # 獲取學生和村民名單
        students = Record.get_students_by_record(db, record.RecordID)
        villagers = Record.get_villagers_by_record(db, record.RecordID)
        
        return {
            'status': 'success',
            'data': {
                'recordid': record.RecordID,
                'semester': record.Semester,
                'date': record.Date,
                'photo': record.Photo,
                'description': record.Description,
                'location': record.Location,
                'account': account_name,
                'students': [s['name'] for s in students],
                'villagers': [v['name'] for v in villagers]
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.exception(f"更新記錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新記錄時發生錯誤: {str(e)}"
        )

# **刪除家訪記錄**
@router.delete("/delete/{record_id}", status_code=status.HTTP_200_OK)
def delete_existing_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    刪除家訪記錄
    
    Args:
        record_id (int): 要刪除的家訪記錄ID
        db (Session): 資料庫連線
        
    Returns:
        dict: 包含狀態信息
    """
    # 檢查記錄是否存在
    db_record = db.query(models.Record).filter(models.Record.RecordID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到ID為 {record_id} 的家訪記錄"
        )
    
    try:
        # 刪除家訪記錄
        success = Record.delete_record(db, record_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刪除記錄時發生錯誤"
            )
            
        return {
            "status": "success", 
            "message": f"已成功刪除ID為 {record_id} 的家訪記錄"
        }
        
    except Exception as e:
        db.rollback()
        logger.exception(f"刪除記錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除記錄時發生錯誤: {str(e)}"
        )


