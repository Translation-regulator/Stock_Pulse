import os 
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        con = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME"),
            charset = "utf8mb4"
        )
        return con
    except mysql.connector.Error as e:
        print(f"MySQL connection fail: {e}")
        raise