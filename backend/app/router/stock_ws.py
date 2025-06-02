from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import httpx
import asyncio
import time
from app_utils.db import get_connection

router = APIRouter()

@router.websocket("/stock/{stock_id}")
async def stock_ws(websocket: WebSocket, stock_id: str):
    print(f"📥 WebSocket 連線：{stock_id}")
    await websocket.accept()

    conn = get_connection()
    cursor = conn.cursor()

    # 查詢股票上市類型（上市/上櫃）
    cursor.execute("SELECT listing_type FROM stock_info WHERE stock_id = %s", (stock_id,))
    stock_row = cursor.fetchone()
    if not stock_row:
        await websocket.send_json({"error": "查無此股票代號"})
        await websocket.close()
        return

    # 查詢最新一筆 close（昨收價）
    cursor.execute("""
        SELECT close FROM stock_daily_price
        WHERE stock_id = %s AND close IS NOT NULL
        ORDER BY date DESC
        LIMIT 1
    """, (stock_id,))
    close_row = cursor.fetchone()
    conn.close()

    yesterday_close = float(close_row[0]) if close_row else 0

    prefix = "tse" if stock_row[0] == "上市" else "otc"
    ex_ch = f"{prefix}_{stock_id}.tw"
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}"

    headers = {
        "Referer": "https://mis.twse.com.tw/stock/index.jsp",
        "User-Agent": "Mozilla/5.0"
    }

    last_valid_data = None

    try:
        async with httpx.AsyncClient(verify=False) as client:
            while True:
                try:
                    res = await client.get(url, headers=headers, timeout=3.0)
                    data = res.json()

                    if not data.get("msgArray"):
                        print(f"無資料：{stock_id}")
                        await websocket.send_json({
                            "stock_id": stock_id,
                            "price": None,
                            "stock_name": None,
                            "volume": None,
                            "time": None,
                            "prev_close": yesterday_close,
                            "error": "查無資料"
                        })
                        await asyncio.sleep(5)
                        continue

                    stock = data["msgArray"][0]
                    price = stock["z"]

                    if price in [None, "-", ""]:
                        print(f"⚠️ 尚無成交價：{stock_id}，送出上次價格與最新時間")
                        if last_valid_data:
                            await websocket.send_json({
                                **last_valid_data,
                                "time": str(int(time.time() * 1000))
                            })
                        await asyncio.sleep(5)
                        continue

                    last_valid_data = {
                        "stock_id": stock["c"],
                        "stock_name": stock["n"],
                        "price": float(price),
                        "volume": stock["v"],
                        "time": stock["tlong"],
                        "prev_close": yesterday_close
                    }

                    await websocket.send_json(last_valid_data)
                    print(f"📤 傳送：{stock['c']} 價格：{price}")

                except httpx.ReadTimeout:
                    print(f"⏰ 證交所 timeout：{stock_id}")
                    await websocket.send_json({
                        "stock_id": stock_id,
                        "error": "證交所資料讀取超時"
                    })

                except WebSocketDisconnect:
                    print(f"❌ 使用者中斷連線：{stock_id}")
                    break

                except Exception as e:
                    print(f"❗ 例外錯誤：{e}")
                    try:
                        await websocket.send_json({
                            "stock_id": stock_id,
                            "error": f"資料抓取失敗：{str(e)}"
                        })
                    except:
                        print(f"⚠️ 傳送錯誤（可能已斷線）：{e}")
                        break

                await asyncio.sleep(5)

    except WebSocketDisconnect:
        print(f"❌ 使用者中斷連線（外層）：{stock_id}")
