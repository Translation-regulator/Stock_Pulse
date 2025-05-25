from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import twii_ws
from app.router import twii_ohlc
from app.router import stock_ohlc 
from app.router import auth
app = FastAPI()

# CORS（允許前端請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 可指定 Vue 網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 測試路由
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}

# REST API：統一掛在 /api/twii 下（大盤用）
app.include_router(twii_ohlc.router, prefix="/api/twii", tags=["twii_ohlc"])

# WebSocket 路由：掛在 /ws 下（即時資料）
app.include_router(twii_ws.router, prefix="/ws", tags=["websocket"])

# 掛載個股路由
app.include_router(stock_ohlc.router, prefix="/api")

app.include_router(auth.router)