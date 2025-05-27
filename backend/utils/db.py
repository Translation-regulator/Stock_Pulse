from contextlib import contextmanager
from mysql.connector import pooling
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# 初始化連線池（只會建立一次）
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=2,
    pool_reset_session=True,
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4"
)

def get_connection():
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as e:
        print(f"MySQL connection fail: {e}")
        raise

@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()   
        conn.close()     
