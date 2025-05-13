from utils.db import get_connection

def create_stock_info_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_info (
            id INT PRIMARY KEY AUTO_INCREMENT,
            stock_id VARCHAR(10) NOT NULL UNIQUE,
            stock_name VARCHAR(100) NOT NULL,
            isin_code VARCHAR(20),
            security_type VARCHAR(50),
            industry VARCHAR(100),
            listing_type ENUM('上市', '上櫃', '興櫃') NOT NULL,
            listed_date DATE,
            remark VARCHAR(100),
            cfi_code VARCHAR(10),
            is_active BOOLEAN DEFAULT TRUE,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
    print("stock_info 資料表建立完成")

if __name__ == "__main__":
    create_stock_info_table()
