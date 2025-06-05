from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import twii_ws, twii_ohlc, stock_ohlc, auth, stock_ws, stock_portfolio, chatroom, comments, stock_router

app = FastAPI()
# "http://stockpulse-frontend-vue.s3-website-ap-northeast-1.amazonaws.com"
# CORS 設定（給前端 Vue S3 使用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stock-pulse.site",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}

# 路由掛載
app.include_router(twii_ohlc.router, prefix="/api/twii", tags=["twii_ohlc"])
app.include_router(twii_ws.router, prefix="/ws", tags=["websocket"])
app.include_router(stock_ohlc.router, prefix="/api")
app.include_router(auth.router)
app.include_router(stock_ws.router, prefix="/ws", tags=["stock_ws"])
app.include_router(stock_portfolio.router)
app.include_router(chatroom.router)
app.include_router(comments.router, prefix="/api", tags=["comments"])
app.include_router(stock_router.router)
# 加上主程式跑法
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
