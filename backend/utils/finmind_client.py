import requests
import os
from dotenv import load_dotenv

load_dotenv()

class FinMindClient:
    def __init__(self, token=None):
        self.base_url = "https://api.finmindtrade.com/api/v4/data"
        self.token = token or os.getenv("FINMIND_API_TOKEN")

    def get_data(self, dataset, params=None):
        """
        通用資料取得方法，輸入 dataset 與參數即可查詢
        """
        query = {
            "dataset": dataset,
            "token": self.token
        }

        if params:
            query.update(params)

        response = requests.get(self.base_url, params=query)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            raise Exception(f"FinMind API 錯誤：{response.status_code} - {response.text}")

    def get_company_list(self):
        """
        取得台灣上市上櫃公司清單
        """
        return self.get_data("TaiwanStockInfo")
    
    def get_stock_price(self, stock_id, start_date, end_date=None):
        """
        取得指定股票的歷史價格（可用於畫 K 線圖）
        """
        params = {
            "stock_id": stock_id,
            "start_date": start_date
        }
        if end_date:
            params["end_date"] = end_date
        return self.get_data("TaiwanStockPrice", params)
