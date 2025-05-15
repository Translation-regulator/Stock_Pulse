import sys
from database.create_price_tables import create_price_tables
from service.fetch_daily_prices import fetch_daily_prices_last_n_years

def run_daily_price_init(years=10, partition=1, total_partitions=1):
    print(f"📈 開始抓取個股日線資料（近 {years} 年），分組 {partition}/{total_partitions}\n")
    fetch_daily_prices_last_n_years(n_years=years, partition=partition, total_partitions=total_partitions)
    print("\n🏁 個股日線資料抓取完成！")

if __name__ == "__main__":
    print("🔧 建立日/週/月線資料表...")
    create_price_tables()

    # 從 CLI 取得分組參數
    partition = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    run_daily_price_init(years=10, partition=partition, total_partitions=total)


