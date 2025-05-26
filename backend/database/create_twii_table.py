from utils.db import get_connection

def create_twii_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS twii_index (
            id INT PRIMARY KEY AUTO_INCREMENT,                         -- 主鍵，自動遞增 ID
            date DATE NOT NULL,                                         -- 日期（如 2015-06-01）
            open DECIMAL(10,2),                                         -- 開盤價
            high DECIMAL(10,2),                                         -- 最高價
            low DECIMAL(10,2),                                          -- 最低價
            close DECIMAL(10,2),                                        -- 收盤價
            volume BIGINT,                                              -- 成交量（單位：股）
            trade_count BIGINT,                                         -- 成交筆數
            change_point DECIMAL(10,2),                                 -- 指數漲跌點數
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP               -- 最後更新時間
            ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_date (date)                               -- 保證日期唯一，避免重複資料
        );
    """)
    conn.commit()
    conn.close()
