import requests
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from utils.db import get_connection
from tqdm import tqdm  # type: ignore
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_current_year_month():
    today = datetime.today()
    return today.year, today.month

def get_all_otc_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id FROM stock_info WHERE security_type = '上櫃' ORDER BY stock_id")
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
        stock_id, date, open, high, low, close, volume, amount
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    values = [
        (
            row["stock_id"], row["date"], row["open"], row["high"],
            row["low"], row["close"], row["volume"], row["amount"]
        ) for row in rows
    ]
    cursor.executemany(query, values)
    conn.commit()
    conn.close()
    return len(rows)

def get_otc_monthly_html_prices(stock_id, year, month):
    date_str = f"{year}/{month:02d}/01"
    url = f"https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?response=html&date={date_str}&code={stock_id}"
    try:
        res = requests.get(url, timeout=10, verify=False)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if not table:
            print(f"📭 沒有資料表格：{stock_id} {year}-{month:02d}")
            return []

        rows = table.find_all("tr")[2:]
        result = []

        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 9:
                continue
            raw_date = tds[0].text.strip()
            if "/" not in raw_date:
                continue

            def parse(val):
                try:
                    return float(val.replace(",", "").replace("--", ""))
                except:
                    return None

            try:
                y, m, d = map(int, raw_date.split("/"))
                ad_date = datetime(y + 1911, m, d).date()
            except:
                continue

            if ad_date.year != year or ad_date.month != month:
                continue

            result.append({
                "stock_id": stock_id,
                "date": ad_date,
                "open": parse(tds[3].text),
                "high": parse(tds[4].text),
                "low": parse(tds[5].text),
                "close": parse(tds[6].text),
                "volume": int(parse(tds[1].text) * 1000) if parse(tds[1].text) else None,
                "amount": int(parse(tds[2].text) * 1000) if parse(tds[2].text) else None
            })

        return result

    except Exception as e:
        print(f"抓取錯誤：{stock_id} {year}-{month:02d} → {e}")
        return []

def fetch_otc_current_month_prices():
    year, month = get_current_year_month()
    stock_ids = get_all_otc_ids()
    total_inserted = 0

    print(f"📦 開始抓取上櫃股票：{year}-{month:02d} 共 {len(stock_ids)} 檔")

    for stock_id in tqdm(stock_ids, desc="📊 上櫃日線補抓中"):
        listed = get_listed_date(stock_id)
        if listed.year > year or (listed.year == year and listed.month > month):
            continue

        rows = get_otc_monthly_html_prices(stock_id, year, month)
        new_rows = [r for r in rows if not is_date_fetched(r["stock_id"], r["date"])]
        inserted = insert_price_to_db(new_rows)
        total_inserted += inserted
        time.sleep(random.uniform(0.5, 0.8))

    print(f"\n上櫃日線補抓完成，總共新增 {total_inserted} 筆資料")

if __name__ == "__main__":
    fetch_otc_current_month_prices()
