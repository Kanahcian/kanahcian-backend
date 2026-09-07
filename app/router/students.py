# Purpose: 處理 Student（大學生名單）相關 API

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..crud import Student
from ..database import get_db
from .. import schemas

router = APIRouter(tags=["Student"])


@router.get("/students", response_model=dict, status_code=status.HTTP_200_OK)
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """取得大學生名單（給前端「參與學生」勾選 UI 用）"""
    students = Student.get_students(db, skip=skip, limit=limit)
    return {
        "status": "success",
        "data": [schemas.StudentResponse.from_orm_student(s) for s in students],
    }


@router.get("/students/{student_id}", response_model=dict, status_code=status.HTTP_200_OK)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = Student.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到該大學生")
    return {"status": "success", "data": schemas.StudentResponse.from_orm_student(student)}


@router.post("/students", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    created = Student.create_student(db, student)
    return {"status": "success", "data": schemas.StudentResponse.from_orm_student(created)}


@router.put("/students/{student_id}", response_model=dict)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    updated = Student.update_student(db, student_id, student)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到該大學生")
    return {"status": "success", "data": schemas.StudentResponse.from_orm_student(updated)}


@router.delete("/students/{student_id}", response_model=dict)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    if not Student.delete_student(db, student_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到該大學生")
    return {"status": "success", "message": f"大學生 (ID={student_id}) 已成功刪除"}
