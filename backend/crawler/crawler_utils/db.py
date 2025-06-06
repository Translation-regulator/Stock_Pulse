# crawler_utils/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from contextlib import contextmanager
from dotenv import load_dotenv
import os

# 載入 .env 環境變數
load_dotenv()

# 建立資料庫連線字串
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

# 初始化 SQLAlchemy 引擎與連線池
engine = create_engine(
    DATABASE_URL,
    pool_size=30,
    max_overflow=10,  # 超出 pool_size 後的額外連線數
    pool_pre_ping=True,  # 防止斷線
)

# 建立 session 工廠
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# 宣告 Base 供 ORM model 繼承用
Base = declarative_base()

# 提供共用 session 介面
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
