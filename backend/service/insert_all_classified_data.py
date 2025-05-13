from utils.db import get_connection
from utils.finmind_client import FinMindClient
from utils.stock_classifier import StockCategory

def insert_company_stocks(data, clear_table=False):
    conn = get_connection()
    cursor = conn.cursor()

    if clear_table:
        cursor.execute("TRUNCATE TABLE taiwan_stocks")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taiwan_stocks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_id VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            type ENUM('上市', '上櫃') NOT NULL,
            industry VARCHAR(50)
        ) CHARACTER SET = utf8mb4;
    """)

    count = 0
    for item in data:
        if not StockCategory.is_company_stock(item):
            continue
        stock_id = item["stock_id"]
        name = item["stock_name"]
        stock_type = "上市" if item["type"] == "twse" else "上櫃"
        industry = item.get("industry_category", "其他")

        cursor.execute("""
            INSERT INTO taiwan_stocks (stock_id, name, type, industry)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, type=%s, industry=%s
        """, (stock_id, name, stock_type, industry, name, stock_type, industry))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"公司股票寫入完成，共 {count} 筆")

def insert_etfs(data, clear_table=False):
    conn = get_connection()
    cursor = conn.cursor()

    if clear_table:
        cursor.execute("TRUNCATE TABLE taiwan_etf")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taiwan_etf (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_id VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            type ENUM('上市', '上櫃') NOT NULL,
            industry VARCHAR(50)
        ) CHARACTER SET = utf8mb4;
    """)

    count = 0
    for item in data:
        if not StockCategory.is_etf(item):
            continue
        stock_id = item["stock_id"]
        name = item["stock_name"]
        etf_type = "上市" if item["type"] == "twse" else "上櫃"
        industry = item.get("industry_category", "ETF")

        cursor.execute("""
            INSERT INTO taiwan_etf (stock_id, name, type, industry)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, type=%s, industry=%s
        """, (stock_id, name, etf_type, industry, name, etf_type, industry))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"ETF 資料寫入完成，共 {count} 筆")

def insert_stock_indexes(data, clear_table=False):
    conn = get_connection()
    cursor = conn.cursor()

    if clear_table:
        cursor.execute("TRUNCATE TABLE taiwan_stock_index")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taiwan_stock_index (
            id INT AUTO_INCREMENT PRIMARY KEY,
            index_id VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            industry VARCHAR(50)
        ) CHARACTER SET = utf8mb4;
    """)

    count = 0
    for item in data:
        if not StockCategory.is_index(item):
            continue
        index_id = item["stock_id"]
        name = item["stock_name"]
        industry = item.get("industry_category", "分類")

        cursor.execute("""
            INSERT INTO taiwan_stock_index (index_id, name, industry)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, industry=%s
        """, (index_id, name, industry, name, industry))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"指數分類資料寫入完成，共 {count} 筆")

def run_all(clear_table=False):
    client = FinMindClient()
    data = client.get_company_list()

    total = len(data)
    count_stock = sum(1 for d in data if StockCategory.is_company_stock(d))
    count_etf = sum(1 for d in data if StockCategory.is_etf(d))
    count_index = sum(1 for d in data if StockCategory.is_index(d))

    print("\n分類統計：")
    print(f"總筆數：{total}")
    print(f"公司股票：{count_stock}")
    print(f"ETF：{count_etf}")
    print(f"分類指數：{count_index}\n")

    insert_company_stocks(data, clear_table)
    insert_etfs(data, clear_table)
    insert_stock_indexes(data, clear_table)

if __name__ == "__main__":
    run_all(clear_table=True)
