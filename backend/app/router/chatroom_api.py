from fastapi import APIRouter
from app_utils.db import get_cursor
from datetime import timezone
from zoneinfo import ZoneInfo

router = APIRouter()

@router.get("/history/{room_id}")
def get_chat_history(room_id: str, limit: int = 50):
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT m.content, m.created_at, u.name AS username
            FROM chatroom_realtime_message AS m
            JOIN users AS u ON m.user_id = u.id
            WHERE m.room_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (room_id, limit))
        rows = cursor.fetchall()
        return list(reversed([
            {
                "username": row["username"],
                "content": row["content"],
                "time": row["created_at"].astimezone(ZoneInfo("Asia/Taipei")).isoformat()
            } for row in rows
        ]))
