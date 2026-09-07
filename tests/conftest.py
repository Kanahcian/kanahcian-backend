"""測試共用設定：用記憶體 SQLite 取代 Postgres，不需要任何外部服務。

必須在 import app.* 之前設定 DATABASE_URL，讓 app.database 建立 SQLite engine。
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory

import pytest
from sqlalchemy import event

from app.database import engine, SessionLocal
from app import models


# 關聯表在模型裡宣告了 schema='public'，SQLite 需要先掛一個同名 schema
@event.listens_for(engine, "connect")
def _attach_public_schema(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("ATTACH DATABASE ':memory:' AS public")
    cur.close()


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """每個測試一個 session，結束後清空所有表。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(models.Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()
