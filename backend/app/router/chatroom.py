from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from collections import defaultdict
from datetime import datetime
from app_utils.jwt import decode_token
from app_utils.db import get_cursor
import json

router = APIRouter()
room_connections = defaultdict(set)

# ✅ WebSocket 連線（即時聊天）
@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, token: str, room: str = "default"):
    # 🔐 驗證 token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    user_id = payload.get("sub")
    username = payload.get("name")
    if not user_id:
        await websocket.close(code=1008)
        return

    room_id = room
    room_connections[room_id].add(websocket)
    await websocket.accept()

    print(f"[WS] 使用者 {username} 加入房間 {room_id}，目前人數：{len(room_connections[room_id])}")
    
    try:
        while True:
            raw_msg = await websocket.receive_text()
            try:
                parsed_msg = json.loads(raw_msg)
                content = parsed_msg.get("content", "").strip()
                if not content:
                    continue
            except json.JSONDecodeError:
                print(f"[WS] JSON decode 錯誤：{raw_msg}")
                continue

            current_time = datetime.now().strftime("%H:%M")
            message_data = {
                "username": username,
                "content": content,
                "time": current_time
            }

            # ✅ 儲存訊息進資料庫
            try:
                with get_cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO chat_messages (room_id, username, content)
                        VALUES (%s, %s, %s)
                    """, (room_id, username, content))
            except Exception as e:
                print(f"[DB] 儲存訊息失敗：{e}")

            # ✅ 廣播訊息給房間所有人
            for conn in list(room_connections[room_id]):
                try:
                    await conn.send_text(json.dumps(message_data))
                except Exception as e:
                    print(f"[WS] 廣播失敗：{e}")

    except WebSocketDisconnect:
        room_connections[room_id].discard(websocket)
        print(f"[WS] 使用者 {username} 離開房間 {room_id}，剩餘人數：{len(room_connections[room_id])}")



