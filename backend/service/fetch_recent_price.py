import time
import random
from datetime import datetime
from utils.db import get_connection
from utils.twse_price_client import get_monthly_daily_price
from tqdm import tqdm  # type: ignore
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def get_current_year_month():
    today = datetime.today()
    return today.year, today.month

def get_all_listed_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id FROM stock_info WHERE listing_type = '上市' ORDER BY stock_id")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_listed_date(stock_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT listed_date FROM stock_info WHERE stock_id = %s", (stock_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else datetime(2005, 1, 1).date()

def is_date_fetched(stock_id, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM stock_daily_price WHERE stock_id = %s AND date = %s LIMIT 1", (stock_id, date))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def insert_price_to_db(rows):
    if not rows:
        return 0
    conn = get_connection()
    cursor = conn.cursor()
    query = """REPLACE INTO stock_daily_price (
        stock_id, date, open, high, low, close, volume, amount, change, transaction_count
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = [
        (
            row["stock_id"], row["date"], row["open"], row["high"],
            row["low"], row["close"], row["volume"], row["amount"],
            row.get("change"), row.get("transaction_count")
        ) for row in rows
    ]
    cursor.executemany(query, values)
    conn.commit()
    conn.close()
    return len(rows)

def safe_get_monthly_daily_price(stock_id, year, month, max_retries=2):
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(0.8, 1.5))  
            return get_monthly_daily_price(stock_id, year, month)
        except Exception as e:
            print(f"第 {attempt + 1} 次嘗試失敗：{stock_id} → {e}")
            if attempt == max_retries - 1:
                raise e


def fetch_listed_current_month_prices():
    year, month = get_current_year_month()
    stock_ids = get_all_listed_ids()
    total_inserted = 0

    print(f"\U0001F4E6 開始抓取上市股票：{year}-{month:02d} 共 {len(stock_ids)} 檔")

    for stock_id in tqdm(stock_ids, desc="\U0001F4CA 上市日線補抓中"):
        listed = get_listed_date(stock_id)
        if listed.year > year or (listed.year == year and listed.month > month):
            continue

        try:
            prices = safe_get_monthly_daily_price(stock_id, year, month)
        except Exception as e:
            print(f"抓取失敗：{stock_id} {year}-{month:02d} → {e}")
            continue

        new_rows = []
        for p in prices:
            try:
                ad_date = datetime.strptime(p["date"], "%Y-%m-%d").date()
            except:
                continue

            if ad_date.year != year or ad_date.month != month:
                continue

            if is_date_fetched(stock_id, ad_date):
                continue

            new_rows.append({
                "stock_id": stock_id,
                "date": ad_date,
                "open": p["open"],
                "high": p["high"],
                "low": p["low"],
                "close": p["close"],
                "volume": p["volume"],
                "amount": p["amount"],
                "change": p.get("change"),
                "transaction_count": p.get("transaction_count")
            })

        inserted = insert_price_to_db(new_rows)
        total_inserted += inserted

    print(f"\n上市日線補抓完成，總共新增 {total_inserted} 筆資料")

if __name__ == "__main__":
    fetch_listed_current_month_prices()
