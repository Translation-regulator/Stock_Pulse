from contextlib import contextmanager
from mysql.connector import pooling
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

#  初始化連線池（設計合理）
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=30,
    pool_reset_session=True,
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4"
)

#  單獨取得連線（不推薦直接用）
def get_connection():
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as e:
        print(f"MySQL connection fail: {e}")
        raise

#  建議統一使用 get_cursor 寫法
@contextmanager
def get_cursor(dictionary=True):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=dictionary)  # 預設回傳 dict
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"DB Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
