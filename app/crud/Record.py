# 負責 Record 的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas

# **取得所有家訪紀錄**
def get_records(db: Session):
    return db.query(models.Record).all()

# **根據位置取得特定家訪紀錄**
def get_record_by_location(db: Session, ID: int) -> list:
    # return db.query(models.Record).filter(models.Record.Location == ID).order_by(models.Record.Date.desc()).all()
    """
    根據地點ID獲取所有相關的家訪記錄，並將Account ID轉換為Account名稱
    
    Args:
        db (Session): 資料庫連線
        ID (int): 地點ID (LocationID)
    
    Returns:
        List: 包含豐富資訊的記錄列表，記錄中的Account欄位已替換為Account名稱
    """
    # 使用JOIN連接Record和Account表格
    records_query = (db.query(
            models.Record,
            models.Account.Name.label('AccountName')  # 取得Account名稱
        )
        .join(models.Account, models.Record.Account == models.Account.AccountID)  # 連結Account表
        .filter(models.Record.Location == ID)  # 篩選特定地點
        .order_by(models.Record.Date.desc())  # 依日期降序排列
    ).all()
    
    # 轉換查詢結果為適合返回的格式
    result = []
    for record, account_name in records_query:
        # 建立新的記錄字典，包含所有Record欄位
        record_dict = {
            'RecordID': record.RecordID,
            'Semester': record.Semester,
            'Date': record.Date,
            'Photo': record.Photo,
            'Description': record.Description,
            'Location': record.Location,
            'Account': account_name,  # 將Account ID替換為名稱
        }
        
        # 添加到結果列表
        result.append(record_dict)
    
    return result

# **根據紀錄 id 取得該次家訪的大學生名單**
def get_students_by_record(db: Session, record_id: int) -> list:
    """
    使用 JOIN 查詢根據家訪紀錄ID取得參與的大學生資訊 (優化版)
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 家訪紀錄ID
    
    Returns:
        list: 參與該家訪紀錄的大學生資訊列表
    """
    # 使用 JOIN 一次性查詢學生資料
    students = (db.query(
                    models.Account.AccountID,
                    models.Account.Name,
                    models.Account.EntrySemester,
                    models.Account.Photo
                )
                .join(
                    models.StudentsAtRecord,
                    models.Account.AccountID == models.StudentsAtRecord.Account
                )
                .filter(models.StudentsAtRecord.Record == record_id)
                .all())
    
    # 轉換查詢結果為字典列表
    student_info = [
        {
            'account_id': student.AccountID,
            'name': student.Name,
        }
        for student in students
    ]
    
    return student_info

# **根據紀錄 id 取得該次家訪的村民名單**
def get_villagers_by_record(db: Session, record_id: int) -> list:
    """
    使用 JOIN 查詢根據家訪紀錄ID取得相關的村民資訊 (優化版)
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 家訪紀錄ID
    
    Returns:
        list: 與該家訪紀錄相關的村民資訊列表
    """
    # 使用 JOIN 一次性查詢村民資料
    villagers = (db.query(
                    models.Villager.VillagerID,
                    models.Villager.Name,
                    models.Villager.Gender,
                    models.Villager.Job,
                    models.Villager.Photo,
                    models.Villager.Location,
                    models.Villager.URL
                )
                .join(
                    models.VillagersAtRecord,
                    models.Villager.VillagerID == models.VillagersAtRecord.Villager
                )
                .filter(models.VillagersAtRecord.Record == record_id)
                .all())
    
    # 轉換查詢結果為字典列表
    villager_info = [
        {
            'villager_id': villager.VillagerID,
            'name': villager.Name,
        }
        for villager in villagers
    ]
    
    return villager_info

# **根據地點ID獲取所有相關的家訪記錄**
def get_record_by_location_with_details(db: Session, location_id: int) -> list:
    """
    根據地點ID獲取所有相關的家訪記錄，包含:
    - 記錄基本資訊
    - 負責人名稱
    - 參與的大學生名單
    - 相關的村民名單
    
    Args:
        db (Session): 資料庫連線
        location_id (int): 地點ID (LocationID)
    
    Returns:
        List: 包含完整家訪資訊的記錄列表
    """
    # 使用JOIN連接Record和Account表格獲取基本資訊
    records_query = (db.query(
            models.Record,
            models.Account.Name.label('AccountName')  # 取得Account名稱
        )
        .join(models.Account, models.Record.Account == models.Account.AccountID)  # 連結Account表
        .filter(models.Record.Location == location_id)  # 篩選特定地點
        .order_by(models.Record.Date.desc())  # 依日期降序排列
    ).all()
    
    # 如果沒有找到記錄，直接返回空列表
    if not records_query:
        return []
    
    # 轉換查詢結果為適合返回的格式
    result = []
    for record, account_name in records_query:
        # 查詢此記錄關聯的大學生
        students = (db.query(models.Account.Name)
                    .join(models.StudentsAtRecord, models.Account.AccountID == models.StudentsAtRecord.Account)
                    .filter(models.StudentsAtRecord.Record == record.RecordID)
                    .all())
        student_names = [student[0] for student in students]
        
        # 查詢此記錄關聯的村民
        villagers = (db.query(models.Villager.Name)
                    .join(models.VillagersAtRecord, models.Villager.VillagerID == models.VillagersAtRecord.Villager)
                    .filter(models.VillagersAtRecord.Record == record.RecordID)
                    .all())
        villager_names = [villager[0] for villager in villagers]
        
        # 建立新的記錄字典，包含所有需要的資訊
        record_dict = {
            'recordid': record.RecordID,
            'semester': record.Semester,
            'date': record.Date,
            'photo': record.Photo,
            'description': record.Description,
            'location': record.Location,
            'account': account_name,  # 將Account ID替換為名稱
            'students': student_names,  # 參與家訪的大學生名單
            'villagers': villager_names  # 相關的村民名單
        }
        
        # 添加到結果列表
        result.append(record_dict)
    
    return result

def create_record(db: Session, record_data: schemas.RecordCreate) -> models.Record:
    """
    創建新的家訪記錄
    
    Args:
        db (Session): 資料庫連線
        record_data (schemas.RecordCreate): 家訪記錄數據
        
    Returns:
        models.Record: 創建的家訪記錄
    """
    # 創建家訪記錄
    db_record = models.Record(
        Semester=record_data.semester,
        Date=record_data.date,
        Photo=record_data.photo,
        Description=record_data.description,
        Location=record_data.location_id,
        Account=record_data.account_id
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 添加參與的學生
    for student_id in record_data.student_ids:
        db_student_record = models.StudentsAtRecord(
            Account=student_id,
            Record=db_record.RecordID
        )
        db.add(db_student_record)
    
    # 添加相關的村民
    for villager_id in record_data.villager_ids:
        db_villager_record = models.VillagersAtRecord(
            Villager=villager_id,
            Record=db_record.RecordID
        )
        db.add(db_villager_record)
    
    db.commit()
    return db_record

def update_record(db: Session, record_id: int, record_data: schemas.RecordUpdate) -> models.Record:
    """
    更新家訪記錄
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 家訪記錄ID
        record_data (schemas.RecordUpdate): 要更新的家訪記錄數據
        
    Returns:
        models.Record: 更新後的家訪記錄
    """
    # 獲取現有的記錄
    db_record = db.query(models.Record).filter(models.Record.RecordID == record_id).first()
    if not db_record:
        return None
    
    # 更新基本資訊
    if record_data.semester is not None:
        db_record.Semester = record_data.semester
    if record_data.date is not None:
        db_record.Date = record_data.date
    if record_data.photo is not None:
        db_record.Photo = record_data.photo
    if record_data.description is not None:
        db_record.Description = record_data.description
    if record_data.location_id is not None:
        db_record.Location = record_data.location_id
    if record_data.account_id is not None:
        db_record.Account = record_data.account_id
    
    # 如果需要更新學生列表
    if record_data.student_ids is not None:
        # 刪除現有的學生關聯
        db.query(models.StudentsAtRecord).filter(
            models.StudentsAtRecord.Record == record_id
        ).delete()
        
        # 添加新的學生關聯
        for student_id in record_data.student_ids:
            db_student_record = models.StudentsAtRecord(
                Account=student_id,
                Record=record_id
            )
            db.add(db_student_record)
    
    # 如果需要更新村民列表
    if record_data.villager_ids is not None:
        # 刪除現有的村民關聯
        db.query(models.VillagersAtRecord).filter(
            models.VillagersAtRecord.Record == record_id
        ).delete()
        
        # 添加新的村民關聯
        for villager_id in record_data.villager_ids:
            db_villager_record = models.VillagersAtRecord(
                Villager=villager_id,
                Record=record_id
            )
            db.add(db_villager_record)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_record(db: Session, record_id: int) -> bool:
    """
    刪除家訪記錄
    
    Args:
        db (Session): 資料庫連線
        record_id (int): 要刪除的家訪記錄ID
        
    Returns:
        bool: 是否成功刪除
    """
    # 刪除相關的學生關聯
    db.query(models.StudentsAtRecord).filter(
        models.StudentsAtRecord.Record == record_id
    ).delete()
    
    # 刪除相關的村民關聯
    db.query(models.VillagersAtRecord).filter(
        models.VillagersAtRecord.Record == record_id
    ).delete()
    
    # 刪除家訪記錄
    result = db.query(models.Record).filter(
        models.Record.RecordID == record_id
    ).delete()
    
    db.commit()
    return result > 0