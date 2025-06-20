# Purpose: FastAPI 應用程式的進入點

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import locations, record, villagers
from app.database import Base, engine, get_pool_status
from app.utils.connection_monitor import connection_monitor
import threading
import time
import requests
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# **建立資料表**
Base.metadata.create_all(bind=engine)

# **FastAPI 應用程式**
app = FastAPI()

# **設定 CORS**
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **掛載 API 路由**
app.include_router(locations.router, prefix="/api")
app.include_router(record.router, prefix="/api")
app.include_router(villagers.router, prefix="/api")

# **測試 API**
@app.get("/")
def read_root():
    return {"message": "FastAPI 伺服器運行中"}

# **連接池監控端點**
@app.get("/api/pool-status")
def get_connection_pool_status():
    """監控連接池狀態"""
    try:
        status = get_pool_status()
        return {
            "status": "ok",
            "pool_info": status,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# **改進的 Keep Alive 機制**
KEEP_ALIVE_URL = "https://kanahcian-backend.onrender.com/"
KEEP_ALIVE_INTERVAL = 300  # 改為 5 分鐘（減少頻率）

# 添加停止標誌
keep_alive_stop_event = threading.Event()

def keep_alive():
    """改進的 Keep Alive 函數，避免連接洩漏"""
    initial_delay = 60
    time.sleep(initial_delay)
    
    session = requests.Session()  # 重用 session
    session.timeout = 10  # 設置超時
    
    try:
        while not keep_alive_stop_event.is_set():
            try:
                # 使用更輕量的端點
                response = session.get(f"{KEEP_ALIVE_URL}api/pool-status", timeout=10)
                
                if response.status_code == 200:
                    pool_info = response.json().get('pool_info', {})
                    checked_out = pool_info.get('checked_out', 0)
                    
                    logger.info(f"Keep-alive successful. Active connections: {checked_out}")
                    
                    # 如果連接數過高，發出警告
                    if checked_out > 15:
                        logger.warning(f"High connection count detected: {checked_out}")
                else:
                    logger.warning(f"Keep-alive failed with status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Keep-alive request failed: {e}")
            except Exception as e:
                logger.error(f"Keep-alive unexpected error: {e}")
            
            # 等待下一次請求，但檢查停止事件
            if not keep_alive_stop_event.wait(KEEP_ALIVE_INTERVAL):
                continue
            else:
                break
                
    finally:
        session.close()
        logger.info("Keep-alive thread stopped")

# **啟動 Keep Alive 背景執行緒**
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

# **優雅關閉處理**
import atexit

def cleanup():
    """應用程式關閉時的清理函數"""
    logger.info("Shutting down application...")
    keep_alive_stop_event.set()
    
    # 等待 keep_alive 線程結束
    if keep_alive_thread.is_alive():
        keep_alive_thread.join(timeout=5)
    
    # 關閉資料庫連接池
    try:
        engine.dispose()
        logger.info("Database connections disposed")
    except Exception as e:
        logger.error(f"Error disposing database connections: {e}")

atexit.register(cleanup)


connection_monitor.start_monitoring()

# **啟動指令**
# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs  --> Swagger API 文件，可測試 API 與查看規格，記得要先啟動本機伺服器再輸入此網址
