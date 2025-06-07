import requests
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm  # type: ignore
import urllib3

from sqlalchemy import Table, MetaData, text
from sqlalchemy.dialects.mysql import insert as mysql_insert
from crawler_utils.db import engine

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_current_year_month():
    today = datetime.today()
    return today.year, today.month

def get_all_listed_ids():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT stock_id FROM stock_info 
            WHERE listing_type = '上市' 
            ORDER BY stock_id
        """))
        return [row[0] for row in result.fetchall()]

def get_listed_date(stock_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT listed_date FROM stock_info WHERE stock_id = :stock_id"),
            {"stock_id": stock_id}
        )
        row = result.fetchone()
        return row[0] if row and row[0] else datetime(2005, 1, 1).date()

def get_existing_dates(stock_id, year, month):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT date, volume, close FROM stock_daily_price
            WHERE stock_id = :stock_id AND YEAR(date) = :year AND MONTH(date) = :month
        """), {"stock_id": stock_id, "year": year, "month": month})
        rows = result.fetchall()

    complete_dates = set()
    incomplete_dates = set()
    for date, volume, close in rows:
        if volume and close is not None:
            complete_dates.add(date)
        else:
            incomplete_dates.add(date)
    return complete_dates, incomplete_dates

def insert_price_to_db(rows):
    if not rows:
        print("沒有新資料需要寫入")
        return 0

    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = Table("stock_daily_price", metadata, autoload_with=engine)

    inserted_count = 0

    with engine.begin() as conn:
        for row in rows:
            try:
                stmt = mysql_insert(table).values(**row)
                stmt = stmt.on_duplicate_key_update(
                    open=stmt.inserted.open,
                    high=stmt.inserted.high,
                    low=stmt.inserted.low,
                    close=stmt.inserted.close,
                    volume=stmt.inserted.volume,
                    amount=stmt.inserted.amount,
                    change_price=stmt.inserted.change_price,
                    transaction_count=stmt.inserted.transaction_count
                )
                conn.execute(stmt)
                inserted_count += 1
            except Exception as e:
                print(f"❌ 存入失敗 {row['stock_id']} {row['date']} → {e}")

    return inserted_count

def get_twse_monthly_html_prices(stock_id, year, month, max_retries=3):
    date_str = f"{year}{month:02d}01"
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={date_str}&stockNo={stock_id}&response=html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.twse.com.tw/"
    }

    for attempt in range(1, max_retries + 1):
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=20)
            if res.status_code != 200:
                print(f"⚠️ HTTP {res.status_code}，等待 retry")
                raise Exception("HTTP 非 200 回應")

            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            if not table:
                print(f"⚠️ {stock_id} 找不到資料表格")
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
                    "volume": int(parse(tds[1].text)) if parse(tds[1].text) else None,
                    "amount": int(parse(tds[2].text)) if parse(tds[2].text) else None,
                    "change_price": parse(tds[7].text),
                    "transaction_count": int(parse(tds[8].text)) if parse(tds[8].text) else None
                })

            return result

        except Exception as e:
            print(f"嘗試第 {attempt} 次失敗：{stock_id} {year}-{month:02d} → {e}")
            time.sleep(3 * attempt + random.uniform(2, 4))

    return None

def fetch_twse_current_month_prices():
    year, month = get_current_year_month()
    stock_ids = get_all_listed_ids()
    all_rows = []
    failed_ids = []
    skipped_ids = []

    print(f"📦 開始抓取上市股票：{year}-{month:02d} 共 {len(stock_ids)} 檔")

    for idx, stock_id in enumerate(tqdm(stock_ids, desc="📊 上市日線補抓中")):
        listed = get_listed_date(stock_id)
        if listed.year > year or (listed.year == year and listed.month > month):
            continue

        rows = get_twse_monthly_html_prices(stock_id, year, month)
        if rows is None:
            failed_ids.append(stock_id)
            continue
        if not rows:
            skipped_ids.append(stock_id)
            continue

        complete_dates, incomplete_dates = get_existing_dates(stock_id, year, month)
        new_rows = [
            r for r in rows
            if r["date"] not in complete_dates or r["date"] in incomplete_dates
        ]
        all_rows.extend(new_rows)

        if idx > 0 and idx % 50 == 0:
            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(1.2, 2))

    inserted = insert_price_to_db(all_rows)

    print(f"上市日線補抓完成，總共新增 {inserted} 筆資料")

if __name__ == "__main__":
    fetch_twse_current_month_prices()