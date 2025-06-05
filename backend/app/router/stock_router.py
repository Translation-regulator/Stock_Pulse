from fastapi import APIRouter
from app_utils.db import get_connection

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

@router.get("/all")
def get_all_stocks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT stock_id, stock_name FROM stock_info ORDER BY stock_id")
    data = cursor.fetchall()
    conn.close()
    return data
