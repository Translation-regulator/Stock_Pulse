import pandas as pd
from utils.db import get_connection

def generate_twii_ohlc():
    conn = get_connection()
    df = pd.read_sql("SELECT date, open, high, low, close, volume, trade_count FROM twii_index", conn)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # === 週線資料 ===
    df_weekly = df.resample("W-MON").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "trade_count": "sum"
    }).dropna().reset_index()

    # === 月線資料 ===
    df_monthly = df.resample("M").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "trade_count": "sum"
    }).dropna().reset_index()

    cursor = conn.cursor()

    # 清空原有資料
    cursor.execute("TRUNCATE TABLE twii_weekly")
    cursor.execute("TRUNCATE TABLE twii_monthly")

    # 寫入週線
    for _, row in df_weekly.iterrows():
        cursor.execute("""
            INSERT INTO twii_weekly (date, open, high, low, close, volume, trade_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['date'].date(),  # ✅ 轉為 datetime.date
            row['open'],
            row['high'],
            row['low'],
            row['close'],
            row['volume'],
            row['trade_count']
        ))

    # 寫入月線
    for _, row in df_monthly.iterrows():
        cursor.execute("""
            INSERT INTO twii_monthly (date, open, high, low, close, volume, trade_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['date'].date(),  # ✅ 同上
            row['open'],
            row['high'],
            row['low'],
            row['close'],
            row['volume'],
            row['trade_count']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ twii_weekly 與 twii_monthly 寫入完成")

if __name__ == "__main__":
    generate_twii_ohlc()
