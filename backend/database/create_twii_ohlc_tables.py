from utils.db import get_connection  # 你原本應該就有這個連線方法

def create_twii_ohlc_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 建立 twii_weekly
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS twii_weekly (
            id INT PRIMARY KEY AUTO_INCREMENT,
            date DATE NOT NULL,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT,
            trade_count BIGINT,            
            change_point FLOAT,             
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_weekly_date (date)
        );
    """)

    # 建立 twii_monthly
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS twii_monthly (
            id INT PRIMARY KEY AUTO_INCREMENT,
            date DATE NOT NULL,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT,
            trade_count BIGINT,        
            change_point FLOAT,              
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_monthly_date (date)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ twii_weekly 和 twii_monthly 表格更新完成")

if __name__ == "__main__":
    create_twii_ohlc_tables()


