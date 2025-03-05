# Purpose: FastAPI 應用程式的進入點

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import locations, record
from app.database import Base, engine

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

# **測試 API**
@app.get("/")
def read_root():
    return {"message": "FastAPI 伺服器運行中"}

# **啟動指令**
# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs  --> Swagger API 文件，可測試 API 與查看規格，記得要先啟動本機伺服器再輸入此網址