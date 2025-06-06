from datetime import datetime, timedelta
from service.insert_twii_index import fetch_twii_by_month, insert_twii_data
from crawler_utils.db import engine
import pandas as pd
from sqlalchemy import text

def get_last_date_in_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(date) FROM twii_daily"))
        last_date = result.scalar()
        return last_date or datetime(2000, 1, 1).date()

def is_twii_day_complete(date):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT volume, close FROM twii_daily WHERE date = :date"),
            {"date": date}
        ).fetchone()
        if not result:
            return False
        volume, close = result
        return bool(volume) and close is not None

def get_workdays(start_date, end_date, check_db=True):
    current = start_date
    days = []
    while current <= end_date:
        if current.weekday() < 5:
            if not check_db or not is_twii_day_complete(current):
                days.append(current)
        current += timedelta(days=1)
    return days

def main():
    today = datetime.today().date()
    first_day_this_month = today.replace(day=1)
    last_date_in_db = get_last_date_in_db()
    last_date = max(last_date_in_db, first_day_this_month)

    print("開始執行每日更新作業")
    print(f"當前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n===== 大盤指數補抓開始 =====")
    print(f"最後一筆資料日期：{last_date_in_db}")
    print(f"補抓區間：{last_date + timedelta(days=1)} ～ {today}")

    workdays = get_workdays(last_date + timedelta(days=1), today, check_db=True)
    if not workdays:
        print("資料已是最新，無需補抓。")
        return

    fetched_months = set()
    monthly_cache = {}
    total = 0

    for target_day in workdays:
        ym = (target_day.year, target_day.month)
        if ym not in fetched_months:
            try:
                print(f"\n抓取 {ym[0]}/{ym[1]:02d} 全月資料中...")
                data = fetch_twii_by_month(ym[0], ym[1])
                monthly_cache[ym] = data
                fetched_months.add(ym)
            except Exception as e:
                print(f"抓取 {ym[0]}/{ym[1]:02d} 失敗：{e}")
                continue

        month_data = monthly_cache.get(ym, [])
        data_for_day = [d for d in month_data if d["date"] == target_day]

        if data_for_day:
            inserted_dates = insert_twii_data(data_for_day)
            if inserted_dates:
                print(f"✅ 寫入 {target_day} 成功")
                total += 1
            else:
                print(f"{target_day} 已存在，略過")
        else:
            print(f"{target_day} 沒有在 API 回傳中，可能休市")

    print(f"\n📈 補抓完成，共新增 {total} 筆 TWII 資料")

if __name__ == "__main__":
    main()
