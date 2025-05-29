from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app_utils.db import get_connection
from app_utils.jwt import get_current_user

router = APIRouter()

class PortfolioCreate(BaseModel):
    stock_id: str
    stock_name: str
    shares: int
    buy_price: float
    buy_date: Optional[date] = None
    note: Optional[str] = None

class PortfolioOut(PortfolioCreate):
    id: int
    user_id: int
    current_price: Optional[float] = None
    profit: Optional[float] = None

@router.post("/api/portfolio", response_model=PortfolioOut)
def create_portfolio(p: PortfolioCreate, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_portfolio (user_id, stock_id, stock_name, shares, buy_price, buy_date, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user['id'], p.stock_id, p.stock_name, p.shares, p.buy_price, p.buy_date, p.note))

    conn.commit()
    p_id = cursor.lastrowid

    cursor.execute("SELECT close FROM stock_daily_price WHERE stock_id = %s ORDER BY date DESC LIMIT 1", (p.stock_id,))
    row = cursor.fetchone()
    current_price = float(row[0]) if row and row[0] else None
    profit = None
    if current_price is not None:
        profit = round((current_price - p.buy_price) * p.shares, 2)

    conn.close()

    return PortfolioOut(
        id=p_id,
        user_id=user['id'],
        current_price=current_price,
        profit=profit,
        **p.dict()
    )

@router.get("/api/portfolio/me", response_model=List[PortfolioOut])
def get_user_portfolio(user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user_portfolio WHERE user_id = %s", (user['id'],))
    rows = cursor.fetchall()

    result = []
    for row in rows:
        cursor.execute("SELECT close FROM stock_daily_price WHERE stock_id = %s ORDER BY date DESC LIMIT 1", (row['stock_id'],))
        r = cursor.fetchone()
        current_price = float(r["close"]) if r and r.get("close") is not None else None
        profit = None
        if current_price is not None:
            profit = round((current_price - float(row['buy_price'])) * int(row['shares']), 2)

        result.append(PortfolioOut(
            id=row['id'],
            user_id=row['user_id'],
            stock_id=row['stock_id'],
            stock_name=row['stock_name'],
            shares=row['shares'],
            buy_price=row['buy_price'],
            buy_date=row['buy_date'],
            note=row['note'],
            current_price=current_price,
            profit=profit
        ))

    conn.close()
    return result

@router.put("/api/portfolio/{id}", response_model=PortfolioOut)
def update_portfolio(id: int, p: PortfolioCreate, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE user_portfolio
        SET stock_id=%s, stock_name=%s, shares=%s, buy_price=%s, buy_date=%s, note=%s
        WHERE id = %s AND user_id = %s
    """, (p.stock_id, p.stock_name, p.shares, p.buy_price, p.buy_date, p.note, id, user['id']))

    conn.commit()

    cursor.execute("SELECT close FROM stock_daily_price WHERE stock_id = %s ORDER BY date DESC LIMIT 1", (p.stock_id,))
    row = cursor.fetchone()
    current_price = float(row[0]) if row and row[0] else None
    profit = round((current_price - p.buy_price) * p.shares, 2) if current_price else None
    conn.close()

    return PortfolioOut(id=id, user_id=user['id'], current_price=current_price, profit=profit, **p.dict())

@router.delete("/api/portfolio/{id}")
def delete_portfolio(id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_portfolio WHERE id = %s AND user_id = %s", (id, user['id']))
    conn.commit()
    conn.close()
    return {"success": True}
