from fugle_marketdata import WebSocketClient 
import os
import threading
import json
from dotenv import load_dotenv

load_dotenv()
FUGLE_API_KEY = os.getenv("FUGLE_API_TOKEN", "").strip()

def start_fugle_stream(send_func):
    def worker():
        client = WebSocketClient(api_key=FUGLE_API_KEY)

        def handle_message(message):
            print("📦 Fugle 傳來資料:", message)
            send_func(message if isinstance(message, str) else json.dumps(message))

        stock = client.stock
        stock.on('message', handle_message)
        stock.connect()
        stock.subscribe({
            'channel': 'indices',
            'symbol': 'IX0001'
        })

    threading.Thread(target=worker, daemon=True).start()
