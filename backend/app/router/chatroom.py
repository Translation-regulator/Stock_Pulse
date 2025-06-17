from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app_utils.jwt import decode_token
from app_utils.db import get_cursor
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json

router = APIRouter()
room_connections = defaultdict(set)

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, token: str, room: str = "default"):
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
    await websocket.accept()
    room_connections[room_id].add(websocket)
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
                continue

            try:
                with get_cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO chatroom_realtime_message (room_id, user_id, content)
                        VALUES (%s, %s, %s)
                    """, (room_id, user_id, content))
            except Exception as e:
                print(f"[DB] 儲存訊息失敗：{e}")
                continue

            message_data = {
                "username": username,
                "content": content,
                "time": datetime.now(ZoneInfo("Asia/Taipei")).isoformat()
            }

            for conn in list(room_connections[room_id]):
                try:
                    await conn.send_text(json.dumps(message_data))
                except Exception:
                    room_connections[room_id].discard(conn)

    except WebSocketDisconnect:
        room_connections[room_id].discard(websocket)
        print(f"[WS] 使用者 {username} 離開房間 {room_id}，剩餘人數：{len(room_connections[room_id])}")
        
