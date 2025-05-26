import pandas as pd
from datetime import timedelta
from utils.db import get_connection

def generate_twii_ohlc():
    conn = get_connection()
    df = pd.read_sql("SELECT date, open, high, low, close, volume, trade_count, change_point FROM twii_index", conn)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    cursor = conn.cursor()

    # ========== ✅ 週線處理：以週五為週期結束 ========== #
    weekly_rows = []
    for _, group in df.groupby(pd.Grouper(key='date', freq='W-FRI')):

        if group.empty:
            continue

        last_date = group['date'].max()
        week_start = group['date'].min()
        week_end = group['date'].max()

        # 🔁 刪除這週內所有週線資料（避免殘留週一等）
        cursor.execute("""
            DELETE FROM twii_weekly
            WHERE date BETWEEN %s AND %s
        """, (week_start.date(), week_end.date()))

        weekly_rows.append({
            'date': last_date,  # ✅ 使用目前週內的最後交易日（滾動式更新）
            'open': float(group.iloc[0]['open']),
            'high': float(group['high'].max()),
            'low': float(group['low'].min()),
            'close': float(group.iloc[-1]['close']),
            'volume': int(group['volume'].sum()),
            'trade_count': int(group['trade_count'].sum()),
            'change_point': float(group.iloc[-1]['change_point'])
        })

    # ========== ✅ 月線處理（保留本月） ========== #
    df['month_id'] = df['date'].dt.to_period("M")
    monthly_rows = []
    for month_id, group in df.groupby('month_id'):
        last_date = group['date'].max()
        month_start = month_id.start_time
        month_end = month_id.end_time - timedelta(days=1)

        cursor.execute("""
            DELETE FROM twii_monthly
            WHERE date BETWEEN %s AND %s
        """, (month_start.date(), month_end.date()))

        monthly_rows.append({
            'date': last_date,
            'open': float(group.iloc[0]['open']),
            'high': float(group['high'].max()),
            'low': float(group['low'].min()),
            'close': float(group.iloc[-1]['close']),
            'volume': int(group['volume'].sum()),
            'trade_count': int(group['trade_count'].sum()),
            'change_point': float(group.iloc[-1]['change_point'])
        })

    # ========== ✅ 寫入週線資料（REPLACE） ========== #
    for row in weekly_rows:
        cursor.execute("""
            REPLACE INTO twii_weekly (date, open, high, low, close, volume, trade_count, change_point)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['date'].date(),
            row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['trade_count'], row['change_point']
        ))


    # ========== ✅ 寫入月線資料（REPLACE） ========== #
    for row in monthly_rows:
        cursor.execute("""
            REPLACE INTO twii_monthly (date, open, high, low, close, volume, trade_count, change_point)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['date'].date(),
            row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['trade_count'], row['change_point']
        ))



    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 週線（滾動更新）與月線已成功寫入")

if __name__ == "__main__":
    generate_twii_ohlc()
