import pandas as pd
from datetime import timedelta
from tqdm import tqdm # type:ignore
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
    # ✅ 確保 start_date 是 Python datetime.date
    start_date = pd.to_datetime(start_date).to_pydatetime().date()
    df = pd.read_sql(query, conn, params=(stock_id, start_date))
    conn.close()
    if df.empty:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

# 寫入週／月線資料（UPSERT）
def insert_ohlc(conn, table_name, stock_id, df):
    df = df.dropna().reset_index()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {table_name}
            (stock_id, date, open, high, low, close, volume, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                volume = VALUES(volume),
                amount = VALUES(amount)
        """, (
            stock_id,
            row["date"].date(),
            row["open"], row["high"], row["low"], row["close"],
            row["volume"], row["amount"]
        ))
    conn.commit()

# 處理單一股票
def process_stock(stock_id, conn):
    last_weekly = get_last_converted_date(conn, "stock_weekly_price", stock_id)
    last_monthly = get_last_converted_date(conn, "stock_monthly_price", stock_id)

    start_date = min(
        d - timedelta(days=7) if d else pd.Timestamp("2000-01-01")
        for d in [last_weekly, last_monthly]
    )

    df = get_daily_data(stock_id, start_date)
    if df is None or df.empty:
        return

    # === 週線處理 ===
    df['week_id'] = df.index.to_series().dt.to_period("W").apply(lambda r: r.start_time)
    weekly_rows = []
    for _, group in df.groupby("week_id"):
        last_date = group.index.max()
        weekly_rows.append({
            "date": last_date,
            "open": group.iloc[0]["open"],
            "high": group["high"].max(),
            "low": group["low"].min(),
            "close": group.iloc[-1]["close"],
            "volume": group["volume"].sum(),
            "amount": group["amount"].sum()
        })
    df_weekly = pd.DataFrame(weekly_rows)

    # === 月線處理 ===
    df['month_id'] = df.index.to_series().dt.to_period("M")
    monthly_rows = []
    for _, group in df.groupby("month_id"):
        last_date = group.index.max()
        monthly_rows.append({
            "date": last_date,
            "open": group.iloc[0]["open"],
            "high": group["high"].max(),
            "low": group["low"].min(),
            "close": group.iloc[-1]["close"],
            "volume": group["volume"].sum(),
            "amount": group["amount"].sum()
        })
    df_monthly = pd.DataFrame(monthly_rows)

    insert_ohlc(conn, "stock_weekly_price", stock_id, df_weekly)
    insert_ohlc(conn, "stock_monthly_price", stock_id, df_monthly)

# 主程式
def main():
    stock_ids = get_all_stock_ids()
    conn = get_connection()

    for stock_id in tqdm(stock_ids, desc="📈 計算個股週/月線"):
        process_stock(stock_id, conn)

    conn.close()
    print("✅ 所有個股資料已轉換為週線與月線")

if __name__ == "__main__":
    main()