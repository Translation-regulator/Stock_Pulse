from utils.db import get_connection

def create_portfolio_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_portfolio (
            id INT PRIMARY KEY AUTO_INCREMENT,                                          -- 資料表主鍵，唯一識別每筆紀錄
            user_id INT NOT NULL,                                                       -- 對應會員編號，參照 users(id)
            stock_id VARCHAR(10) NOT NULL,                                              -- 股票代號，例如 2330，參照 stock_info(stock_id)
            stock_name VARCHAR(50) NOT NULL,                                            -- 股票名稱，例如 台積電，方便顯示用
            shares INT NOT NULL,                                                        -- 持有張數或股數
            buy_price DECIMAL(10,2) NOT NULL,                                           -- 買進價格（單位：元，兩位小數）
            buy_date DATE,                                                              -- 買進日期（可選填）
            note TEXT,                                                                  -- 備註（可選填）
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,                              -- 建立時間
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新時間
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (stock_id) REFERENCES stock_info(stock_id)
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_portfolio_table()

