import time
import random
from datetime import datetime, timedelta
import calendar
from utils.db import get_connection
from utils.twse_price_client import get_monthly_daily_price
from tqdm import tqdm

def convert_to_ad_date(date_str):
    try:
        y, m, d = date_str.split("-")
        year = int(y) + 1911
        return f"{year}-{m}-{d}"
    except:
        return None

def get_four_digit_stocks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stock_id FROM stock_info
        WHERE CHAR_LENGTH(stock_id) = 4 AND is_active = TRUE
        AND listing_type = '上市'
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_existing_months(stock_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE_FORMAT(date, '%%Y-%%m') FROM daily_price
        WHERE stock_id = %s
    """, (stock_id,))
    rows = cursor.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def insert_monthly_data(stock_id, year, month, cursor):
    prices = get_monthly_daily_price(stock_id, year, month)
    for p in prices:
        date = convert_to_ad_date(p["date"])
        if not date:
            continue
        try:
            cursor.execute("""
                INSERT IGNORE INTO daily_price
                (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                stock_id,
                date,
                p["open"],
                p["high"],
                p["low"],
                p["close"],
                p["volume"],
                p["amount"],
                p["change"],
                p["transaction_count"]
            ))
        except Exception as e:
            print(f"❌ 寫入失敗：{stock_id} {date} -> {e}")

def fetch_daily_prices_last_n_years(n_years=10, partition=1, total_partitions=1):
    stock_ids = sorted(get_four_digit_stocks())
    stock_ids = [s for i, s in enumerate(stock_ids) if i % total_partitions == (partition - 1)]

    end = datetime.today()
    start = end.replace(year=end.year - n_years)

    print(f"📆 抓取範圍：{start.date()} ~ {end.date()}")
    print(f"📈 四碼普通股數量：{len(stock_ids)} 檔 (分組 {partition}/{total_partitions})")

    conn = get_connection()
    cursor = conn.cursor()
    total_inserted = 0

    for stock_id in tqdm(stock_ids, desc="股票進度"):
        existing_months = get_existing_months(stock_id)

        for y in range(start.year, end.year + 1):
            for m in range(1, 13):
                month_start = datetime(y, m, 1)
                if month_start < start or month_start > end:
                    continue

                key = f"{y}-{m:02d}"
                if key in existing_months:
                    continue

                print(f"📦 {stock_id} - {y}/{m:02d}")
                insert_monthly_data(stock_id, y, m, cursor)
                conn.commit()
                total_inserted += cursor.rowcount

                sleep_time = round(random.uniform(0.5, 0.8), 2)
                print(f"⏱️ 等待 {sleep_time} 秒...")
                time.sleep(sleep_time)

    conn.close()
    print(f"\n✅ 抓取完成，新增資料共 {total_inserted} 筆")
