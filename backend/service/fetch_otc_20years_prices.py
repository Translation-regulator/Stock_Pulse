
import requests
import time
import random
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from utils.db import get_connection
import urllib3
from tqdm import tqdm # type: ignore


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# CLI 參數：第幾組、總共幾組
part_index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
total_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 5

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

def is_month_fetched(stock_id, year, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM stock_daily_price
        WHERE stock_id = %s AND YEAR(date) = %s AND MONTH(date) = %s
        LIMIT 1
    """, (stock_id, year, month))
    row = cursor.fetchone()
    conn.close()
    return row is not None

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

        print(f"✅ 抓取 {stock_id} {year}-{month:02d} 共 {len(result)} 筆")
        return result

    except Exception as e:
        print(f"⚠️ 抓取錯誤：{stock_id} {year}-{month:02d} → {e}")
        return []

def insert_price_to_db(rows):
    if not rows:
        return
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
    print(f"📝 已寫入 {len(rows)} 筆")

if __name__ == "__main__":
    all_ids = get_all_otc_ids()
    total = len(all_ids)
    chunk_size = total // total_parts
    start_index = (part_index - 1) * chunk_size
    end_index = start_index + chunk_size if part_index < total_parts else total
    ids_to_fetch = all_ids[start_index:end_index]

    print(f"🚀 第 {part_index}/{total_parts} 組，共 {len(ids_to_fetch)} 檔")

    for stock_id in tqdm(ids_to_fetch, desc="📊 股票進度", unit="檔"):
        listed_date = get_listed_date(stock_id)
        start_year = max(listed_date.year, 2005)
        print(f"📦 開始處理 {stock_id}，從 {start_year} 年起")

        for year in range(start_year, 2025):
            for month in range(1, 13):
                if year == listed_date.year and month < listed_date.month:
                    continue
                if is_month_fetched(stock_id, year, month):
                    print(f"⏩ 已存在：{stock_id} {year}-{month:02d}")
                    continue
                rows = get_otc_monthly_html_prices(stock_id, year, month)
                insert_price_to_db(rows)
                time.sleep(random.uniform(3, 5))  
