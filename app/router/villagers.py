# Purpose: 處理 Villager 相關 API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from ..crud import Villager
from ..database import get_db
from .. import schemas

# Import FastAPI router with tags
router = APIRouter(tags=["Villager"])

# **取得所有村民**
@router.get("/villager", response_model=dict, status_code=status.HTTP_200_OK)
def get_villagers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取一組村民
    
    Args:
        skip (int): 跳過記錄數，用於分頁
        limit (int): 限制記錄數，用於分頁
        db (Session): 資料庫連線
    
    Returns:
        dict: 包含村民列表的回應
    """
    villager_list = Villager.get_villagers(db, skip=skip, limit=limit)

    if not villager_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="沒有找到任何村民資料"
        )

    return {
        "status": "success",
        "data": [
            {
                "villagerid": villager.VillagerID,
                "name": villager.Name,
                "gender": villager.Gender,
                "job": villager.Job,
                "locationid": villager.Location
            }
            for villager in villager_list
        ]
    }

# **根據ID取得村民**
@router.get("/villager/{villager_id}", response_model=dict, status_code=status.HTTP_200_OK)
def get_villager_by_id(villager_id: int, db: Session = Depends(get_db)):
    """根據村民ID獲取村民詳細資訊，包含親屬關係
    
    Args:
        villager_id (int): 村民ID
        db (Session): 資料庫連線
    
    Returns:
        dict: 包含村民資料和親屬關係的回應
    """
    villager = Villager.get_villager_by_id(db, villager_id)

    if not villager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到對應的村民資料"
        )
    
    # 獲取親屬關係
    relationships = Villager.get_villager_relationships(db, villager_id)

    return {
        "status": "success",
        "data": schemas.VillagerDetailResponse(
            villagerid=villager.VillagerID,
            name=villager.Name,
            gender=villager.Gender,
            job=villager.Job,
            url=villager.URL,
            photo=villager.Photo,
            locationid=villager.Location,
            relationships=relationships
        )
    }

# **新增村民**
@router.post("/villager", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_villager(villager: schemas.VillagerCreate, db: Session = Depends(get_db)):
    """建立新的村民
    
    Args:
        villager (schemas.VillagerCreate): 村民創建資料
        db (Session): 資料庫連線
    
    Returns:
        dict: 創建成功的村民資料
    """
    new_villager = Villager.create_villager(db, villager)
    
    # 新村民還沒有親屬關係
    relationships = []
    
    return {
        "status": "success",
        "data": schemas.VillagerDetailResponse(
            villagerid=new_villager.VillagerID,
            name=new_villager.Name,
            gender=new_villager.Gender,
            job=new_villager.Job,
            url=new_villager.URL,
            photo=new_villager.Photo,
            locationid=new_villager.Location,
            relationships=relationships
        )
    }

# **更新村民**
@router.put("/villager/{villager_id}", response_model=dict)
def update_villager(villager_id: int, villager: schemas.VillagerUpdate, db: Session = Depends(get_db)):
    """更新單一村民資訊
    
    Args:
        villager_id (int): 村民ID
        villager (schemas.VillagerUpdate): 更新資料
        db (Session): 資料庫連線
    
    Returns:
        dict: 更新後的村民資料
    """
    updated = Villager.update_villager(db, villager_id, villager)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該村民"
        )
    
    # 獲取親屬關係
    relationships = Villager.get_villager_relationships(db, villager_id)
    
    return {
        "status": "success",
        "data": schemas.VillagerDetailResponse(
            villagerid=updated.VillagerID,
            name=updated.Name,
            gender=updated.Gender,
            job=updated.Job,
            url=updated.URL,
            photo=updated.Photo,
            locationid=updated.Location,
            relationships=relationships
        )
    }

# **刪除村民**
@router.delete("/villager/{villager_id}", response_model=dict)
def delete_villager(villager_id: int, db: Session = Depends(get_db)):
    """刪除單一村民資訊
    
    Args:
        villager_id (int): 村民ID
        db (Session): 資料庫連線
    
    Returns:
        dict: 操作結果
    """
    success = Villager.delete_villager(db, villager_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該村民"
        )
    
    return {
        "status": "success",
        "message": f"村民 (ID={villager_id}) 已成功刪除"
    }

# **根據地點ID取得村民**
@router.get("/villagers/location/{location_id}", response_model=dict, status_code=status.HTTP_200_OK)
def get_villagers_by_location(location_id: int, db: Session = Depends(get_db)):
    """獲取特定地點的村民
    
    Args:
        location_id (int): 地點ID
        db (Session): 資料庫連線
    
    Returns:
        dict: 包含村民列表的回應
    """
    villager_list = Villager.get_villagers_by_location(db, location_id)

    if not villager_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"沒有找到地點ID={location_id}的村民資料"
        )

    result = []
    for villager in villager_list:
        # 獲取親屬關係
        relationships = Villager.get_villager_relationships(db, villager.VillagerID)
        
        villager_data = {
            "villagerid": villager.VillagerID,
            "name": villager.Name,
            "gender": villager.Gender,
            "job": villager.Job,
            "url": villager.URL,
            "photo": villager.Photo,
            "locationid": villager.Location,
            "relationships": relationships
        }
        result.append(villager_data)

    return {
        "status": "success",
        "data": result
    }

# **添加村民親屬關係**
@router.post("/villager/relationship", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_relationship(relationship: schemas.RelationshipCreate, db: Session = Depends(get_db)):
    """添加村民親屬關係
    
    Args:
        relationship (schemas.RelationshipCreate): 關係創建資料
        db (Session): 資料庫連線
    
    Returns:
        dict: 操作結果
    """
    new_relationship = Villager.create_relationship(db, relationship)
    
    return {
        "status": "success",
        "message": "親屬關係添加成功",
        "data": {
            "relationship_id": new_relationship.RelationshipID,
            "source_villager_id": new_relationship.SourceVillagerID,
            "target_villager_id": new_relationship.TargetVillagerID,
            "relationship_type_id": new_relationship.RelationshipTypeID
        }
    }

# **刪除村民親屬關係**
@router.delete("/villager/relationship/{relationship_id}", response_model=dict)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db)):
    """移除村民親屬關係
    
    Args:
        relationship_id (int): 關係ID
        db (Session): 資料庫連線
    
    Returns:
        dict: 操作結果
    """
    success = Villager.delete_relationship(db, relationship_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該親屬關係"
        )
    
    return {
        "status": "success",
        "message": f"親屬關係 (ID={relationship_id}) 已成功移除"
    }