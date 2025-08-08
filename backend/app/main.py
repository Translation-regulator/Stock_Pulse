from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  
from router import (
    auth, stock_router, stock_ohlc, twii_ohlc, stock_portfolio,
    comments, chatroom, chatroom_api, stock_ws, twii_ws
)

app = FastAPI(title="StockPulse API")

# CORS 設定：允許前端站點跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stock-pulse.site",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API 路由區塊（有 prefix & tag）
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(stock_router.router, prefix="/api/stocks", tags=["industry"])
app.include_router(stock_ohlc.router, prefix="/api/stocks", tags=["stocks_ohlc"])
app.include_router(twii_ohlc.router, prefix="/api/twii", tags=["twii_ohlc"])
app.include_router(stock_portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(chatroom_api.router, prefix="/api/chat", tags=["chatroom"])

# WebSocket
app.include_router(chatroom.router, tags=["chatroom_ws"])
app.include_router(twii_ws.router, prefix="/ws", tags=["twii_ws"])
app.include_router(stock_ws.router, prefix="/ws", tags=["stock_ws"])

@app.get("/")
def root():
    return JSONResponse(content={"status": "ok"})

# 執行主程式
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
