from utils.db import get_connection

def create_price_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 日線表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_daily_price (
            id INT PRIMARY KEY AUTO_INCREMENT,
            stock_id VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            close DECIMAL(10, 2),
            volume BIGINT,
            amount BIGINT,
            change_price DECIMAL(10,2),
            transaction_count INT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_daily (stock_id, date),
            FOREIGN KEY (stock_id) REFERENCES stock_info(stock_id)
        );
    """)

    # 週線表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_weekly_price (
            id INT PRIMARY KEY AUTO_INCREMENT,
            stock_id VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            close DECIMAL(10, 2),
            volume BIGINT,
            amount BIGINT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_weekly (stock_id, date),
            FOREIGN KEY (stock_id) REFERENCES stock_info(stock_id)
        );
    """)

    # 月線表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_monthly_price (
            id INT PRIMARY KEY AUTO_INCREMENT,
            stock_id VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            close DECIMAL(10, 2),
            volume BIGINT,
            amount BIGINT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_monthly (stock_id, date),
            FOREIGN KEY (stock_id) REFERENCES stock_info(stock_id)
        );
    """)

    conn.commit()
    conn.close()
    print("✅ stock_daily_price、stock_weekly_price、stock_monthly_price 資料表建立完成")

if __name__ == "__main__":
    create_price_tables()
