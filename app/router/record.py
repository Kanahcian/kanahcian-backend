# Purpose: 處理 Record 相關 API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud import Record
from ..database import get_db
from .. import schemas

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
#             photo=rec.Photo,
#             description=rec.Description,
#             location=rec.Location,
#             # villager=rec.Villager,
#             account=rec.Account,
#         )
#         for rec in record_list
#     ]
# }

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



