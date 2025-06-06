import requests
from bs4 import BeautifulSoup
from datetime import datetime
from crawler_utils.db import engine  
import urllib3
import time
import random

from sqlalchemy import Table, MetaData
from sqlalchemy.dialects.mysql import insert as mysql_insert

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def convert_to_ad_date(date_str):
    try:
        y, m, d = map(int, date_str.split('/'))
        return datetime(y + 1911, m, d).date()
    except:
        return None

def retry_request(url, headers=None, params=None, max_retries=2, sleep_range=(0.5, 1.0)):
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(*sleep_range))
            res = requests.get(url, headers=headers, params=params, verify=False)
            res.encoding = "utf-8"
            return res
        except Exception as e:
            print(f"⚠️ 第 {attempt+1} 次嘗試失敗：{e}")
            if attempt == max_retries - 1:
                raise e

def fetch_summary_by_date(date):
    date_str = date.strftime("%Y%m%d")
    headers = {"User-Agent": "Mozilla/5.0"}
    volume = trade_count = amount = 0
    change_point = 0.0

    url_volume = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date_str}&type=MS&response=html"
    try:
        res = retry_request(url_volume, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4 and "總計" in cols[0].text:
                    amount = int(cols[1].text.replace(",", ""))
                    volume = int(cols[2].text.replace(",", ""))
                    trade_count = int(cols[3].text.replace(",", ""))
                    break
    except Exception as e:
        print(f"抓成交金額與成交量失敗 {date_str}: {e}")

    url_index = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST"
    params = {"response": "html", "date": date_str}
    try:
        res = retry_request(url_index, headers=headers, params=params)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[2:]:
                time.sleep(random.uniform(0.5, 1.0))
                cols = row.find_all("td")
                if len(cols) >= 5:
                    html_date = cols[0].text.strip()
                    ad_date = convert_to_ad_date(html_date)
                    if ad_date == date:
                        change_point = float(cols[4].text.replace(",", "")) - float(cols[1].text.replace(",", ""))
                        break
    except Exception as e:
        print(f"抓加權指數變化失敗 {date_str}: {e}")

    print(f"{date} amount: {amount}, volume: {volume}, trade_count: {trade_count}, change: {change_point}")
    return volume, trade_count, change_point, amount

def fetch_twii_by_month(year, month):
    url = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST"
    params = {
        "response": "html",
        "date": f"{year}{month:02d}01"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"抓取網址: {url}?response=html&date={params['date']}")

    try:
        res = retry_request(url, headers=headers, params=params)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
    except Exception as e:
        print(f"主資料抓取失敗：{e}")
        return []

    if not table:
        print(f"找不到 {params['date']} 的表格")
        return []

    result = []
    rows = table.find_all("tr")
    for row in rows[2:]:
        time.sleep(random.uniform(0.3, 0.6))
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        try:
            ad_date = convert_to_ad_date(cols[0].text.strip())
            if ad_date.month != month or ad_date.year != year:
                continue

            open_price = float(cols[1].text.replace(",", ""))
            high_price = float(cols[2].text.replace(",", ""))
            low_price = float(cols[3].text.replace(",", ""))
            close_price = float(cols[4].text.replace(",", ""))
            volume, trade_count, change_point, amount = fetch_summary_by_date(ad_date)

            result.append({
                "date": ad_date,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
                "trade_count": trade_count,
                "amount": amount,
                "change_point": change_point
            })
        except Exception as e:
            print(f"跳過資料列：{e}")
            continue

    print(f"原始資料筆數：{len(result)}，前5筆：")
    for item in result[:5]:
        print(item)

    return result

def insert_twii_data(data):
    if not data:
        return []

    metadata = MetaData()
    metadata.reflect(bind=engine)
    twii_daily = Table("twii_daily", metadata, autoload_with=engine)

    inserted_dates = []

    with engine.begin() as conn:
        for item in data:
            try:
                stmt = mysql_insert(twii_daily).values(**item)
                update_dict = {
                    "open": stmt.inserted.open,
                    "high": stmt.inserted.high,
                    "low": stmt.inserted.low,
                    "close": stmt.inserted.close,
                    "volume": stmt.inserted.volume,
                    "change_point": stmt.inserted.change_point,
                    "trade_count": stmt.inserted.trade_count,
                    "amount": stmt.inserted.amount
                }
                stmt = stmt.on_duplicate_key_update(**update_dict)
                conn.execute(stmt)
                inserted_dates.append(item["date"])
            except Exception as e:
                print(f"寫入失敗 {item['date']} -> {e}")

    return inserted_dates
