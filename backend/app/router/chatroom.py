from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from collections import defaultdict
from datetime import datetime
import json
from app_utils.jwt import decode_token

router = APIRouter()
room_connections = defaultdict(set)

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, token: str, room: str = "default"):
    # 解碼 JWT
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    user = payload.get("sub")
    username = payload.get("name")
    if not user:
        await websocket.close(code=1008)
        return

    room_id = room  # ✅ 取得聊天室房號
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

            for conn in room_connections[room_id]:
                try:
                    await conn.send_text(json.dumps(message_data))
                except Exception as e:
                    print(f"[WS] 廣播失敗：{e}")

    except WebSocketDisconnect:
        room_connections[room_id].discard(websocket)
        print(f"[WS] 使用者 {username} 離開房間 {room_id}，剩餘人數：{len(room_connections[room_id])}")
