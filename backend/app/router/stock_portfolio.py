from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app_utils.db import get_cursor
from app_utils.jwt import get_current_user

router = APIRouter()

# shares 與 buy_price 加預設值
class PortfolioCreate(BaseModel):
    stock_id: str
    stock_name: str
    shares: int = 0
    buy_price: float = 0.0
    buy_date: Optional[date] = None
    note: Optional[str] = None

class PortfolioOut(PortfolioCreate):
    id: int
    user_id: int
    current_price: Optional[float] = None
    profit: Optional[float] = None


@router.post("/", response_model=PortfolioOut)
def create_portfolio(p: PortfolioCreate, user=Depends(get_current_user)):
    try:
        print("📥 請求內容:", p)
        print("👤 使用者資訊:", user)

        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_portfolio (user_id, stock_id, stock_name, shares, buy_price, buy_date, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user['id'],
                p.stock_id,
                p.stock_name,
                p.shares,
                p.buy_price,
                p.buy_date or None,
                p.note,
            ))
            p_id = cursor.lastrowid

            cursor.execute("""
                SELECT close FROM stock_daily_price
                WHERE stock_id = %s ORDER BY date DESC LIMIT 1
            """, (p.stock_id,))
            row = cursor.fetchone()

        current_price = float(row["close"]) if row and row.get("close") is not None else None
        profit = round((current_price - p.buy_price) * p.shares, 2) if current_price is not None else None

        return PortfolioOut(
            id=p_id,
            user_id=user['id'],
            current_price=current_price,
            profit=profit,
            **p.dict()
        )

    except Exception as e:
        import traceback
        print("🔥 建立持股失敗:", e)
        traceback.print_exc()  # ✅ 印出完整錯誤 traceback
        raise HTTPException(status_code=500, detail="新增持股失敗")



# 查詢所有持股
@router.get("/me", response_model=List[PortfolioOut])
def get_user_portfolio(user=Depends(get_current_user)):
    result = []
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM user_portfolio WHERE user_id = %s", (user['id'],))
        rows = cursor.fetchall()

        for row in rows:
            cursor.execute("""
                SELECT close FROM stock_daily_price
                WHERE stock_id = %s ORDER BY date DESC LIMIT 1
            """, (row['stock_id'],))
            r = cursor.fetchone()
            current_price = float(row["close"]) if row and row.get("close") is not None else None
            profit = None

            buy_price = float(row['buy_price']) if row['buy_price'] is not None else 0.0
            shares = int(row['shares']) if row['shares'] is not None else 0
            if current_price is not None:
                profit = round((current_price - buy_price) * shares, 2)

            result.append(PortfolioOut(
                id=row['id'],
                user_id=row['user_id'],
                stock_id=row['stock_id'],
                stock_name=row['stock_name'],
                shares=shares,
                buy_price=buy_price,
                buy_date=row['buy_date'],
                note=row['note'],
                current_price=current_price,
                profit=profit
            ))

    return result


# 編輯持股
@router.put("/{id}", response_model=PortfolioOut)
def update_portfolio(id: int, p: PortfolioCreate, user=Depends(get_current_user)):
    with get_cursor() as cursor:
        cursor.execute("""
            UPDATE user_portfolio
            SET stock_id=%s, stock_name=%s, shares=%s, buy_price=%s, buy_date=%s, note=%s
            WHERE id = %s AND user_id = %s
        """, (p.stock_id, p.stock_name, p.shares, p.buy_price, p.buy_date, p.note, id, user['id']))

        cursor.execute("""
            SELECT close FROM stock_daily_price
            WHERE stock_id = %s ORDER BY date DESC LIMIT 1
        """, (p.stock_id,))
        row = cursor.fetchone()

    current_price = float(row["close"]) if row and row.get("close") is not None else None
    profit = round((current_price - p.buy_price) * p.shares, 2) if current_price else None

    return PortfolioOut(id=id, user_id=user['id'], current_price=current_price, profit=profit, **p.dict())


# 刪除持股
@router.delete("/{id}")
def delete_portfolio(id: int, user=Depends(get_current_user)):
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM user_portfolio WHERE id = %s AND user_id = %s", (id, user['id']))
    return {"success": True}
