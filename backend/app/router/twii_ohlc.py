from fastapi import APIRouter
from datetime import datetime, time as dt_time
from app_utils.db import get_cursor
import pandas as pd

router = APIRouter()

# 通用函式：處理 OHLC + MA + 漲跌點幅
def fetch_ohlc(table: str):
    with get_cursor() as cursor:
        cursor.execute(f"""
            SELECT date, open, high, low, close, volume, amount
            FROM {table}
            ORDER BY date ASC
        """)
        rows = cursor.fetchall()

    df = pd.DataFrame(rows)

    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma60"] = df["close"].rolling(window=60).mean()
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
            "turnover": int(row["amount"]) if row.get("amount") is not None else None,
            "change_point": row["change_point"] if pd.notna(row["change_point"]) else None,
            "change_percent": row["change_percent"] if pd.notna(row["change_percent"]) else None,
        })
    return result


# 大盤日線
@router.get("/daily")
async def get_twii_daily():
    return fetch_ohlc("twii_daily")

# 大盤週線
@router.get("/weekly")
async def get_twii_weekly():
    return fetch_ohlc("twii_weekly")

# 大盤月線
@router.get("/monthly")
async def get_twii_monthly():
    return fetch_ohlc("twii_monthly")
