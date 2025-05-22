import pandas as pd
from utils.db import get_connection
from tqdm import tqdm  # type: ignore


# ✅ 取得所有股票 ID（從 daily 表取得）
def get_all_stock_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT stock_id FROM stock_daily_price")
    stock_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return stock_ids


# ✅ 單檔處理：轉換為週線與月線
def process_stock(stock_id: str):
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT date, open, high, low, close, volume
        FROM stock_daily_price
        WHERE stock_id = '{stock_id}'
        ORDER BY date ASC
    """, conn, parse_dates=['date'])

    if df.empty:
        return

    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    cursor = conn.cursor()

    # ✅ 週線處理（每日滾動更新）
    df['week_id'] = df.index.to_series().dt.to_period("W").apply(lambda r: r.start_time)
    for week_id, group in df.groupby("week_id"):
        week_start = group.index.min().date()
        week_end = group.index.max().date()
        last_date = group.index.max().date()

        # 🔁 刪除這週的舊資料（避免殘留週一、週二等）
        cursor.execute("""
            DELETE FROM stock_weekly_price
            WHERE stock_id = %s AND date BETWEEN %s AND %s
        """, (stock_id, week_start, week_end))

        # ✏️ 寫入最新週線資料（代表日為最新交易日）
        cursor.execute("""
            REPLACE INTO stock_weekly_price
            (stock_id, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            stock_id,
            last_date,
            float(group.iloc[0]["open"]),
            float(group["high"].max()),
            float(group["low"].min()),
            float(group.iloc[-1]["close"]),
            int(group["volume"].sum()),
        ))

    # ✅ 月線處理（每日滾動更新）
    df['month_id'] = df.index.to_series().dt.to_period("M").apply(lambda r: r.start_time)
    for month_id, group in df.groupby("month_id"):
        month_start = group.index.min().date()
        month_end = group.index.max().date()
        last_date = group.index.max().date()

        cursor.execute("""
            DELETE FROM stock_monthly_price
            WHERE stock_id = %s AND date BETWEEN %s AND %s
        """, (stock_id, month_start, month_end))

        cursor.execute("""
            REPLACE INTO stock_monthly_price
            (stock_id, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            stock_id,
            last_date,
            float(group.iloc[0]["open"]),
            float(group["high"].max()),
            float(group["low"].min()),
            float(group.iloc[-1]["close"]),
            int(group["volume"].sum()),
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {stock_id} 的週線與月線資料更新完畢")


# ✅ 執行所有個股轉換
def generate_stock_ohlc():
    stock_ids = get_all_stock_ids()
    for stock_id in tqdm(stock_ids, desc="⏳ 轉換中"):
        process_stock(stock_id)


if __name__ == "__main__":
    generate_stock_ohlc()
