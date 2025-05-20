from datetime import datetime
from service.fetch_twii_latest import main as fetch_twii
from service.fetch_recent_price import fetch_recent_prices
from service.generate_stock_ohlc_latest import main as generate_ohlc

def main():
    print("\n🔁 開始執行每日更新作業")
    print(f"🕒 當前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 大盤加權指數
    print("\n===== ⬇️ 大盤指數補抓開始 =====")
    try:
        fetch_twii()
    except Exception as e:
        print(f"❌ 大盤補抓失敗：{e}")

    # 個股日線股價
    print("\n===== ⬇️ 個股資料補抓開始 =====")
    try:
        fetch_recent_prices()
    except Exception as e:
        print(f"❌ 個股補抓失敗：{e}")

    # 個股日線 → 週/月線轉換
    print("\n===== ⬇️ 個股週/月線轉換開始 =====")
    try:
        generate_ohlc()
    except Exception as e:
        print(f"❌ 個股週/月線轉換失敗：{e}")

    print("\n🎉 所有補抓與轉換作業完成")

if __name__ == "__main__":
    main()