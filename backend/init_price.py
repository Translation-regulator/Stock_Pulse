from database.create_price_tables import create_price_tables
from service.fetch_daily_prices_last_year import fetch_daily_prices_last_year

def run_price_init():
    print("✅ 開始初始化股價資料...\n")

    print("🔧 建立日/週/月線資料表...")
    create_price_tables()

    print("📥 抓取近一年普通股日線資料...")
    fetch_daily_prices_last_year()

    print("\n✅ 股價初始化完成！")

if __name__ == "__main__":
    run_price_init()
