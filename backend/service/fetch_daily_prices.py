import time
import random
from datetime import datetime
from utils.db import get_connection
from utils.twse_price_client import get_monthly_daily_price
from tqdm import tqdm  

# ✅ 民國轉西元
def convert_to_ad_date(date_str):
    try:
        y, m, d = date_str.split("-")
        year = int(y) + 1911
        return f"{year}-{m}-{d}"
    except:
        return None

# ✅ 取得上市四碼普通股
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

# ✅ 查詢該股票已有資料月份（避免重複）
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

# ✅ 抓資料時加入 retry（避免失敗）
def get_monthly_daily_price_with_retry(stock_id, year, month, max_retries=2):
    for attempt in range(max_retries):
        try:
            return get_monthly_daily_price(stock_id, year, month)
        except Exception as e:
            print(f"⚠️  {stock_id} {year}-{month:02d} 第 {attempt+1} 次失敗：{e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(random.uniform(1.0, 2.0))

# ✅ 整月批次寫入，並加入 deadlock retry
def insert_monthly_data(stock_id, year, month, cursor):
    prices = get_monthly_daily_price_with_retry(stock_id, year, month)

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
        for attempt in range(2):  # 最多 retry 1 次
            try:
                cursor.executemany("""
                    INSERT IGNORE INTO daily_price
                    (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, data_to_insert)
                return
            except Exception as e:
                if "Deadlock" in str(e) or "deadlock" in str(e):
                    print(f"⚠️ Deadlock 發生：{stock_id} {year}-{month:02d}，第 {attempt+1} 次重試中...")
                    time.sleep(random.uniform(1.0, 2.0))
                    continue
                else:
                    print(f"❌ 寫入失敗：{stock_id} {year}-{month:02d} -> {e}")
                    return

# ✅ 主流程：抓近 n 年，分組執行
def fetch_daily_prices_last_n_years(n_years=20, partition=1, total_partitions=1):
    stock_ids = sorted(get_four_digit_stocks())
    stock_ids = [s for i, s in enumerate(stock_ids) if i % total_partitions == (partition - 1)]

    end = datetime.today()
    start = end.replace(year=end.year - n_years)

    print(f"📆 抓取範圍：{start.date()} ~ {end.date()}")
    print(f"📈 四碼普通股數量：{len(stock_ids)} 檔 (第 {partition}/{total_partitions} 組)")

    conn = get_connection()
    cursor = conn.cursor()
    total_inserted = 0

    for stock_id in tqdm(stock_ids, desc="📊 股票進度"):
        existing_months = get_existing_months(stock_id)

        for y in range(start.year, end.year + 1):
            for m in range(1, 13):
                month_key = f"{y}-{m:02d}"
                if month_key in existing_months:
                    continue

                print(f"📦 處理：{stock_id} - {y}/{m:02d}")
                try:
                    insert_monthly_data(stock_id, y, m, cursor)
                    conn.commit()
                    total_inserted += cursor.rowcount
                except Exception as e:
                    print(f"❌ 發生錯誤：{stock_id} {y}-{month_key} -> {e}")
                    continue

                sleep_time = round(random.uniform(0.5, 0.8), 2)
                print(f"⏱️ 等待 {sleep_time} 秒...")
                time.sleep(sleep_time)

    conn.close()
    print(f"\n✅ 抓取完成，第 {partition}/{total_partitions} 組共新增 {total_inserted} 筆")
