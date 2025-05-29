import requests
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from crawler_utils.db import get_connection
from tqdm import tqdm # type: ignore
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_current_year_month():
    today = datetime.today()
    return today.year, today.month

def get_all_otc_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id FROM stock_info WHERE listing_type = '上櫃' ORDER BY stock_id")
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

# ✅ 新增：取得該股票當月已存在的日期集合
def get_existing_dates(stock_id, year, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date FROM stock_daily_price
        WHERE stock_id = %s AND YEAR(date) = %s AND MONTH(date) = %s
    """, (stock_id, year, month))
    rows = cursor.fetchall()
    conn.close()
    return set(row[0] for row in rows)

def insert_price_to_db(rows):
    if not rows:
        print("⚠️ 沒有新資料需要寫入")
        return 0
    print(f"📝 準備寫入 {len(rows)} 筆資料，範例：{rows[0]}")
    conn = get_connection()
    cursor = conn.cursor()
    query = """REPLACE INTO stock_daily_price (
        stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = [
        (
            row["stock_id"], row["date"], row["open"], row["high"],
            row["low"], row["close"], row["volume"], row["amount"],
            row.get("change_price"), row.get("transaction_count")
        ) for row in rows
    ]
    cursor.executemany(query, values)
    conn.commit()
    conn.close()
    return len(rows)

def get_otc_monthly_html_prices(stock_id, year, month, max_retries=3):
    date_str = f"{year}/{month:02d}/01"
    url = f"https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?response=html&date={date_str}&code={stock_id}"

    for attempt in range(1, max_retries + 1):
        try:
            res = requests.get(url, timeout=20, verify=False)
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
                        return float(val.replace(",", "").replace("--", "").replace("+", "").strip())
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
                    "amount": int(parse(tds[2].text) * 1000) if parse(tds[2].text) else None,
                    "change_price": parse(tds[7].text),
                    "transaction_count": int(parse(tds[8].text)) if parse(tds[8].text) else None
                })

            return result

        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout 第 {attempt}/{max_retries} 次：{stock_id} {year}-{month:02d}")
        except Exception as e:
            print(f"❌ 嘗試第 {attempt} 次失敗：{stock_id} {year}-{month:02d} → {e}")

        time.sleep(random.uniform(1.0, 2.0))

    return None

def fetch_otc_current_month_prices():
    year, month = get_current_year_month()
    stock_ids = get_all_otc_ids()
    total_inserted = 0
    failed_ids = []

    print(f"\U0001F4E6 開始抓取上櫃股票：{year}-{month:02d} 共 {len(stock_ids)} 檔")

    for stock_id in tqdm(stock_ids, desc="\U0001F4CA 上櫃日線補抓中"):
        listed = get_listed_date(stock_id)
        if listed.year > year or (listed.year == year and listed.month > month):
            continue

        rows = get_otc_monthly_html_prices(stock_id, year, month)
        if rows is None:
            failed_ids.append(stock_id)
            continue

        # ✅ 使用快速方式比對哪些資料尚未寫入
        existing_dates = get_existing_dates(stock_id, year, month)
        new_rows = [r for r in rows if r["date"] not in existing_dates]

        inserted = insert_price_to_db(new_rows)
        total_inserted += inserted
        time.sleep(random.uniform(1, 1.2))

    print(f"\n✅ 上櫃日線補抓完成，總共新增 {total_inserted} 筆資料")
    if failed_ids:
        print(f"❌ 有 {len(failed_ids)} 檔抓取失敗，已寫入 otc_failed_ids.txt")
        with open("otc_failed_ids.txt", "w", encoding="utf-8") as f:
            for stock_id in failed_ids:
                f.write(f"{stock_id}\n")

if __name__ == "__main__":
    fetch_otc_current_month_prices()
