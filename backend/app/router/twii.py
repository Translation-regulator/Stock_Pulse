from fastapi import APIRouter
from datetime import datetime, time as dt_time
from utils.db import get_connection

router = APIRouter()

@router.get("/daily")
def get_twii_daily_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT date, open, high, low, close
        FROM twii_index
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
