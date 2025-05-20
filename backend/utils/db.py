import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

load_dotenv()

# 建立連線池物件（只建立一次）
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,  # 你可以依據服務需求調整
    pool_reset_session=True,
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4"
)

# 每次呼叫取得一條連線
def get_connection():
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as e:
        print(f"MySQL connection fail: {e}")
        raise
