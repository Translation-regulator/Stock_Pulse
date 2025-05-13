# service/insert_stock_info.py

from utils.twse_client import get_twse_listed_companies
from utils.otc_client import get_otc_listed_companies
from utils.db import get_connection

def insert_or_update_stock_info():
    # 1. 取得上市與上櫃公司資料
    twse_data = get_twse_listed_companies()
    otc_data = get_otc_listed_companies()
    all_new_data = twse_data + otc_data

    # 2. 整理成 stock_id: {...} 格式
    new_data_map = {item["stock_id"]: item for item in all_new_data}
    new_stock_ids = set(new_data_map.keys())

    # 3. 建立資料庫連線
    conn = get_connection()
    cursor = conn.cursor()

    # 4. 取得現有資料庫 stock_id 列表
    cursor.execute("SELECT stock_id FROM stock_info")
    existing_rows = cursor.fetchall()
    existing_ids = set(row[0] for row in existing_rows)

    # 5. 要新增的項目
    insert_ids = new_stock_ids - existing_ids
    # 6. 要更新的項目
    update_ids = new_stock_ids & existing_ids
    # 7. 要標記下市的項目
    inactive_ids = existing_ids - new_stock_ids

    # 8. 執行 INSERT
    for stock_id in insert_ids:
        item = new_data_map[stock_id]
        cursor.execute("""
            INSERT INTO stock_info (
                stock_id, stock_name, isin_code, security_type,
                industry, listing_type, listed_date, remark, cfi_code, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (
            item["stock_id"],
            item["stock_name"],
            item["isin_code"],
            item["security_type"],
            item["industry"],
            item["listing_type"],
            item["listed_date"],
            item["remark"],
            item["cfi_code"]
        ))

    # 9. 執行 UPDATE
    for stock_id in update_ids:
        item = new_data_map[stock_id]
        cursor.execute("""
            UPDATE stock_info SET
                stock_name = %s,
                isin_code = %s,
                security_type = %s,
                industry = %s,
                listing_type = %s,
                listed_date = %s,
                remark = %s,
                cfi_code = %s,
                is_active = TRUE
            WHERE stock_id = %s
        """, (
            item["stock_name"],
            item["isin_code"],
            item["security_type"],
            item["industry"],
            item["listing_type"],
            item["listed_date"],
            item["remark"],
            item["cfi_code"],
            item["stock_id"]
        ))

    # 10. 將已下市的標記為 inactive
    for stock_id in inactive_ids:
        cursor.execute("""
            UPDATE stock_info SET is_active = FALSE WHERE stock_id = %s
        """, (stock_id,))

    conn.commit()
    conn.close()
    print(f"✅ 新增 {len(insert_ids)} 筆，更新 {len(update_ids)} 筆，標記下市 {len(inactive_ids)} 筆")

if __name__ == "__main__":
    insert_or_update_stock_info()
