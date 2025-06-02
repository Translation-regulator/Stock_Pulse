from datetime import datetime
from service.fetch_twii_latest import main as fetch_twii
from service.fetch_twse_latest_daily_price import fetch_twse_current_month_prices
from service.fetch_otc_latest_daily_price import fetch_otc_latest_daily_price
from service.generate_stock_ohlc import generate_stock_ohlc
from service.generate_twii_ohlc import generate_twii_ohlc

def main():
    print("\n🔁 開始執行每日更新作業")
    print(f"🕒 當前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 大盤加權指數
    print("\n===== ⬇️ 大盤指數補抓開始 =====")
    try:
        fetch_twii()
    except Exception as e:
        print(f"大盤補抓失敗：{e}")

    # 上市個股日線股價
    print("===== 上市個股資料補抓開始 =====")
    try:
        fetch_twse_current_month_prices()
    except Exception as e:
        print(f"上市個股補抓失敗：{e}")

    # 上櫃個股日線股價
    print("===== 上櫃個股資料補抓開始 =====")
    try:
        fetch_otc_latest_daily_price()
    except Exception as e:
        print(f"上櫃個股補抓失敗：{e}")

    # 大盤轉換週/月線
    print("===== TWII 週/月線轉換開始 =====")
    try:
        generate_twii_ohlc()
    except Exception as e:
        print(f"TWII 轉換失敗：{e}")

    # 個股轉換週/月線
    print("===== 個股週/月線轉換開始 =====")
    try:
        generate_stock_ohlc()
    except Exception as e:
        print(f"個股週/月線轉換失敗：{e}")

    print("所有補抓與轉換作業完成")

if __name__ == "__main__":
    main()
