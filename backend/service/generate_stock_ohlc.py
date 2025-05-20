import pandas as pd
from tqdm import tqdm # type: ignore
from utils.db import get_connection
import warnings

# 忽略 Pandas 使用非 SQLAlchemy 連線的警告
warnings.filterwarnings("ignore", category=UserWarning)

# 忽略 "M" 被棄用的未來警告
warnings.filterwarnings("ignore", category=FutureWarning)

def get_all_stock_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT stock_id FROM stock_daily_price")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_daily_data(stock_id):
    conn = get_connection()
    query = """
        SELECT date, open, high, low, close, volume, amount
        FROM stock_daily_price
        WHERE stock_id = %s
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn, params=(stock_id,))
    conn.close()
    if df.empty:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df

def insert_ohlc(conn, table_name, stock_id, df, date_col):
    df = df.dropna().reset_index()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT IGNORE INTO {table_name}
            (stock_id, {date_col}, open, high, low, close, volume, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            stock_id,
            row["date"].date(),  # 週五或月底
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["volume"],
            row["amount"]
        ))
    conn.commit()

def process_stock(stock_id, conn):
    df = get_daily_data(stock_id)
    if df is None or df.empty:
        print(f"⚠️ 無日線資料：{stock_id}")
        return

    # 使用結束日為代表日期（週五、月底）
    df_weekly = df.resample("W-FRI").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })

    df_monthly = df.resample("M").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })

    insert_ohlc(conn, "stock_weekly_price", stock_id, df_weekly, "date")
    insert_ohlc(conn, "stock_monthly_price", stock_id, df_monthly, "date")

def main():
    stock_ids = get_all_stock_ids()
    conn = get_connection()

    # ✅ 清空舊資料
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE stock_weekly_price")
    cursor.execute("TRUNCATE TABLE stock_monthly_price")
    conn.commit()

    for stock_id in tqdm(stock_ids, desc="📊 個股週/月線轉換中"):
        process_stock(stock_id, conn)

    conn.close()
    print("✅ 所有個股週線與月線轉換完成")

if __name__ == "__main__":
    main()
