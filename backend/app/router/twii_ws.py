from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.fugle_ws_client import start_fugle_stream
import asyncio

router = APIRouter()

@router.websocket("/ws/twii")
async def twii_ws(websocket: WebSocket):
    await websocket.accept()

    queue = asyncio.Queue()

    def send_to_frontend(message):
        print("📤 已送出即時資料給前端:", message)
        asyncio.run(queue.put(message))  # 非同步安全

    start_fugle_stream(send_to_frontend)  # 啟動 Fugle 串流（背景 thread）

    try:
        while True:
            msg = await queue.get()
            await websocket.send_text(msg)
    except WebSocketDisconnect:
        print("⚠️ WebSocket 已中斷，停止推播")
