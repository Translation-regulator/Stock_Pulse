from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app_utils.db import get_connection
from app_utils.jwt import decode_token

router = APIRouter()

class CommentCreate(BaseModel):
    content: str
    guest_name: Optional[str] = None

@router.post("/comments/{room_id}")
async def post_comment(room_id: str, body: CommentCreate, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = decode_token(token) if token else None

    print("Token:", token[:30], "...")  # 看 token 是否成功送進來
    print("Decoded user:", user)       # 看 sub 是不是 user_id

    if not body.content.strip():
        raise HTTPException(status_code=400, detail="留言內容不得為空")

    user_id = None
    guest_name = None

    if user:
        try:
            user_id = int(user.get("sub"))
        except (TypeError, ValueError):
            print("⚠️ sub 不是 int，值為：", user.get("sub"))
            raise HTTPException(status_code=400, detail="使用者 token 無效")
    else:
        guest_name = body.guest_name or f"訪客{str(datetime.now().timestamp())[-4:]}"

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()

    cursor.execute("""
        INSERT INTO chat_message (room_id, user_id, guest_name, content, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (room_id, user_id, guest_name, body.content, now))
    conn.commit()

    return {"message": "留言成功", "created_at": now.isoformat()}


@router.get("/comments/{room_id}")
async def get_comments(room_id: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT m.id, m.room_id, m.content, m.created_at,
        u.name AS user_name, m.guest_name
        FROM chat_message m
        LEFT JOIN users u ON m.user_id = u.id
        WHERE room_id = %s
        ORDER BY m.created_at ASC
        LIMIT 100
    """, (room_id,))
    return cursor.fetchall()
