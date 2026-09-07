"""CRUD 層基本測試，直接打資料庫函式，不經過 FastAPI / 網路。"""
from datetime import date

import pytest

from app import models, schemas
from app.crud import Location as location_crud
from app.crud import Villager as villager_crud
from app.crud import Record as record_crud
from app.crud import Student as student_crud


# ---------- Location ----------

def _make_location(db, name="部落A"):
    return location_crud.add_location(
        db,
        schemas.LocationCreate(
            name=name, latitude=23.5, longitude=121.5,
            address="花蓮", brief_description="測試", tag=["tag1", "tag2"],
        ),
    )


def test_add_and_get_location(db):
    loc = _make_location(db)
    assert loc.LocationID is not None
    assert loc.Tag == ["tag1", "tag2"]

    all_locs = location_crud.get_locations(db)
    assert [l.name for l in all_locs] == ["部落A"]


def test_update_location(db):
    loc = _make_location(db)
    updated = location_crud.update_location(
        db, loc.LocationID,
        schemas.LocationUpdate(name="部落B", latitude=1, longitude=2, tag=["x"]),
    )
    assert updated.name == "部落B"
    assert updated.Tag == ["x"]


def test_update_missing_location_returns_none(db):
    assert location_crud.update_location(
        db, 9999,
        schemas.LocationUpdate(name="x", latitude=1, longitude=2),
    ) is None


def test_delete_location(db):
    loc = _make_location(db)
    assert location_crud.delete_location(db, loc.LocationID) is True
    assert location_crud.delete_location(db, loc.LocationID) is False
    assert location_crud.get_locations(db) == []


# ---------- Villager ----------

def _make_villager(db, loc_id, name="小明", gender="M"):
    return villager_crud.create_villager(
        db,
        schemas.VillagerCreate(name=name, gender=gender, job="務農", location_id=loc_id),
    )


def test_create_and_query_villager(db):
    loc = _make_location(db)
    v = _make_villager(db, loc.LocationID)
    assert v.VillagerID is not None

    assert villager_crud.get_villager_by_id(db, v.VillagerID).Name == "小明"
    assert len(villager_crud.get_villagers(db)) == 1
    assert len(villager_crud.get_villagers_by_location(db, loc.LocationID)) == 1
    assert villager_crud.get_villagers_by_location(db, 9999) == []


def test_update_and_delete_villager(db):
    loc = _make_location(db)
    v = _make_villager(db, loc.LocationID)

    updated = villager_crud.update_villager(
        db, v.VillagerID,
        schemas.VillagerUpdate(name="大明", gender="M", job="老師", location_id=loc.LocationID),
    )
    assert updated.Name == "大明" and updated.Job == "老師"

    assert villager_crud.delete_villager(db, v.VillagerID) is True
    assert villager_crud.delete_villager(db, v.VillagerID) is False
    assert villager_crud.get_villager_by_id(db, v.VillagerID) is None


def test_villager_relationship_roundtrip(db):
    loc = _make_location(db)
    father = _make_villager(db, loc.LocationID, name="父")
    son = _make_villager(db, loc.LocationID, name="子")

    rel_type = models.RelationshipType(Name="父子", Source_Role="父親", Target_Role="兒子")
    db.add(rel_type)
    db.commit()

    rel = villager_crud.create_relationship(
        db,
        schemas.RelationshipCreate(
            source_villager_id=father.VillagerID,
            target_villager_id=son.VillagerID,
            relationship_type_id=rel_type.RelationshipTypeID,
        ),
    )
    assert rel.RelationshipID is not None

    rels = villager_crud.get_villager_relationships(db, father.VillagerID)
    assert rels[0]["relative_name"] == "子"
    assert rels[0]["relationship_type"] == "父子"

    assert villager_crud.delete_relationship(db, rel.RelationshipID) is True
    assert villager_crud.get_villager_relationships(db, father.VillagerID) == []


def test_create_relationship_missing_villager_raises(db):
    loc = _make_location(db)
    v = _make_villager(db, loc.LocationID)
    rel_type = models.RelationshipType(Name="夫妻", Source_Role="夫", Target_Role="妻")
    db.add(rel_type)
    db.commit()

    with pytest.raises(ValueError):
        villager_crud.create_relationship(
            db,
            schemas.RelationshipCreate(
                source_villager_id=v.VillagerID,
                target_villager_id=9999,
                relationship_type_id=rel_type.RelationshipTypeID,
            ),
        )


# ---------- Record ----------

def _make_student(db):
    stu = models.Student(Name="家訪小組", EntrySemester="25S")
    db.add(stu)
    db.commit()
    return stu


# ---------- Student ----------

def test_student_crud_flow(db):
    created = student_crud.create_student(
        db, schemas.StudentCreate(name="彭靖淵", entry_semester="23S"),
    )
    assert created.StudentID is not None

    assert student_crud.get_student_by_id(db, created.StudentID).Name == "彭靖淵"
    assert [s.Name for s in student_crud.get_students(db)] == ["彭靖淵"]

    updated = student_crud.update_student(
        db, created.StudentID, schemas.StudentUpdate(entry_semester="24S"),
    )
    assert updated.EntrySemester == "24S" and updated.Name == "彭靖淵"

    assert student_crud.update_student(
        db, 9999, schemas.StudentUpdate(name="x"),
    ) is None

    assert student_crud.delete_student(db, created.StudentID) is True
    assert student_crud.delete_student(db, created.StudentID) is False
    assert student_crud.get_students(db) == []


def test_delete_student_clears_record_link(db):
    loc = _make_location(db)
    stu = _make_student(db)
    rec = record_crud.create_record(
        db,
        schemas.RecordCreate(
            semester="25S", date=date(2025, 3, 1), location_id=loc.LocationID,
        ),
    )
    db.add(models.StudentsAtRecord(Student=stu.StudentID, Record=rec.RecordID))
    db.commit()

    assert student_crud.delete_student(db, stu.StudentID) is True
    assert db.query(models.StudentsAtRecord).count() == 0


def test_record_crud_flow(db):
    loc = _make_location(db)

    rec = record_crud.create_record(
        db,
        schemas.RecordCreate(
            semester="25S", date=date(2025, 3, 1), description="第一次",
            location_id=loc.LocationID,
        ),
    )
    assert rec.RecordID is not None
    assert record_crud.get_records_count(db) == 1
    assert record_crud.get_records_count_by_location(db, loc.LocationID) == 1

    assert record_crud.get_record_by_id(db, rec.RecordID).Semester == "25S"
    assert len(record_crud.get_records_by_location(db, loc.LocationID)) == 1
    assert len(record_crud.get_records_by_semester(db, "25S")) == 1
    assert record_crud.get_records_by_semester(db, "99W") == []

    updated = record_crud.update_record(
        db, rec.RecordID, schemas.RecordUpdate(description="更新後"),
    )
    assert updated.Description == "更新後" and updated.Semester == "25S"

    assert record_crud.delete_record(db, rec.RecordID) is True
    assert record_crud.delete_record(db, rec.RecordID) is False
    assert record_crud.get_records_count(db) == 0


def test_record_with_details_includes_participants(db):
    loc = _make_location(db)
    stu = _make_student(db)
    v = villager_crud.create_villager(
        db, schemas.VillagerCreate(name="村民甲", gender="F", location_id=loc.LocationID),
    )
    rec = record_crud.create_record(
        db,
        schemas.RecordCreate(
            semester="25S", date=date(2025, 3, 1),
            location_id=loc.LocationID,
        ),
    )
    db.add(models.StudentsAtRecord(Student=stu.StudentID, Record=rec.RecordID))
    db.add(models.VillagersAtRecord(Villager=v.VillagerID, Record=rec.RecordID))
    db.commit()

    # 第二筆沒有任何參與者，students/villagers 要是空陣列而不是 None
    record_crud.create_record(
        db,
        schemas.RecordCreate(
            semester="25S", date=date(2025, 2, 1),
            location_id=loc.LocationID,
        ),
    )

    by_id = {d["recordid"]: d for d in
             record_crud.get_record_by_location_with_details(db, loc.LocationID)}
    assert by_id[rec.RecordID]["students"] == ["家訪小組"]
    assert by_id[rec.RecordID]["villagers"] == [{"villager_id": v.VillagerID, "name": "村民甲"}]
    other = next(d for rid, d in by_id.items() if rid != rec.RecordID)
    assert other["students"] == [] and other["villagers"] == []
