import pandas as pd
from datetime import timedelta
from tqdm import tqdm  # type: ignore
from utils.db import get_connection

# 取得所有股票 ID
def get_all_stock_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT stock_id FROM stock_daily_price")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# 取最後一筆已轉換的日期
def get_last_converted_date(conn, table_name, stock_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX(date) FROM {table_name} WHERE stock_id = %s", (stock_id,))
    row = cursor.fetchone()
    return row[0]  # may be None

# 取得該股的日線資料
def get_daily_data(stock_id, start_date):
    conn = get_connection()
    query = """
        SELECT date, open, high, low, close, volume, amount
        FROM stock_daily_price
        WHERE stock_id = %s AND date >= %s
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn, params=(stock_id, start_date))
    conn.close()
    if df.empty:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# 寫入 weekly_price / monthly_price
def insert_ohlc(conn, table_name, stock_id, df):
    df = df.dropna().reset_index()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT IGNORE INTO {table_name}
            (stock_id, date, open, high, low, close, volume, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            stock_id,
            row["date"].date(),
            row["open"], row["high"], row["low"], row["close"],
            row["volume"], row["amount"]
        ))
    conn.commit()

# 處理單一股票
def process_stock(stock_id, conn):
    # 最後一筆進行轉換的日期
    last_weekly = get_last_converted_date(conn, "weekly_price", stock_id)
    last_monthly = get_last_converted_date(conn, "monthly_price", stock_id)

    # 設定最早日期，最少有一週和一月資料
    start_date = min(
        d - timedelta(days=7) if d else pd.Timestamp("2000-01-01")
        for d in [last_weekly, last_monthly]
    )

    df = get_daily_data(stock_id, start_date)
    if df is None or df.empty:
        return

    df_weekly = df.resample("W-FRI").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })

    df_monthly = df.resample("ME").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })

    insert_ohlc(conn, "weekly_price", stock_id, df_weekly)
    insert_ohlc(conn, "monthly_price", stock_id, df_monthly)

# 主程式
def main():
    stock_ids = get_all_stock_ids()
    conn = get_connection()

    for stock_id in tqdm(stock_ids, desc="📈 計算最新個股資料"):
        process_stock(stock_id, conn)

    conn.close()
    print("✅ 新日線資料已轉換為週/月線")

if __name__ == "__main__":
    main()
