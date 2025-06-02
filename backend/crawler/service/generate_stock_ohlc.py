import sys
import pandas as pd
from datetime import datetime
from crawler_utils.db import get_connection
from tqdm import tqdm  # type: ignore

# CLI 分段參數（如 1 5 表示第1組，共5組）
part_index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
total_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 1

# 取得所有股票 ID（從 daily 表取得）
def get_all_stock_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT stock_id FROM stock_daily_price ORDER BY stock_id")
    stock_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return stock_ids

# 單檔處理（只用傳入的 conn/cursor）
def process_stock(stock_id: str, conn, cursor):
    df = pd.read_sql(f"""
        SELECT date, open, high, low, close, volume, amount, transaction_count
        FROM stock_daily_price
        WHERE stock_id = '{stock_id}'
        ORDER BY date ASC
    """, conn, parse_dates=['date'])

    if df.empty:
        return

    # 僅保留本月資料
    first_day_of_month = datetime.today().replace(day=1)
    df = df[df['date'] >= first_day_of_month]
    if df.empty:
        return

    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    # ===== 週線處理 =====
    df['week_id'] = df.index.to_series().dt.to_period("W").apply(lambda r: r.start_time)
    for week_id, group in df.groupby("week_id"):
        group = group.dropna(subset=["open", "high", "low", "close", "volume", "amount", "transaction_count"])
        if group.empty:
            print(f"[跳過週線] {stock_id} @ {week_id} → 無有效資料")
            continue

        week_start = group.index.min().date()
        week_end = group.index.max().date()
        last_date = group.index.max().date()

        cursor.execute("""
            DELETE FROM stock_weekly_price
            WHERE stock_id = %s AND date BETWEEN %s AND %s
        """, (stock_id, week_start, week_end))

        cursor.execute("""
            REPLACE INTO stock_weekly_price
            (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            stock_id,
            last_date,
            float(group.iloc[0]["open"]),
            float(group["high"].max()),
            float(group["low"].min()),
            float(group.iloc[-1]["close"]),
            int(group["volume"].sum()),
            int(group["amount"].sum()),
            float(group.iloc[-1]["close"]) - float(group.iloc[0]["open"]),
            int(group["transaction_count"].sum())
        ))

    # ===== 月線處理 =====
    df['month_id'] = df.index.to_series().dt.to_period("M").apply(lambda r: r.start_time)
    for month_id, group in df.groupby("month_id"):
        group = group.dropna(subset=["open", "high", "low", "close", "volume", "amount", "transaction_count"])
        if group.empty:
            print(f"[跳過月線] {stock_id} @ {month_id} → 無有效資料")
            continue

        month_start = group.index.min().date()
        month_end = group.index.max().date()
        last_date = group.index.max().date()

        cursor.execute("""
            DELETE FROM stock_monthly_price
            WHERE stock_id = %s AND date BETWEEN %s AND %s
        """, (stock_id, month_start, month_end))

        cursor.execute("""
            REPLACE INTO stock_monthly_price
            (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            stock_id,
            last_date,
            float(group.iloc[0]["open"]),
            float(group["high"].max()),
            float(group["low"].min()),
            float(group.iloc[-1]["close"]),
            int(group["volume"].sum()),
            int(group["amount"].sum()),
            float(group.iloc[-1]["close"]) - float(group.iloc[0]["open"]),
            int(group["transaction_count"].sum())
        ))

# 主流程：只開一條連線 + 一個 cursor
def generate_stock_ohlc():
    conn = get_connection()
    cursor = conn.cursor()

    all_ids = get_all_stock_ids(conn)
    total = len(all_ids)
    chunk_size = total // total_parts
    start = (part_index - 1) * chunk_size
    end = total if part_index == total_parts else start + chunk_size
    ids_to_process = all_ids[start:end]

    print(f"🚀 開始處理第 {part_index}/{total_parts} 組，共 {len(ids_to_process)} 檔")
    for stock_id in tqdm(ids_to_process, desc=f"第 {part_index} 組"):
        try:
            process_stock(stock_id, conn, cursor)
        except Exception as e:
            print(f"❌ 處理 {stock_id} 時發生錯誤：{e}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    generate_stock_ohlc()
