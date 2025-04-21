# Purpose: 處理 locations API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud import Location
from ..database import get_db
from .. import schemas

router = APIRouter()

# **取得所有地點**
@router.get("/locations", response_model=dict, status_code=status.HTTP_200_OK)
def get_locations(db: Session = Depends(get_db)):
    location_list = Location.get_locations(db)

    if not location_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="沒有找到任何地點資料"
        )
    # 這裡的資料格式名是對應　models.py　的 Location
    return {
    "status": "success",
    "data": [
        schemas.LocationResponse(
            id=loc.LocationID,  # 保留大寫
            name=loc.name,  # 小寫
            latitude=loc.Latitude,  # ORM 是大寫，但 Schema 需要小寫
            longitude=loc.Longitude,
            address=loc.Address,
            brief_description=loc.BriefDescription,
            photo=loc.Photo,
            tag=loc.Tag
        )
        for loc in location_list
    ]
}


# 新增地點
@router.post("/location", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    new_loc = Location.add_location(db, location)
    return {
        "status": "success",
        "data": schemas.LocationResponse(
            id=new_loc.LocationID,
            name=new_loc.name,
            latitude=new_loc.Latitude,
            longitude=new_loc.Longitude,
            address=new_loc.Address,
            brief_description=new_loc.BriefDescription,
            photo=new_loc.Photo,
            tag=new_loc.Tag
        )
    }

# 編輯地點
@router.put("/location/{location_id}", response_model=dict)
def update_location(location_id: int, location: schemas.LocationUpdate, db: Session = Depends(get_db)):
    updated = Location.update_location(db, location_id, location)
    if not updated:
        raise HTTPException(status_code=404, detail="找不到該地點")
    return {
        "status": "success",
        "data": schemas.LocationResponse(
            id=updated.LocationID,
            name=updated.name,
            latitude=updated.Latitude,
            longitude=updated.Longitude,
            address=updated.Address,
            brief_description=updated.BriefDescription,
            photo=updated.Photo,
            tag=updated.Tag
        )
    }

# 刪除地點
@router.delete("/location/{location_id}", response_model=dict)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    success = Location.delete_location(db, location_id)
    if not success:
        raise HTTPException(status_code=404, detail="找不到該地點")
    return {
        "status": "success",
        "message": f"地點 (ID={location_id}) 已成功刪除"
    }

