from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.fugle_ws_client import start_fugle_stream, register_client
import asyncio

router = APIRouter()
start_fugle_stream()

@router.websocket("/ws/twii")
async def twii_ws(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue()

    # 前端送資料 callback（會被 Fugle 呼叫）
    def send_to_frontend(message: str):
        asyncio.run(queue.put(message))  # 放入 queue 非同步處理

    register_client(send_to_frontend)  # 註冊此前端連線

    try:
        while True:
            msg = await queue.get()
            await websocket.send_text(msg)
    except WebSocketDisconnect:
        print("⚠️ 前端斷線，停止傳送資料")

