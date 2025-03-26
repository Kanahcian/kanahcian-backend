from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud import Villager
from ..database import get_db
from .. import schemas

router = APIRouter()

@router.get("/villager/{villager_id}", response_model = dict, status_code = status.HTTP_200_OK)
def get_villager_by_id(villager_id: int, db: Session = Depends(get_db)):
    villager = Villager.get_villager_by_id(db, villager_id)

    if not villager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "找不到對應的個人資料"
        )

    return {
        "status": "success",
        "data": schemas.VillagerResponse(
            villagerid = villager.VillagerID,
            name = villager.Name,
            gender = villager.Gender,
            job = villager.Job,
            url = villager.URL,
            photo = villager.Photo,
            locationid = villager.Location
        )
    }

