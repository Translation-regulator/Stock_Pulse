from sqlalchemy import text
from crawler_utils.db import engine
from crawler_utils.twse_client import get_twse_listed_companies
from crawler_utils.otc_client import get_otc_listed_companies
import time

def clean(text):
    if not text:
        return None
    try:
        return text.encode("big5", errors="ignore").decode("big5").strip()
    except Exception:
        return text.strip()

def sync_stock_info():
    print("🔄 開始同步 stock_info ...")

    twse_data = get_twse_listed_companies()
    time.sleep(1)
    otc_data = get_otc_listed_companies()
    all_data = twse_data + otc_data

    if not all_data:
        print("⚠️ 沒有抓到任何股票資料，暫停更新 stock_info")
        return

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("🧹 清空 stock_info 資料表 ...")
            conn.execute(text("TRUNCATE TABLE stock_info"))

            insert_sql = text("""
                INSERT INTO stock_info (
                    stock_id, stock_name, isin_code,
                    listing_type, industry, listed_date, cfi_code
                ) VALUES (
                    :stock_id, :stock_name, :isin_code,
                    :listing_type, :industry, :listed_date, :cfi_code
                )
            """)

            values = [
                {
                    "stock_id": d["stock_id"],
                    "stock_name": clean(d["stock_name"]),
                    "isin_code": d["isin_code"],
                    "listing_type": clean(d["listing_type"]),
                    "industry": clean(d["industry"]),
                    "listed_date": d["listed_date"],
                    "cfi_code": d["cfi_code"],
                }
                for d in all_data
            ]

            conn.execute(insert_sql, values)
            trans.commit()
            print(f"✅ 成功插入 {len(values)} 筆最新 stock_info 資料")
        except Exception as e:
            trans.rollback()
            print("❌ 錯誤發生，資料未寫入：", e)

if __name__ == "__main__":
    sync_stock_info()
