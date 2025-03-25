# Purpose: FastAPI 應用程式的進入點

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import locations, record, villagers
from app.database import Base, engine
import threading
import time
import requests

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

# # **Keep Alive 機制**
# KEEP_ALIVE_URL = "https://kanahcian-backend.onrender.com/"  # 請換成你的 Render API URL

# def keep_alive():
#     while True:
#         try:
#             response = requests.get(KEEP_ALIVE_URL)
#             print(f"Keep-alive ping sent to {KEEP_ALIVE_URL}, Status Code: {response.status_code}")
#         except Exception as e:
#             print(f"Keep-alive request failed: {e}")
#         time.sleep(60)  # 每 1 分鐘請求一次

# # **啟動 Keep Alive 背景執行緒**
# threading.Thread(target=keep_alive, daemon=True).start()

# **啟動指令**
# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs  --> Swagger API 文件，可測試 API 與查看規格，記得要先啟動本機伺服器再輸入此網址
