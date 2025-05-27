import time
from utils.twse_client import get_twse_listed_companies
from utils.otc_client import get_otc_listed_companies
from utils.db import get_connection

def sync_stock_info():
    print("🔄 開始同步 stock_info ...")

    # 1. 抓取資料
    twse_data = get_twse_listed_companies()
    time.sleep(1)  # 防止短時間大量請求
    otc_data = get_otc_listed_companies()
    all_data = twse_data + otc_data

    # 2. 防止抓不到資料卻清空資料庫
    if not all_data:
        print("⚠️ 沒有抓到任何股票資料，暫停更新 stock_info")
        return

    # 3. 清空並重新插入資料
    conn = get_connection()
    cursor = conn.cursor()

    print("🧹 清空 stock_info 資料表 ...")
    cursor.execute("TRUNCATE TABLE stock_info")

    insert_sql = """
        INSERT INTO stock_info (
            stock_id, stock_name, isin_code,
            security_type, industry, listed_date, cfi_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            d["stock_id"],
            d["stock_name"],
            d["isin_code"],
            d["security_type"],
            d["industry"],
            d["listed_date"],
            d["cfi_code"]
        ) for d in all_data
    ]

    cursor.executemany(insert_sql, values)
    conn.commit()
    conn.close()

    print(f"成功插入 {len(values)} 筆最新 stock_info 資料")

if __name__ == "__main__":
    sync_stock_info()
