# app/crud/Record.py - 完整替換版本

from sqlalchemy.orm import Session
from .. import models, schemas

def get_all_records(db: Session):
    """
    取得所有家訪紀錄
    
    Args:
        db (Session): 資料庫連線
    
    Returns:
        List[models.Record]: 所有家訪紀錄
    """
    return db.query(models.Record).order_by(models.Record.Date.desc()).all()

def get_record_by_id(db: Session, record_id: int):
    """
    根據 ID 取得單筆家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 紀錄 ID
    
    Returns:
        models.Record: 家訪紀錄，若未找到則回傳 None
    """
    return db.query(models.Record).filter(models.Record.RecordID == record_id).first()

def get_records_by_location(db: Session, location_id: int):
    """
    根據地點 ID 取得該地點的所有家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        location_id (int): 地點 ID
    
    Returns:
        List[models.Record]: 該地點的家訪紀錄列表
    """
    return db.query(models.Record).filter(
        models.Record.Location == location_id
    ).order_by(models.Record.Date.desc()).all()

def get_records_by_account(db: Session, account_id: int):
    """
    根據帳號 ID 取得該帳號創建的所有家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        account_id (int): 帳號 ID
    
    Returns:
        List[models.Record]: 該帳號的家訪紀錄列表
    """
    return db.query(models.Record).filter(
        models.Record.Account == account_id
    ).order_by(models.Record.Date.desc()).all()

def get_records_by_semester(db: Session, semester: str):
    """
    根據學期取得該學期的所有家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        semester (str): 學期代碼
    
    Returns:
        List[models.Record]: 該學期的家訪紀錄列表
    """
    return db.query(models.Record).filter(
        models.Record.Semester == semester
    ).order_by(models.Record.Date.desc()).all()

def create_record(db: Session, record: schemas.RecordCreate):
    """
    創建新的家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        record (schemas.RecordCreate): 家訪紀錄創建資料
    
    Returns:
        models.Record: 創建的家訪紀錄
    """
    db_record = models.Record(
        Semester=record.semester,
        Date=record.date,
        Photo=record.photo,
        Description=record.description,
        Location=record.location_id,
        Account=record.account_id
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def update_record(db: Session, record_id: int, record: schemas.RecordUpdate):
    """
    更新家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 紀錄 ID
        record (schemas.RecordUpdate): 更新資料
    
    Returns:
        models.Record: 更新後的家訪紀錄，若未找到則回傳 None
    """
    db_record = db.query(models.Record).filter(models.Record.RecordID == record_id).first()
    
    if not db_record:
        return None
    
    # 只更新提供的欄位
    if record.semester is not None:
        db_record.Semester = record.semester
    if record.date is not None:
        db_record.Date = record.date
    if record.photo is not None:
        db_record.Photo = record.photo
    if record.description is not None:
        db_record.Description = record.description
    if record.location_id is not None:
        db_record.Location = record.location_id
    if record.account_id is not None:
        db_record.Account = record.account_id
    
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_record(db: Session, record_id: int):
    """
    刪除家訪紀錄
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 紀錄 ID
    
    Returns:
        bool: 刪除成功返回 True，未找到紀錄返回 False
    """
    db_record = db.query(models.Record).filter(models.Record.RecordID == record_id).first()
    
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True

def get_records_count(db: Session):
    """
    取得家訪紀錄總數
    
    Args:
        db (Session): 資料庫連線
    
    Returns:
        int: 家訪紀錄總數
    """
    return db.query(models.Record).count()

def get_records_count_by_location(db: Session, location_id: int):
    """
    取得特定地點的家訪紀錄數量
    
    Args:
        db (Session): 資料庫連線
        location_id (int): 地點 ID
    
    Returns:
        int: 該地點的家訪紀錄數量
    """
    return db.query(models.Record).filter(models.Record.Location == location_id).count()

# ===== 舊版函數 - 保持向後兼容 =====

def get_records(db: Session):
    """舊版函數名稱，重定向到新版"""
    return get_all_records(db)

def get_record_by_location(db: Session, ID: int):
    """
    舊版函數 - 保持向後兼容
    根據位置取得特定家訪紀錄（簡化版本，只返回基本欄位）
    """
    records = get_records_by_location(db, ID)
    
    # 轉換為舊版格式
    result = []
    for record in records:
        record_dict = {
            'RecordID': record.RecordID,
            'Semester': record.Semester,
            'Date': record.Date,
            'Photo': record.Photo,
            'Description': record.Description,
            'Location': record.Location,
            'Account': record.Account,  # 注意：這裡直接返回 Account ID，不是名稱
        }
        result.append(record_dict)
    
    return result

def get_record_by_location_with_details(db: Session, location_id: int):
    """
    舊版函數 - 保持向後兼容
    根據地點ID獲取所有相關的家訪記錄（簡化版本）
    """
    records = get_records_by_location(db, location_id)
    
    # 轉換為舊版格式
    result = []
    for record in records:
        record_dict = {
            'recordid': record.RecordID,
            'semester': record.Semester,
            'date': record.Date,
            'photo': record.Photo,
            'description': record.Description,
            'location': record.Location,
            'account': record.Account,  # 簡化版本：直接返回 Account ID
            'students': [],  # 簡化版本：不包含學生資料
            'villagers': []  # 簡化版本：不包含村民資料
        }
        result.append(record_dict)
    
    return result

def get_students_by_record(db: Session, record_id: int):
    """
    舊版函數 - 保持向後兼容
    簡化版本：返回空列表
    """
    return []

def get_villagers_by_record(db: Session, record_id: int):
    """
    舊版函數 - 保持向後兼容
    簡化版本：返回空列表
    """
    return []

