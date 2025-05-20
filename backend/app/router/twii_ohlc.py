from fastapi import APIRouter
from datetime import datetime, time as dt_time
from utils.db import get_connection
import pandas as pd
router = APIRouter()

# ✅ 通用函式
def fetch_ohlc(table: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT date, open, high, low, close
        FROM {table}
        ORDER BY date ASC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows)
    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma60"] = df["close"].rolling(window=60).mean()

    result = []
    for row in df.to_dict(orient="records"):
        dt = datetime.combine(row['date'], dt_time.min)
        result.append({
            "time": int(dt.timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "ma5": round(row["ma5"], 2) if pd.notna(row["ma5"]) else None,
            "ma20": round(row["ma20"], 2) if pd.notna(row["ma20"]) else None,
            "ma60": round(row["ma60"], 2) if pd.notna(row["ma60"]) else None,
        })
    return result


# ✅ 大盤日線
@router.get("/daily")
async def get_twii_daily():
    return fetch_ohlc("twii_index")

# ✅ 大盤週線
@router.get("/weekly")
async def get_twii_weekly():
    return fetch_ohlc("twii_weekly")

# ✅ 大盤月線
@router.get("/monthly")
async def get_twii_monthly():
    return fetch_ohlc("twii_monthly")
