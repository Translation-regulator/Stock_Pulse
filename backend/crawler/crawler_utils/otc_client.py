import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_otc_listed_companies():
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"  # 上櫃
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "zh-TW,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml"
    }

    res = requests.get(url, headers=headers, verify=False, timeout=10)
    res.encoding = "big5"

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", {"class": "h4"})

    if not table:
        print("沒有找到 class='h4' 的表格（上櫃）！")
        return []

    rows = table.find_all("tr")
    print(f"上櫃表格列數（含表頭）：{len(rows)}")

    result = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 7:
            continue

        stock_info = cols[0].text.strip().split()
        if len(stock_info) < 2:
            continue

        stock_id, stock_name = stock_info[0], stock_info[1]
        if not stock_id.isdigit() or len(stock_id) != 4:
            continue  # 篩掉非四碼普通股（如ETF、債券、特別股）


        isin_code = cols[1].text.strip()
        listed_date_raw = cols[2].text.strip()
        security_type = cols[3].text.strip()
        industry = cols[4].text.strip()
        cfi_code = cols[5].text.strip()
        remark = cols[6].text.strip()

        try:
            listed_date = None
            if listed_date_raw:
                year, month, day = map(int, listed_date_raw.split('/'))
                if year < 200:  # 民國才加 1911
                    year += 1911
                listed_date = datetime(year, month, day).date()
        except Exception as e:
            print(f"上櫃日期轉換錯誤：{listed_date_raw} → {e}")
            listed_date = None

        result.append({
            "stock_id": stock_id,
            "stock_name": stock_name,
            "isin_code": isin_code,
            "listing_type": security_type,
            "industry": industry,
            "listed_date": listed_date,
            "cfi_code": cfi_code
        })

    print(f"抓取成功，共 {len(result)} 筆上櫃股票")
    return result


if __name__ == "__main__":
    data = get_otc_listed_companies()
    for r in data[:5]:
        print(r)
