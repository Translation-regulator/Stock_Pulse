import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_otc_listed_companies():
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "zh-TW,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml"
    }

    res = requests.get(url, headers=headers, verify=False)
    res.encoding = "big5"

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", {"class": "h4"})

    if not table:
        print("❌ 沒有找到 class='h4' 的表格（上櫃）！")
        return []

    rows = table.find_all("tr")
    print(f"📊 上櫃表格列數：{len(rows)}")

    result = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 7:
            continue

        stock_info = cols[0].text.strip().split()
        if len(stock_info) < 2:
            continue

        stock_id, stock_name = stock_info[0], stock_info[1]
        if not stock_id.isdigit():
            continue

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
                listed_date = datetime(year + 1911, month, day).date()
        except:
            listed_date = None

        result.append({
            "stock_id": stock_id,
            "stock_name": stock_name,
            "isin_code": isin_code,
            "security_type": security_type,
            "industry": industry,
            "listing_type": "上櫃",
            "listed_date": listed_date,
            "remark": remark,
            "cfi_code": cfi_code
        })

    return result
