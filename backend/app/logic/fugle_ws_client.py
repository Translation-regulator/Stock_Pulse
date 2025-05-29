from fugle_marketdata import WebSocketClient  # type: ignore
import os
import threading
import json
from dotenv import load_dotenv
from datetime import datetime
import time
import random

load_dotenv()
FUGLE_API_KEY = os.getenv("FUGLE_API_TOKEN", "").strip()
USE_FAKE_TWII = os.getenv("USE_FAKE_TWII", "false").lower() == "true"

# 儲存所有前端連線對應的 send_func callback
clients = set()

def start_fugle_stream():
    def broadcast(obj):
        message = json.dumps(obj)  # 在這裡統一轉為 JSON 字串
        print("廣播給所有客戶端:", message)
        for callback in clients.copy():
            try:
                callback(message)
            except Exception as e:
                print("傳送給客戶端失敗:", e)
                clients.discard(callback)

    def fake_worker():
        value = 17000.0

        while True:
            now = time.time()
            ts = int(now)

            # 每次更新 value，模擬波動
            value += random.uniform(-5, 5)

            fake_data = {
                "time": ts,
                "value": round(value, 2),
                "raw_time": datetime.fromtimestamp(now).strftime("%H:%M:%S"),
                "name": "加權股價指數 (模擬)"
            }

            broadcast(fake_data)
            time.sleep(5)


    def real_worker():
        print("正在使用 Fugle 真實即時資料串流")
        client = WebSocketClient(api_key=FUGLE_API_KEY)

        def handle_message(message):
            try:
                data = json.loads(message) if isinstance(message, str) else message
                if data.get("event") != "data":
                    return

                payload = data.get("data")
                if isinstance(payload, str):
                    payload = json.loads(payload)

                ts = int(payload.get("time", 0)) // 1_000_000  # 轉為秒

                parsed = {
                    "time": ts,
                    "value": payload.get("index"),
                    "raw_time": datetime.fromtimestamp(ts).strftime("%H:%M:%S"),
                    "name": "加權股價指數"
                }

                broadcast(parsed)
            except Exception as e:
                print("處理 Fugle 資料失敗:", e)

        stock = client.stock
        stock.on('message', handle_message)
        stock.connect()
        stock.subscribe({
            'channel': 'indices',
            'symbol': 'IX0001'
        })

    threading.Thread(target=fake_worker if USE_FAKE_TWII else real_worker, daemon=True).start()

# 註冊前端連線 callback
def register_client(send_func):
    clients.add(send_func)
