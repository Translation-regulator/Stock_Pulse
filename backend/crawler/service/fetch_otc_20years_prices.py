import requests
import time
import random
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from crawler_utils.db import get_connection, get_cursor
import urllib3
from tqdm import tqdm  # type: ignore

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

part_index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
total_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 5

def get_all_otc_ids():
    with get_cursor() as cursor:
        cursor.execute("SELECT stock_id FROM stock_info WHERE security_type = '上櫃' ORDER BY stock_id")
        rows = cursor.fetchall()
    return [row[0] for row in rows]

def get_listed_date(stock_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT listed_date FROM stock_info WHERE stock_id = %s", (stock_id,))
        row = cursor.fetchone()
    return row[0] if row and row[0] else datetime(2005, 1, 1).date()

def get_otc_monthly_html_prices(stock_id, year, month):
    date_str = f"{year}/{month:02d}/01"
    url = f"https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?response=html&date={date_str}&code={stock_id}"

    try:
        res = requests.get(url, timeout=10, verify=False)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")

        if not table:
            print(f"\U0001F4ED 沒有資料表格：{stock_id} {year}-{month:02d}")
            return []

        rows = table.find_all("tr")[2:]
        result = []

        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 9 or "/" not in tds[0].text:
                continue

            try:
                y, m, d = map(int, tds[0].text.strip().split("/"))
                ad_date = datetime(y + 1911, m, d).date()
            except:
                continue

            def parse(val):
                try:
                    return float(val.replace(",", "").replace("--", ""))
                except:
                    return None

            parsed = [parse(tds[i].text) for i in [1, 2, 3, 4, 5, 6, 7, 8]]
            result.append({
                "stock_id": stock_id,
                "date": ad_date,
                "open": parsed[2],
                "high": parsed[3],
                "low": parsed[4],
                "close": parsed[5],
                "change_price": parsed[6],
                "transaction_count": int(parsed[7]) if parsed[7] else None,
                "volume": int(parsed[0] * 1000) if parsed[0] else None,
                "amount": int(parsed[1] * 1000) if parsed[1] else None
            })

        print(f"抓取 {stock_id} {year}-{month:02d} 共 {len(result)} 筆")
        return result

    except Exception as e:
        print(f"抓取錯誤：{stock_id} {year}-{month:02d} → {e}")
        return []

def insert_price_to_db(rows):
    if not rows:
        return

    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """REPLACE INTO stock_daily_price (
            stock_id, date, open, high, low, close, change_price,
            volume, amount, transaction_count
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = [
            (
                row["stock_id"], row["date"], row["open"], row["high"],
                row["low"], row["close"], row["change_price"],
                row["volume"], row["amount"], row["transaction_count"]
            ) for row in rows
        ]
        cursor.executemany(query, values)
        conn.commit()
    finally:
        conn.close()
    print(f"已寫入 {len(rows)} 筆")

def main():
    all_ids = get_all_otc_ids()
    total = len(all_ids)
    chunk_size = total // total_parts
    start_index = (part_index - 1) * chunk_size
    end_index = start_index + chunk_size if part_index < total_parts else total
    ids_to_fetch = all_ids[start_index:end_index]

    current_year = datetime.today().year
    current_month = datetime.today().month

    print(f"第 {part_index}/{total_parts} 組，共 {len(ids_to_fetch)} 檔")

    for stock_id in tqdm(ids_to_fetch, desc="股票進度", unit="檔"):
        listed_date = get_listed_date(stock_id)
        start_year = max(listed_date.year, 2005)
        print(f"開始處理 {stock_id}，從 {start_year} 年起")

        for year in range(start_year, current_year + 1):
            year_rows = []
            for month in range(1, 13):
                if year == listed_date.year and month < listed_date.month:
                    continue
                if year == current_year and month > current_month:
                    break
                rows = get_otc_monthly_html_prices(stock_id, year, month)
                year_rows.extend(rows)
                time.sleep(random.uniform(0.5, 0.8))

            if year_rows:
                print(f"寫入 {stock_id} 年 {year} 共 {len(year_rows)} 筆")
                insert_price_to_db(year_rows)
            else:
                print(f"❗ {stock_id} 年 {year} 沒有資料")

if __name__ == "__main__":
    main()
