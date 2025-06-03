from datetime import datetime, timedelta
from service.insert_twii_index import fetch_twii_by_month, insert_twii_data
from crawler_utils.db import get_connection

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
    start_date = datetime(2005, 1, 1).date()  # ✅ 從 2005-01-01 全面補抓

    print("開始執行 TWII 全量補抓")
    print(f"當前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"補抓區間：{start_date} ～ {today}")

    workdays = get_workdays(start_date, today)
    if not workdays:
        print("⚠️ 無有效工作日")
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
