from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from collections import defaultdict
from utils.jwt import decode_token

router = APIRouter()
room_connections = defaultdict(set)

@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    user = payload.get("sub")
    username = payload.get("name")
    if not user:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    room_connections[room_id].add(websocket) 

    print(f"[WS] 使用者 {username} 加入聊天室 {room_id}")

    try:
        while True:
            msg = await websocket.receive_text()
            print(f"[WS] 收到訊息：{msg}")
            full_msg = f"{username}：{msg}"

            # 廣播給房間內所有人
            for conn in room_connections[room_id]:
                await conn.send_text(full_msg)

    except WebSocketDisconnect:
        if websocket in room_connections[room_id]:
            room_connections[room_id].remove(websocket)
        print(f"[WS] 使用者 {username} 離開聊天室 {room_id}")
