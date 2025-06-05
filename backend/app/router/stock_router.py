from fastapi import APIRouter
from app_utils.db import get_cursor

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

@router.get("/all")
def get_all_stocks():
    with get_cursor() as cursor:
        cursor.execute("SELECT stock_id, stock_name FROM stock_info ORDER BY stock_id")
        data = cursor.fetchall()
    return data
