from crawler_utils.db import get_connection

def create_twii_tables():
    create_sql_template = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        open DECIMAL(10,2) NOT NULL,
        high DECIMAL(10,2) NOT NULL,
        low DECIMAL(10,2) NOT NULL,
        close DECIMAL(10,2) NOT NULL,
        volume BIGINT NOT NULL,
        trade_count BIGINT NOT NULL,
        amount BIGINT NOT NULL,
        change_point DECIMAL(10,2) NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY unique_date (date)
    );
    """

    tables = ["twii_daily", "twii_weekly", "twii_monthly"]

    conn = get_connection()
    cursor = conn.cursor()

    for table in tables:
        try:
            cursor.execute(create_sql_template.format(table_name=table))
            print(f"資料表 {table} 建立成功")
        except Exception as e:
            print(f"資料表 {table} 建立失敗：{e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_twii_tables()