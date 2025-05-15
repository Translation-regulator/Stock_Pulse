from utils.db import get_connection

def create_twii_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS twii_index (
            id INT PRIMARY KEY AUTO_INCREMENT,
            date DATE NOT NULL,
            open DECIMAL(10,2),
            high DECIMAL(10,2),
            low DECIMAL(10,2),
            close DECIMAL(10,2),
            volume BIGINT,
            trade_count BIGINT,
            weighted_index DECIMAL(10,2),
            change_point DECIMAL(10,2),
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_date (date)
        );
    """)
    conn.commit()
    conn.close()
