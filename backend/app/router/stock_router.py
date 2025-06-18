from fastapi import APIRouter, Query, HTTPException
from app_utils.db import get_cursor

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

@router.get("/all")
def get_all_stocks():
    with get_cursor() as cursor:
        cursor.execute("SELECT stock_id, stock_name FROM stock_info ORDER BY stock_id")
        data = cursor.fetchall()
    return data

@router.get("/industry")
def get_stocks_by_industry(category: str = Query(..., alias="category")):
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT stock_id, stock_name, industry FROM stock_info WHERE industry = %s ORDER BY stock_id",
            (category,)
        )
        data = cursor.fetchall()
    if not data:
        raise HTTPException(status_code=404, detail="查無相關股票")
    return data

@router.get("/industries")
def get_all_industries():
    with get_cursor() as cursor:
        cursor.execute("SELECT DISTINCT industry FROM stock_info ORDER BY industry")
        data = cursor.fetchall()
    return [row['industry'] for row in data]
