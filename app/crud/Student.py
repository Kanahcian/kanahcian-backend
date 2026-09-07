# 負責 Student（大學生名單）的資料庫 CRUD

from sqlalchemy.orm import Session
from .. import models, schemas


def get_students(db: Session, skip: int = 0, limit: int = 100):
    """取得所有大學生（支援分頁）"""
    return (
        db.query(models.Student)
        .order_by(models.Student.EntrySemester, models.Student.StudentID)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_student_by_id(db: Session, student_id: int):
    """根據 ID 取得單一大學生，未找到回傳 None"""
    return db.query(models.Student).filter(models.Student.StudentID == student_id).first()


def create_student(db: Session, student: schemas.StudentCreate):
    """新增大學生"""
    db_student = models.Student(
        Name=student.name,
        EntrySemester=student.entry_semester,
        Photo=student.photo,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    """更新大學生，只改有提供的欄位；未找到回傳 None"""
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return None

    if student.name is not None:
        db_student.Name = student.name
    if student.entry_semester is not None:
        db_student.EntrySemester = student.entry_semester
    if student.photo is not None:
        db_student.Photo = student.photo

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int):
    """刪除大學生，連同其家訪紀錄關聯；未找到回傳 False"""
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return False

    db.query(models.StudentsAtRecord).filter(
        models.StudentsAtRecord.Student == student_id
    ).delete()
    db.delete(db_student)
    db.commit()
    return True
