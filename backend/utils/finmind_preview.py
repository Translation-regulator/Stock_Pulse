import requests
import os
from dotenv import load_dotenv

try:
    import pandas as pd
except ImportError:
    pd = None

load_dotenv()

def preview_dataset(dataset, params=None, preview_count=5, as_dataframe=True):
    token = os.getenv("FINMIND_API_TOKEN")
    if not token:
        raise ValueError("請在 .env 檔案中設定 FINMIND_API_TOKEN")
    
    url = "https://api.finmindtrade.com/api/v4/data"
    query = {
        "dataset": dataset,
        "token": token
    }
    if params:
        query.update(params)

    response = requests.get(url, params=query)
    if response.status_code != 200:
        print(f"❌ API 錯誤：{response.status_code} - {response.text}")
        return

    data = response.json().get("data", [])
    if not data:
        print("⚠️ 沒有收到任何資料")
        return

    print(f"預覽 dataset: {dataset}，共 {len(data)} 筆，顯示前 {preview_count} 筆：")

    if as_dataframe and pd:
        df = pd.DataFrame(data)
        print(df.head(preview_count))
        return df
    else:
        for item in data[:preview_count]:
            print(item)
        return data
