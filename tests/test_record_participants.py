"""家訪紀錄的參與大學生 / 受訪村民有沒有真的被撈出來。

直接執行： python tests/test_record_participants.py
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.crud import Record as record_crud


def _session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    # 關聯表在模型裡宣告了 schema='public'，sqlite 得先掛一個同名 schema
    @event.listens_for(engine, "connect")
    def _attach_public(dbapi_conn, _):
        dbapi_conn.execute("ATTACH DATABASE ':memory:' AS public")

    models.Base.metadata.create_all(
        engine,
        tables=[
            models.Account.__table__,
            models.Villager.__table__,
            models.Record.__table__,
            models.StudentsAtRecord.__table__,
            models.VillagersAtRecord.__table__,
        ],
    )
    return sessionmaker(bind=engine)()


def test_record_includes_participants():
    db = _session()
    db.add_all([
        models.Account(AccountID=1, Name="家訪小組", Password="x", EntrySemester="25S"),
        models.Account(AccountID=2, Name="彭靖淵", Password="x", EntrySemester="25S"),
        models.Villager(VillagerID=1, Name="江新武長老", Gender="M"),
        models.Villager(VillagerID=2, Name="胡阿男牧師", Gender="M"),
        models.Record(RecordID=1, Semester="19W", Date=date(2019, 1, 1), Location=6, Account=1),
        models.Record(RecordID=2, Semester="20S", Date=date(2020, 7, 1), Location=6, Account=1),
        models.StudentsAtRecord(Account=1, Record=1),
        models.StudentsAtRecord(Account=2, Record=1),
        models.VillagersAtRecord(Villager=1, Record=1),
        models.VillagersAtRecord(Villager=2, Record=1),
    ])
    db.commit()

    by_id = {r["recordid"]: r for r in record_crud.get_record_by_location_with_details(db, 6)}

    assert sorted(by_id[1]["students"]) == ["家訪小組", "彭靖淵"]
    # 前端用 villager_id 這個 key 判斷資料結構，改名會讓村民名稱變成物件
    assert by_id[1]["villagers"] == [
        {"villager_id": 1, "name": "江新武長老"},
        {"villager_id": 2, "name": "胡阿男牧師"},
    ]
    # 沒有關聯的紀錄要是空陣列，不是 None
    assert by_id[2]["students"] == [] and by_id[2]["villagers"] == []
    db.close()


if __name__ == "__main__":
    test_record_includes_participants()
    print("ok")
