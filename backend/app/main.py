from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import twii  # 引入大盤的路由
from app.router import twii_ws
from app.router import twii_ohlc

app = FastAPI()

# CORS（允許前端請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可指定 Vue 網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(twii.router, prefix="/api/twii", tags=["twii"])
app.include_router(twii_ws.router)
app.include_router(twii_ohlc.router)