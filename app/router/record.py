# app/router/record.py - 修復版本（兼容現有代碼）

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..crud import Record
from ..database import get_db
from .. import schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Record"])

# ===== 修復後的原有接口 =====

@router.post("/records", response_model=dict)
def get_record_by_location(
    location: schemas.LocationID,  # 使用原有的 LocationID schema
    db: Session = Depends(get_db)
):
    """
    根據地點 ID 獲取所有相關的家訪記錄（修復版本）
    
    Args:
        location (schemas.LocationID): 包含地點 ID 的請求物件
        db (Session): 資料庫連線
    
    Returns:
        dict: 包含狀態和完整家訪資料的回應
    """
    try:
        logger.info(f"正在查詢地點 ID: {location.locationid} 的家訪記錄")
        
        # 使用簡化的查詢函數
        record_list = Record.get_record_by_location_with_details(db, location.locationid)
        
        logger.info(f"查詢到 {len(record_list)} 條記錄")
        
        if not record_list:
            logger.warning(f"地點 ID {location.locationid} 沒有找到家訪記錄")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"沒有找到地點 ID={location.locationid} 的家訪記錄"
            )

        logger.info(f"成功返回 {len(record_list)} 條家訪記錄")
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

# ===== 新增的接口（提供更多選擇） =====

@router.get("/records/location/{location_id}", response_model=dict)
def get_records_by_location_get(
    location_id: int = Path(..., description="地點 ID"),
    db: Session = Depends(get_db)
):
    """
    使用 GET 方法根據地點 ID 獲取家訪記錄（新增的替代方案）
    
    Args:
        location_id: 地點 ID
        db: 資料庫連線
    
    Returns:
        dict: 包含狀態和家訪記錄列表的回應
    """
    try:
        logger.info(f"GET 方法查詢地點 ID: {location_id} 的家訪記錄")
        
        records = Record.get_records_by_location(db, location_id)
        
        if not records:
            return {
                "status": "success", 
                "data": [],
                "message": f"地點 ID {location_id} 沒有家訪記錄"
            }
        
        # 轉換為回應格式
        record_responses = [
            schemas.RecordResponse.from_orm_record(record) 
            for record in records
        ]
        
        logger.info(f"找到 {len(record_responses)} 筆記錄")
        
        return {
            "status": "success",
            "data": record_responses,
            "total": len(record_responses)
        }
        
    except Exception as e:
        logger.exception(f"GET 方法查詢記錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢記錄失敗: {str(e)}"
        )

@router.post("/records/by-location", response_model=dict)
def get_records_by_location_post(
    location_param: schemas.LocationIdParam,
    db: Session = Depends(get_db)
):
    """
    根據地點 ID 獲取該地點的所有家訪記錄（新版 POST 方法）
    
    Args:
        location_param: 包含地點 ID 的參數
        db: 資料庫連線
    
    Returns:
        dict: 包含狀態和家訪記錄列表的回應
    """
    try:
        logger.info(f"POST 方法查詢地點 ID: {location_param.location_id} 的家訪記錄")
        
        records = Record.get_records_by_location(db, location_param.location_id)
        
        if not records:
            return {
                "status": "success",
                "data": [],
                "message": f"地點 ID {location_param.location_id} 沒有家訪記錄"
            }
        
        # 轉換為回應格式
        record_responses = [
            schemas.RecordResponse.from_orm_record(record) 
            for record in records
        ]
        
        logger.info(f"找到 {len(record_responses)} 筆記錄")
        
        return {
            "status": "success",
            "data": record_responses,
            "total": len(record_responses)
        }
        
    except Exception as e:
        logger.exception(f"查詢地點記錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢記錄失敗: {str(e)}"
        )

# ===== 基本 CRUD 接口 =====

@router.get("/records", response_model=dict)
def get_all_records(
    skip: int = Query(0, ge=0, description="跳過的記錄數"),
    limit: int = Query(100, ge=1, le=1000, description="返回的記錄數限制"),
    db: Session = Depends(get_db)
):
    """獲取所有家訪記錄"""
    try:
        all_records = Record.get_all_records(db)
        total = len(all_records)
        records = all_records[skip:skip + limit]
        
        if not records:
            return {
                "status": "success",
                "data": [],
                "total": 0,
                "skip": skip,
                "limit": limit
            }
        
        record_responses = [
            schemas.RecordResponse.from_orm_record(record) 
            for record in records
        ]
        
        return {
            "status": "success",
            "data": record_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
            "returned": len(record_responses)
        }
        
    except Exception as e:
        logger.exception(f"獲取所有記錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取記錄失敗: {str(e)}"
        )

@router.get("/records/{record_id}", response_model=dict)
def get_record_by_id(
    record_id: int = Path(..., description="記錄 ID"),
    db: Session = Depends(get_db)
):
    """根據 ID 獲取單筆家訪記錄"""
    try:
        record = Record.get_record_by_id(db, record_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到 ID 為 {record_id} 的家訪記錄"
            )
        
        return {
            "status": "success",
            "data": schemas.RecordResponse.from_orm_record(record)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"獲取記錄 {record_id} 時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取記錄失敗: {str(e)}"
        )

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_record(
    record_data: schemas.RecordCreate,
    db: Session = Depends(get_db)
):
    """創建新的家訪記錄"""
    try:
        new_record = Record.create_record(db, record_data)
        
        return {
            "status": "success",
            "message": "家訪記錄創建成功",
            "data": schemas.RecordResponse.from_orm_record(new_record)
        }
        
    except Exception as e:
        logger.exception(f"創建記錄時發生錯誤: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建記錄失敗: {str(e)}"
        )

@router.put("/update/{record_id}", response_model=dict)
def update_existing_record(
    record_id: int,
    record_data: schemas.RecordUpdate,
    db: Session = Depends(get_db)
):
    """更新家訪記錄"""
    try:
        updated_record = Record.update_record(db, record_id, record_data)
        
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到ID為 {record_id} 的家訪記錄"
            )
        
        return {
            "status": "success",
            "message": "家訪記錄更新成功",
            "data": schemas.RecordResponse.from_orm_record(updated_record)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"更新記錄時發生錯誤: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新記錄失敗: {str(e)}"
        )

@router.delete("/delete/{record_id}", status_code=status.HTTP_200_OK)
def delete_existing_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """刪除家訪記錄"""
    try:
        success = Record.delete_record(db, record_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到ID為 {record_id} 的家訪記錄"
            )
            
        return {
            "status": "success", 
            "message": f"已成功刪除ID為 {record_id} 的家訪記錄"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"刪除記錄時發生錯誤: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除記錄時發生錯誤: {str(e)}"
        )

# ===== 調試接口 =====

@router.get("/records/debug/all", response_model=dict)
def debug_all_records(db: Session = Depends(get_db)):
    """調試用：獲取所有家訪記錄的基本信息"""
    try:
        all_records = Record.get_all_records(db)
        
        result = []
        null_account_count = 0
        null_location_count = 0
        
        for record in all_records:
            if record.Account is None:
                null_account_count += 1
            if record.Location is None:
                null_location_count += 1
                
            result.append({
                "record_id": record.RecordID,
                "location_id": record.Location,
                "account_id": record.Account,
                "semester": record.Semester,
                "date": str(record.Date) if record.Date else None,
                "has_null_account": record.Account is None,
                "has_null_location": record.Location is None
            })
        
        return {
            "status": "success",
            "total_records": len(result),
            "null_account_count": null_account_count,
            "null_location_count": null_location_count,
            "data": result
        }
        
    except Exception as e:
        logger.exception(f"調試查詢發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"調試查詢錯誤: {str(e)}"
        )

@router.get("/records/debug/location/{location_id}", response_model=dict)
def debug_records_by_location(location_id: int, db: Session = Depends(get_db)):
    """調試用：檢查特定地點的記錄查詢"""
    try:
        # 原始查詢，檢查資料品質
        raw_records = db.query(models.Record).filter(
            models.Record.Location == location_id
        ).all()
        
        result = []
        for record in raw_records:
            try:
                # 嘗試轉換為 RecordResponse
                record_response = schemas.RecordResponse.from_orm_record(record)
                conversion_success = True
                conversion_error = None
            except Exception as e:
                conversion_success = False
                conversion_error = str(e)
                record_response = None
            
            result.append({
                "raw_record": {
                    "record_id": record.RecordID,
                    "location": record.Location,
                    "account": record.Account,
                    "semester": record.Semester,
                    "date": str(record.Date) if record.Date else None,
                    "photo": record.Photo,
                    "description": record.Description
                },
                "conversion_success": conversion_success,
                "conversion_error": conversion_error,
                "converted_response": record_response.dict() if record_response else None
            })
        
        return {
            "status": "debug",
            "location_id": location_id,
            "raw_records_count": len(raw_records),
            "data": result
        }
        
    except Exception as e:
        logger.exception(f"調試查詢發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"調試查詢錯誤: {str(e)}"
        )