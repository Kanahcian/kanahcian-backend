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
            # address=loc.Address,
        )
        for loc in location_list
    ]
}


# **新增地點**
@router.post("/add_location", response_model=schemas.LocationResponse)
def add_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    return Location.add_location(db, location)
