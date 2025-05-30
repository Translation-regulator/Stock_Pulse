from fugle_marketdata import WebSocketClient  # type: ignore
import os
import threading
import json
from dotenv import load_dotenv
from datetime import datetime, time as dt_time
import time
from app_utils.db import get_connection  

load_dotenv()
FUGLE_API_KEY = os.getenv("FUGLE_API_TOKEN", "").strip()
USE_FAKE_TWII = os.getenv("USE_FAKE_TWII", "false").lower() == "true"

clients = set()

def is_market_open():
    now = datetime.now()
    is_weekday = now.weekday() < 5
    is_open_time = dt_time(9, 0) <= now.time() <= dt_time(13, 35)
    return is_weekday and is_open_time

def start_fugle_stream():
    def broadcast(obj):
        message = json.dumps(obj)
        print("廣播:", message)
        for callback in clients.copy():
            try:
                callback(message)
            except Exception:
                clients.discard(callback)

    def real_worker():
        print("啟動 Fugle WebSocket 即時資料")
        client = WebSocketClient(api_key=FUGLE_API_KEY)

        def handle_message(message):
            try:
                data = json.loads(message) if isinstance(message, str) else message
                if data.get("event") != "data":
                    return
                payload = data.get("data")
                if isinstance(payload, str):
                    payload = json.loads(payload)
                ts = int(payload.get("time", 0)) // 1_000_000
                parsed = {
                    "time": ts,
                    "value": payload.get("index"),
                    "raw_time": datetime.fromtimestamp(ts).strftime("%H:%M:%S"),
                    "name": "加權指數"
                }
                broadcast(parsed)
            except Exception as e:
                print("處理 Fugle 資料失敗:", e)

        stock = client.stock
        stock.on('message', handle_message)

        for i in range(3):
            try:
                stock.connect()
                stock.subscribe({'channel': 'indices', 'symbol': 'IX0001'})
                return
            except Exception as e:
                print(f"❌ Fugle 第 {i+1} 次連線失敗:", e)
                time.sleep(3 + i * 2)

        print("放棄 Fugle WebSocket 嘗試")

    def non_market_worker():
        print("▶啟動非開盤模式（推送最近收盤價）")
        while True:
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT date, close FROM twii_index ORDER BY date DESC LIMIT 1")
                row = cursor.fetchone()
                conn.close()

                if row:
                    now = datetime.now()
                    broadcast({
                        "time": int(now.timestamp()),
                        "value": float(row["close"]),
                        "raw_time": now.strftime("%H:%M:%S"),
                        "name": f"加權指數（{row['date']} 收盤）"
                    })
                else:
                    print("⚠️ 沒有資料可用")
            except Exception as e:
                print("查詢收盤資料失敗:", e)

            time.sleep(60)

    def monitor_loop():
        current_mode = None  # 'real' or 'non'
        print("啟動大盤資料監控中...")

        while True:
            if USE_FAKE_TWII:
                print("強制使用假資料（測試用）")
                return  # 退出監控 loop（讓你改用 fake_worker() 也可以）

            if is_market_open():
                if current_mode != 'real':
                    print("開盤，切換至 Fugle WebSocket")
                    current_mode = 'real'
                    threading.Thread(target=real_worker, daemon=True).start()
            else:
                if current_mode != 'non':
                    print("非開盤時間，切換至收盤資料推播")
                    current_mode = 'non'
                    threading.Thread(target=non_market_worker, daemon=True).start()
            time.sleep(60)  # 每分鐘判斷一次

    threading.Thread(target=monitor_loop, daemon=True).start()

def register_client(send_func):
    clients.add(send_func)
