import time
from datetime import datetime, timedelta
import calendar
from utils.db import get_connection
from utils.twse_price_client import get_monthly_daily_price
from tqdm import tqdm

def convert_to_ad_date(date_str):
    """ 將 '111-01-03' 轉為 '2022-01-03' """
    try:
        y, m, d = date_str.split("-")
        year = int(y) + 1911
        return f"{year}-{m}-{d}"
    except:
        return None

def get_four_digit_stocks():
    """ 從資料庫撈出所有四碼的普通股 """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stock_id FROM stock_info
        WHERE CHAR_LENGTH(stock_id) = 4 AND is_active = TRUE
        AND listing_type = '上市'
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def has_data_for_month(stock_id, year, month):
    """ 檢查某檔股票某年某月是否已有資料 """
    conn = get_connection()
    cursor = conn.cursor()
    start_date = f"{year}-{month:02d}-01"
    end_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{end_day}"
    cursor.execute("""
        SELECT COUNT(*) FROM daily_price
        WHERE stock_id = %s AND date BETWEEN %s AND %s
    """, (stock_id, start_date, end_date))
    count = cursor.fetchone()[0]
    conn.close()
    return count >= 10  # 若已有 10 筆以上資料，視為該月已存在

def insert_monthly_data(stock_id, year, month, cursor):
    prices = get_monthly_daily_price(stock_id, year, month)
    for p in prices:
        date = convert_to_ad_date(p["date"])
        if not date:
            continue
        try:
            cursor.execute("""
                INSERT IGNORE INTO daily_price
                (stock_id, date, open, high, low, close, volume, amount, change_price, transaction_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                stock_id,
                date,
                p["open"],
                p["high"],
                p["low"],
                p["close"],
                p["volume"],
                p["amount"],
                p["change"],
                p["transaction_count"]
            ))
        except Exception as e:
            print(f"❌ 寫入失敗：{stock_id} {date} -> {e}")

def fetch_daily_prices_last_year():
    stock_ids = get_four_digit_stocks()
    end = datetime.today()
    start = end - timedelta(days=365)

    print(f"📆 抓取範圍：{start.date()} ~ {end.date()}")
    print(f"📈 四碼普通股數量：{len(stock_ids)} 檔")

    conn = get_connection()
    cursor = conn.cursor()
    total_inserted = 0

    for stock_id in tqdm(stock_ids, desc="股票進度"):
        for y in range(start.year, end.year + 1):
            for m in range(1, 13):
                month_start = datetime(y, m, 1)
                if month_start < start or month_start > end:
                    continue
                if has_data_for_month(stock_id, y, m):
                    print(f"⏩ 略過 {stock_id} - {y}/{m:02d}（已有資料）")
                    continue
                print(f"📦 {stock_id} - {y}/{m:02d}")
                insert_monthly_data(stock_id, y, m, cursor)
                conn.commit()
                total_inserted += cursor.rowcount
                time.sleep(0.5)

    conn.close()
    print(f"\n✅ 抓取完成，新增資料共 {total_inserted} 筆")

if __name__ == "__main__":
    fetch_daily_prices_last_year()
