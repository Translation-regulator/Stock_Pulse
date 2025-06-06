import sys
import pandas as pd
from datetime import datetime
from crawler_utils.db import engine
from tqdm import tqdm  # type: ignore
from sqlalchemy import text

# CLI 分段參數（如 1 5 表示第1組，共5組）
part_index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
total_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 1

# 取得所有股票 ID（從 daily 表取得）
def get_all_stock_ids():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT stock_id FROM stock_daily_price ORDER BY stock_id
        """))
        return [row[0] for row in result.fetchall()]

# 處理單檔股票資料
def process_stock(stock_id: str, conn):
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

        conn.execute(text("""
            DELETE FROM stock_weekly_price
            WHERE stock_id = :stock_id AND date BETWEEN :start AND :end
        """), {"stock_id": stock_id, "start": week_start, "end": week_end})

        conn.execute(text("""
            REPLACE INTO stock_weekly_price
            (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
            VALUES (:stock_id, :date, :open, :high, :low, :close, :volume, :amount, :change_price, :transaction_count)
        """), {
            "stock_id": stock_id,
            "date": last_date,
            "open": float(group.iloc[0]["open"]),
            "high": float(group["high"].max()),
            "low": float(group["low"].min()),
            "close": float(group.iloc[-1]["close"]),
            "volume": int(group["volume"].sum()),
            "amount": int(group["amount"].sum()),
            "change_price": float(group.iloc[-1]["close"] - group.iloc[0]["open"]),
            "transaction_count": int(group["transaction_count"].sum())
        })

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

        conn.execute(text("""
            DELETE FROM stock_monthly_price
            WHERE stock_id = :stock_id AND date BETWEEN :start AND :end
        """), {"stock_id": stock_id, "start": month_start, "end": month_end})

        conn.execute(text("""
            REPLACE INTO stock_monthly_price
            (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
            VALUES (:stock_id, :date, :open, :high, :low, :close, :volume, :amount, :change_price, :transaction_count)
        """), {
            "stock_id": stock_id,
            "date": last_date,
            "open": float(group.iloc[0]["open"]),
            "high": float(group["high"].max()),
            "low": float(group["low"].min()),
            "close": float(group.iloc[-1]["close"]),
            "volume": int(group["volume"].sum()),
            "amount": int(group["amount"].sum()),
            "change_price": float(group.iloc[-1]["close"] - group.iloc[0]["open"]),
            "transaction_count": int(group["transaction_count"].sum())
        })

# 主流程：使用 SQLAlchemy engine 處理連線與資料

def generate_stock_ohlc():
    all_ids = get_all_stock_ids()
    total = len(all_ids)
    chunk_size = total // total_parts
    start = (part_index - 1) * chunk_size
    end = total if part_index == total_parts else start + chunk_size
    ids_to_process = all_ids[start:end]

    print(f"🚀 開始處理第 {part_index}/{total_parts} 組，共 {len(ids_to_process)} 檔")
    with engine.begin() as conn:
        for stock_id in tqdm(ids_to_process, desc=f"第 {part_index} 組"):
            try:
                process_stock(stock_id, conn)
            except Exception as e:
                print(f"❌ 處理 {stock_id} 時發生錯誤：{e}")

if __name__ == "__main__":
    generate_stock_ohlc()
