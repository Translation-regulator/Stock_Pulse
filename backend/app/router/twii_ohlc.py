from fastapi import APIRouter
from datetime import datetime, time as dt_time
from utils.db import get_connection

router = APIRouter()

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

    result = []
    for row in rows:
        dt = datetime.combine(row['date'], dt_time.min)
        result.append({
            "time": int(dt.timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        })
    return result

@router.get("/api/twii/weekly")
async def get_twii_weekly():
    return fetch_ohlc("twii_weekly")

@router.get("/api/twii/monthly")
async def get_twii_monthly():
    return fetch_ohlc("twii_monthly")
