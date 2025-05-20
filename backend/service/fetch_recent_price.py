import time
import random
from datetime import datetime
from utils.db import get_connection
from utils.twse_price_client import get_monthly_daily_price
from tqdm import tqdm  # type: ignore

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

def get_last_date(stock_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MAX(date) FROM stock_daily_price
        WHERE stock_id = %s
    """, (stock_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0]

def insert_latest_data(stock_id, cursor):
    today = datetime.today()
    year = today.year
    month = today.month

    prices = get_monthly_daily_price(stock_id, year, month)
    data_to_insert = []

    for p in prices:
        date = convert_to_ad_date(p["date"])
        if not date:
            continue
        data_to_insert.append((
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

    if data_to_insert:
        for attempt in range(2):
            try:
                cursor.executemany("""
                    INSERT IGNORE INTO stock_daily_price
                    (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, data_to_insert)
                return cursor.rowcount
            except Exception as e:
                if "deadlock" in str(e).lower():
                    print(f"⚠️ Deadlock：{stock_id} -> retrying")
                    time.sleep(random.uniform(1.0, 2.0))
                    continue
                else:
                    print(f"❌ 寫入失敗：{stock_id} -> {e}")
                    return 0

def fetch_recent_prices():
    stock_ids = get_four_digit_stocks()
    print(f"📈 開始補抓最近個股資料，共 {len(stock_ids)} 檔")

    conn = get_connection()
    cursor = conn.cursor()
    total_inserted = 0

    for stock_id in tqdm(stock_ids, desc="🛠️ 補抓中"):
        try:
            inserted = insert_latest_data(stock_id, cursor)
            conn.commit()
            total_inserted += inserted
            time.sleep(random.uniform(0.5, 0.8))
        except Exception as e:
            print(f"❌ 補抓錯誤：{stock_id} -> {e}")
            continue

    conn.close()
    print(f"\n✅ 補抓完成，共新增 {total_inserted} 筆資料")

if __name__ == "__main__":
    fetch_recent_prices()
