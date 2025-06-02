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
        print("📢 廣播:", message)
        for callback in clients.copy():
            try:
                callback(message)
            except Exception:
                clients.discard(callback)

    def real_worker(stop_event: threading.Event):
        print("✅ 啟動 Fugle WebSocket 即時資料")
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
                print("❌ 處理 Fugle 資料失敗:", e)

        stock = client.stock
        stock.on('message', handle_message)

        try:
            for i in range(3):
                try:
                    stock.connect()
                    stock.subscribe({'channel': 'indices', 'symbol': 'IX0001'})
                    break
                except Exception as e:
                    print(f"❌ Fugle 第 {i+1} 次連線失敗:", e)
                    time.sleep(3 + i * 2)
            else:
                print("🚫 放棄 Fugle WebSocket 嘗試")
                return

            # 等待直到 stop_event 被觸發
            while not stop_event.is_set():
                time.sleep(1)

            print("🛑 停止 Fugle WebSocket")
            stock.close()

        except Exception as e:
            print("❌ Fugle WebSocket 發生錯誤:", e)

    def non_market_worker(stop_event: threading.Event):
        print("▶ 啟動非開盤模式（推送最近收盤價）")
        while not stop_event.is_set():
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
                print("❌ 查詢收盤資料失敗:", e)

            stop_event.wait(timeout=60)

        print("🛑 停止非開盤推播")

    def monitor_loop():
        current_mode = None  # 'real' or 'non'
        current_thread = None
        current_stop_event = None

        print("🚀 啟動大盤資料監控...")

        while True:
            if USE_FAKE_TWII:
                print("⚠️ 使用假資料模式，跳過 Fugle/WebSocket 啟動")
                return

            new_mode = 'real' if is_market_open() else 'non'

            if new_mode != current_mode:
                # 停掉前一個 worker
                if current_stop_event:
                    print(f"🔁 切換模式（{current_mode} → {new_mode}），中止舊 worker")
                    current_stop_event.set()
                    if current_thread:
                        current_thread.join(timeout=3)

                current_stop_event = threading.Event()
                if new_mode == 'real':
                    current_thread = threading.Thread(target=real_worker, args=(current_stop_event,), daemon=True)
                else:
                    current_thread = threading.Thread(target=non_market_worker, args=(current_stop_event,), daemon=True)

                current_thread.start()
                current_mode = new_mode

            time.sleep(30)

    threading.Thread(target=monitor_loop, daemon=True).start()

def register_client(send_func):
    clients.add(send_func)
