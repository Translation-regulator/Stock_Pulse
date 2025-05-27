from datetime import datetime, timedelta
from service.insert_twii_index import fetch_twii_by_month, insert_twii_data
from utils.db import get_connection

def get_last_date_in_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(date) FROM twii_index")
    row = cursor.fetchone()
    conn.close()
    return row[0] or datetime(2000, 1, 1).date()

def get_workdays(start_date, end_date):
    current = start_date
    days = []
    while current <= end_date:
        if current.weekday() < 5:  # 週一到週五為工作日
            days.append(current)
        current += timedelta(days=1)
    return days

def main():
    today = datetime.today().date()
    last_date = get_last_date_in_db()

    print(f"最後一筆資料日期：{last_date}")
    print(f"補抓區間：{last_date + timedelta(days=1)} ～ {today}")

    workdays = get_workdays(last_date + timedelta(days=1), today)
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
                print(f"寫入 {target_day} 成功")
                total += 1
            else:
                print(f"{target_day} 已存在，略過")
        else:
            print(f"{target_day} 沒有在 API 回傳中，可能休市")

    print(f"補抓完成，共新增 {total} 筆 TWII 資料")

if __name__ == "__main__":
    main()
