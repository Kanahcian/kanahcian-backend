# 負責 Villager 的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas

def get_villager_by_id(db: Session, villager_id: int):
    """
    根據ID取得村民資料
    
    Args:
        db (Session): 資料庫連線
        villager_id (int): 村民ID
    
    Returns:
        models.Villager: 村民資料
    """
    return db.query(models.Villager).filter(models.Villager.VillagerID == villager_id).first()

def get_villagers(db: Session, skip: int = 0, limit: int = 100):
    """
    取得所有村民 (支援分頁)
    
    Args:
        db (Session): 資料庫連線
        skip (int): 跳過筆數
        limit (int): 取得筆數上限
    
    Returns:
        List[models.Villager]: 村民資料列表
    """
    return db.query(models.Villager).offset(skip).limit(limit).all()

def get_villagers_by_location(db: Session, location_id: int):
    """
    根據地點ID取得該地點的所有村民
    
    Args:
        db (Session): 資料庫連線
        location_id (int): 地點ID
    
    Returns:
        List[models.Villager]: 村民資料列表
    """
    return db.query(models.Villager).filter(models.Villager.Location == location_id).all()

def create_villager(db: Session, villager: schemas.VillagerCreate):
    """
    新增村民資料
    
    Args:
        db (Session): 資料庫連線
        villager (schemas.VillagerCreate): 村民資料
    
    Returns:
        models.Villager: 新增的村民資料
    """
    # 將 schema 轉換為與 ORM 模型相符的格式
    villager_data = {
        "Name": villager.name,
        "Gender": villager.gender,
        "Job": villager.job,
        "URL": villager.url,
        "Photo": villager.photo,
        "Location": villager.location_id
    }
    
    new_villager = models.Villager(**villager_data)
    db.add(new_villager)
    db.commit()
    db.refresh(new_villager)
    return new_villager

def update_villager(db: Session, villager_id: int, villager: schemas.VillagerUpdate):
    """
    更新村民資料
    
    Args:
        db (Session): 資料庫連線
        villager_id (int): 村民ID
        villager (schemas.VillagerUpdate): 更新的村民資料
    
    Returns:
        models.Villager: 更新後的村民資料，若未找到則回傳 None
    """
    db_villager = db.query(models.Villager).filter(models.Villager.VillagerID == villager_id).first()
    
    if not db_villager:
        return None
    
    # 更新村民資料
    db_villager.Name = villager.name
    db_villager.Gender = villager.gender
    db_villager.Job = villager.job
    db_villager.URL = villager.url
    db_villager.Photo = villager.photo
    db_villager.Location = villager.location_id
    
    db.commit()
    db.refresh(db_villager)
    return db_villager

def delete_villager(db: Session, villager_id: int):
    """
    刪除村民資料
    
    Args:
        db (Session): 資料庫連線
        villager_id (int): 村民ID
    
    Returns:
        bool: 刪除成功返回 True，未找到村民返回 False
    """
    # 先確認是否存在
    db_villager = db.query(models.Villager).filter(models.Villager.VillagerID == villager_id).first()
    
    if not db_villager:
        return False
    
    # 刪除相關的親屬關係 (先處理外鍵約束)
    db.query(models.VillagerRelationship).filter(
        (models.VillagerRelationship.SourceVillagerID == villager_id) | 
        (models.VillagerRelationship.TargetVillagerID == villager_id)
    ).delete()
    
    # 刪除村民與家訪紀錄的關聯
    db.query(models.VillagersAtRecord).filter(
        models.VillagersAtRecord.Villager == villager_id
    ).delete()
    
    # 刪除村民
    db.delete(db_villager)
    db.commit()
    return True

def get_villager_relationships(db: Session, villager_id: int):
    """
    取得村民的親屬關係
    
    Args:
        db (Session): 資料庫連線
        villager_id (int): 村民ID
    
    Returns:
        List[dict]: 親屬關係列表
    """
    # 查詢該村民作為源頭的親屬關係
    source_relationships = (
        db.query(
            models.VillagerRelationship,
            models.RelationshipType,
            models.Villager.Name.label('relative_name')
        )
        .join(
            models.RelationshipType, 
            models.VillagerRelationship.RelationshipTypeID == models.RelationshipType.RelationshipTypeID
        )
        .join(
            models.Villager, 
            models.VillagerRelationship.TargetVillagerID == models.Villager.VillagerID
        )
        .filter(models.VillagerRelationship.SourceVillagerID == villager_id)
        .all()
    )

    # 查詢該村民作為目標的親屬關係
    target_relationships = (
        db.query(
            models.VillagerRelationship,
            models.RelationshipType,
            models.Villager.Name.label('relative_name')
        )
        .join(
            models.RelationshipType, 
            models.VillagerRelationship.RelationshipTypeID == models.RelationshipType.RelationshipTypeID
        )
        .join(
            models.Villager, 
            models.VillagerRelationship.SourceVillagerID == models.Villager.VillagerID
        )
        .filter(models.VillagerRelationship.TargetVillagerID == villager_id)
        .all()
    )

    # 整理結果
    relationships = []
    
    # 處理源頭關係
    for relationship, rel_type, relative_name in source_relationships:
        relationships.append({
            'relationship_id': relationship.RelationshipID,
            'relative_id': relationship.TargetVillagerID,
            'relative_name': relative_name,
            'relationship_type': rel_type.Name,
            'role': rel_type.Source_Role
        })
    
    # 處理目標關係
    for relationship, rel_type, relative_name in target_relationships:
        relationships.append({
            'relationship_id': relationship.RelationshipID,
            'relative_id': relationship.SourceVillagerID,
            'relative_name': relative_name,
            'relationship_type': rel_type.Name,
            'role': rel_type.Target_Role
        })
    
    return relationships

def create_relationship(db: Session, relationship: schemas.RelationshipCreate):
    """
    建立村民親屬關係
    
    Args:
        db (Session): 資料庫連線
        relationship (schemas.RelationshipCreate): 親屬關係資料
    
    Returns:
        models.VillagerRelationship: 新建立的親屬關係
    """
    # 檢查兩個村民是否存在
    source_villager = get_villager_by_id(db, relationship.source_villager_id)
    target_villager = get_villager_by_id(db, relationship.target_villager_id)
    
    if not source_villager or not target_villager:
        raise ValueError("找不到指定的村民")
    
    # 檢查關係類型是否存在
    relationship_type = db.query(models.RelationshipType).filter(
        models.RelationshipType.RelationshipTypeID == relationship.relationship_type_id
    ).first()
    
    if not relationship_type:
        raise ValueError("找不到指定的關係類型")
    
    # 建立新的親屬關係
    new_relationship = models.VillagerRelationship(
        SourceVillagerID=relationship.source_villager_id,
        TargetVillagerID=relationship.target_villager_id,
        RelationshipTypeID=relationship.relationship_type_id
    )
    
    db.add(new_relationship)
    db.commit()
    db.refresh(new_relationship)
    return new_relationship

def delete_relationship(db: Session, relationship_id: int):
    """
    刪除村民親屬關係
    
    Args:
        db (Session): 資料庫連線
        relationship_id (int): 親屬關係ID
    
    Returns:
        bool: 刪除成功返回 True，未找到關係返回 False
    """
    # 先確認是否存在
    relationship = db.query(models.VillagerRelationship).filter(
        models.VillagerRelationship.RelationshipID == relationship_id
    ).first()
    
    if not relationship:
        return False
    
    # 刪除親屬關係
    db.delete(relationship)
    db.commit()
    return True