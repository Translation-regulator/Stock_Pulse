from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from utils.db import get_connection

router = APIRouter()

class PortfolioCreate(BaseModel):
    user_id: int
    stock_id: str
    stock_name: str
    shares: int
    buy_price: float
    buy_date: Optional[date] = None
    note: Optional[str] = None

class PortfolioOut(PortfolioCreate):
    id: int
    current_price: Optional[float] = None
    profit: Optional[float] = None

@router.post("/api/portfolio", response_model=PortfolioOut)
def create_portfolio(p: PortfolioCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_portfolio (user_id, stock_id, stock_name, shares, buy_price, buy_date, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (p.user_id, p.stock_id, p.stock_name, p.shares, p.buy_price, p.buy_date, p.note))

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
        current_price=current_price,
        profit=profit,
        **p.dict()
    )

@router.get("/api/portfolio/{user_id}", response_model=List[PortfolioOut])
def get_user_portfolio(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user_portfolio WHERE user_id = %s", (user_id,))
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
