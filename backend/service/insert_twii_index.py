import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.db import get_connection
import urllib3
import time
import random
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def convert_to_ad_date(date_str):
    try:
        y, m, d = map(int, date_str.split('/'))
        return datetime(y + 1911, m, d).date()
    except:
        return None


def fetch_summary_by_date(date):
    date_str = date.strftime("%Y%m%d")
    headers = {"User-Agent": "Mozilla/5.0"}
    volume = trade_count = 0
    weighted_index = change_point = 0.0

    # 第一段：抓成交量（afterTrading/MI_INDEX）
    url_volume = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date_str}&type=MS&response=html"
    try:
        time.sleep(1.0)
        res = requests.get(url_volume, headers=headers, verify=False)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4 and "總計" in cols[0].text:
                    volume = int(cols[2].text.replace(",", ""))
                    trade_count = int(cols[3].text.replace(",", ""))
                    break

    except Exception as e:
        print(f"❌ 抓成交量失敗 {date_str}: {e}")

    # 第二段：抓加權指數（TAIEX/MI_5MINS_HIST）
    url_index = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST"
    params = {"response": "html", "date": date_str}
    try:
        time.sleep(1.0)
        res = requests.get(url_index, headers=headers, params=params, verify=False)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[2:]:
                time.sleep(random.uniform(1.0, 1.5))  # 每日資料間隔避免被鎖
                cols = row.find_all("td")
                if len(cols) >= 5:
                    html_date = cols[0].text.strip()
                    ad_date = convert_to_ad_date(html_date)
                    if ad_date == date:
                        weighted_index = float(cols[4].text.replace(",", ""))
                        change_point = weighted_index - float(cols[1].text.replace(",", ""))
                        break
    except Exception as e:
        print(f"❌ 抓加權指數失敗 {date_str}: {e}")

    print(f"📊 {date} volume: {volume}, trade_count: {trade_count}, index: {weighted_index}, change: {change_point}")
    return volume, trade_count, weighted_index, change_point


def fetch_twii_by_month(year, month):
    url = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST"
    params = {
        "response": "html",
        "date": f"{year}{month:02d}01"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    print(f"🔗 抓取網址: {url}?response=html&date={params['date']}")

    res = requests.get(url, params=params, headers=headers, verify=False)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")

    if not table:
        print(f"⚠️ 找不到 {params['date']} 的表格")
        return []

    result = []
    rows = table.find_all("tr")
    for row in rows[2:]:
        time.sleep(1.5)  # 加入延遲以避免頻繁請求被封鎖
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        try:
            ad_date = convert_to_ad_date(cols[0].text.strip())
            if ad_date.month != month or ad_date.year != year:
                continue  # 避免抓到非該月份資料
            open_price = float(cols[1].text.replace(",", ""))
            high_price = float(cols[2].text.replace(",", ""))
            low_price = float(cols[3].text.replace(",", ""))
            close_price = float(cols[4].text.replace(",", ""))

            volume, trade_count, weighted_index, change_point = fetch_summary_by_date(ad_date)
            

            result.append({
                "date": ad_date,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
                "trade_count": trade_count,
                "weighted_index": weighted_index,
                "change_point": change_point
            })
        except Exception as e:
            print(f"⚠️ 跳過資料列：{e}")
            continue

    print(f"🧾 原始資料筆數：{len(result)}，前5筆：")
    for item in result[:5]:
        print(item)

    return result


def insert_twii_data(data):
    conn = get_connection()
    cursor = conn.cursor()
    for item in data:
        try:
            cursor.execute("""
                INSERT INTO twii_index
                (date, open, high, low, close, volume, trade_count, weighted_index, change_point)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    open=VALUES(open),
                    high=VALUES(high),
                    low=VALUES(low),
                    close=VALUES(close),
                    volume=VALUES(volume),
                    trade_count=VALUES(trade_count),
                    weighted_index=VALUES(weighted_index),
                    change_point=VALUES(change_point)
            """, (
                item["date"],
                item["open"],
                item["high"],
                item["low"],
                item["close"],
                item["volume"],
                item["trade_count"],
                item["weighted_index"],
                item["change_point"]
            ))
        except Exception as e:
            print(f"❌ 寫入失敗 {item['date']} -> {e}")
    conn.commit()
    conn.close()

def get_twii_daily_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT date, open, high, low, close
        FROM twii_index
        ORDER BY date ASC
    """)
    result = cursor.fetchall()
    conn.close()
    return result
