# Purpose: 建立資料庫連線，並提供 DB session

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 載入 .env 變數
load_dotenv()

# **取得資料庫連線字串**
DATABASE_URL = os.getenv("DATABASE_URL")

# **修復連接洩漏的資料庫連線設定**
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,  # 縮短連接超時
        # "options": "-c statement_timeout=10000"  # 縮短查詢超時到10秒
    },
    # 嚴格的連接池設定防止洩漏
    pool_size=5,  # 減少基本連接池大小
    max_overflow=10,  # 減少額外連接數
    pool_timeout=20,  # 縮短獲取連接的超時時間
    pool_recycle=1800,  # 30分鐘後回收連接（更頻繁）
    pool_pre_ping=True,  # 使用前檢查連接是否有效
    
    # 新增：強制回收閒置連接
    pool_reset_on_return='commit',  # 返回時重置連接狀態
    echo=False  # 生產環境關閉 SQL 日誌
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# **改進的 DB session 函數 - 防止連接洩漏**
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        if db:
            db.rollback()
        print(f"Database session error: {e}")
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as close_error:
                print(f"Error closing database session: {close_error}")

# **添加連接池監控函數**
def get_pool_status():
    """獲取連接池狀態用於監控"""
    return {
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "checked_in": engine.pool.checkedin(),
        "overflow": engine.pool.overflow(),
        "invalid": engine.pool.invalid()
    }
