from database.create_twii_table import create_twii_table
from service.insert_twii_index import fetch_twii_by_month, insert_twii_data
from utils.db import get_connection
from datetime import datetime
import time
import random
import calendar

# 檢查 twii_index 資料表中是否已經有該月份的資料（判斷 >= 10 筆）
def has_twii_data(year, month):
    conn = get_connection()
    cursor = conn.cursor()
    start_date = f"{year}-{month:02d}-01"
    end_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{end_day}"
    cursor.execute("""
        SELECT COUNT(*) FROM twii_index
        WHERE date BETWEEN %s AND %s
    """, (start_date, end_date))
    count = cursor.fetchone()[0]
    conn.close()
    return count >= 10

def fetch_twii_last_n_years(n_years=10):
    today = datetime.today()
    start = today.replace(year=today.year - n_years)
    print(f"開始抓取 {start.year}/{start.month} ~ {today.year}/{today.month} 的每月加權指數資料")

    for y in range(start.year, today.year + 1):
        for m in range(1, 13):
            target = datetime(y, m, 1)
            if target < start or target > today:
                continue

            if has_twii_data(y, m):
                print(f"略過 {y}/{m:02d}（已有資料）")
                continue

            print(f"抓取 {y}/{m:02d}...")
            try:
                data = fetch_twii_by_month(y, m)
                insert_twii_data(data)
                print(f"成功寫入 {len(data)} 筆資料 - {y}/{m:02d}")
            except Exception as e:
                print(f"抓取失敗 {y}/{m:02d}：{e}")

            delay = round(random.uniform(2.0, 4.0), 2)
            print(f"等待 {delay} 秒再繼續...")
            time.sleep(delay)

    print("加權指數資料抓取完成！")

if __name__ == "__main__":
    create_twii_table()
    fetch_twii_last_n_years(n_years=20)
