from fastapi import APIRouter, Query, HTTPException
from app_utils.db import get_cursor

router = APIRouter()

@router.get("/all")
def get_all_stocks(q: str = ""):
    with get_cursor() as cursor:
        if q:
            # 有輸入查詢字串 → 比對符合的資料（但仍回傳所有匹配結果）
            cursor.execute("""
                SELECT stock_id, stock_name
                FROM stock_info
                WHERE stock_id LIKE %s OR stock_name LIKE %s
                ORDER BY stock_id
            """, (f"{q}%", f"{q}%"))
        else:
            # 沒有搜尋字串 → 回傳所有股票資料（前端再做隨機抽取）
            cursor.execute("""
                SELECT stock_id, stock_name
                FROM stock_info
                ORDER BY stock_id
            """)
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
