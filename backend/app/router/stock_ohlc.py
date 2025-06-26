from fastapi import APIRouter, HTTPException
from datetime import datetime, time as dt_time
from app_utils.db import get_cursor
import pandas as pd

router = APIRouter()

# 查詢個股基本資料（前端用於自動完成）
@router.get("/info/{query}")
async def get_stock_info(query: str):
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT stock_id, stock_name
            FROM stock_info
            WHERE stock_id = %s OR stock_name LIKE %s
            LIMIT 1
        """, (query, f"%{query}%"))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="查無此股票")
    return row


# 搜尋個股列表
@router.get("/search")
async def search_stocks(q: str):
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT stock_id, stock_name
            FROM stock_info
            WHERE stock_id LIKE %s OR stock_name LIKE %s
            ORDER BY stock_id
            LIMIT 10
        """, (f"{q}%", f"{q}%"))  # 改成從頭開始比對
        rows = cursor.fetchall()

    return rows


# 通用：取得個股 ohlc + 技術線
def fetch_stock_ohlc(table: str, stock_id: str):
    with get_cursor() as cursor:
        cursor.execute(f"""
            SELECT date, open, high, low, close, volume, amount
            FROM {table}
            WHERE stock_id = %s
            ORDER BY date ASC
        """, (stock_id,))
        rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="查無資料")

    df = pd.DataFrame(rows)

    # Decimal 轉 float
    for col in ["open", "high", "low", "close", "volume", "amount"]:
        if col in df.columns:
            df[col] = df[col].astype(float)

    df = df.dropna(subset=["open", "high", "low", "close"])

    # 技術指標
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    df["prev_close"] = df["close"].shift(1)
    df["change_point"] = (df["close"] - df["prev_close"]).round(2)
    df["change_percent"] = ((df["change_point"] / df["prev_close"]) * 100).round(2)

    result = []
    for row in df.to_dict(orient="records"):
        dt = datetime.combine(row['date'], dt_time.min)
        result.append({
            "time": int(dt.timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"]) if row.get("volume") is not None else 0,
            "ma5": round(row["ma5"], 2) if pd.notna(row["ma5"]) else None,
            "ma20": round(row["ma20"], 2) if pd.notna(row["ma20"]) else None,
            "ma60": round(row["ma60"], 2) if pd.notna(row["ma60"]) else None,
            "turnover": int(row["amount"]) if pd.notna(row["amount"]) else None,
            "change_point": row["change_point"] if pd.notna(row["change_point"]) else None,
            "change_percent": row["change_percent"] if pd.notna(row["change_percent"]) else None,
        })

    # 過濾異常資料
    result = [r for r in result if all(
        isinstance(r.get(k), (int, float)) for k in ['open', 'high', 'low', 'close']
    )]

    return result


# 個股日週月線路由
@router.get("/{stock_id}/daily")
async def get_stock_daily(stock_id: str):
    return fetch_stock_ohlc("stock_daily_price", stock_id)

@router.get("/{stock_id}/weekly")
async def get_stock_weekly(stock_id: str):
    return fetch_stock_ohlc("stock_weekly_price", stock_id)

@router.get("/{stock_id}/monthly")
async def get_stock_monthly(stock_id: str):
    return fetch_stock_ohlc("stock_monthly_price", stock_id)
