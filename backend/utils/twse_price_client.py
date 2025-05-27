import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_monthly_daily_price(stock_id: str, year: int, month: int):
    date_str = f"{year}{month:02d}01"
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={stock_id}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, verify=False)
        data = res.json()

        if data.get("stat") != "OK":
            print(f"❌ 查詢失敗：{stock_id} {year}/{month}")
            return []

        raw = data["data"]
        prices = []

        for row in raw:
            date = row[0].replace("/", "-")
            open_price = parse_float(row[3])
            high_price = parse_float(row[4])
            low_price = parse_float(row[5])
            close_price = parse_float(row[6])
            volume = parse_int(row[1]) * 1000               # 千股 --> 股
            amount = parse_int(row[2]) * 1000               # 千元 --> 元
            change = parse_change(row[7])
            transaction_count = parse_int(row[8])

            prices.append({
                "stock_id": stock_id,
                "date": date,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
                "amount": amount,
                "change": change,
                "transaction_count": transaction_count
            })

        return prices

    except Exception as e:
        print(f"發生錯誤：{e}")
        return []

def parse_float(value: str):
    try:
        return float(value.replace(",", ""))
    except:
        return None

def parse_int(value: str):
    try:
        return int(value.replace(",", ""))
    except:
        return None

def parse_change(value: str):
    try:
        return float(value.replace(",", "").replace("+", ""))
    except:
        return None

if __name__ == "__main__":
    result = get_monthly_daily_price("2330", 2022, 1)
    for r in result[:3]:
        print(r)
