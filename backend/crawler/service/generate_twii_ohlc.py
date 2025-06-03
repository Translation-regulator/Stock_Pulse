import pandas as pd
from datetime import timedelta
from crawler_utils.db import get_connection

def generate_twii_ohlc():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT date, open, high, low, close, volume, trade_count, change_point, amount
        FROM twii_daily
    """, conn)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    # ========== 週線處理：以週五為週期結束 ========== #
    weekly_rows = []
    for _, group in df.groupby(pd.Grouper(key='date', freq='W-FRI')):
        if group.empty:
            continue

        weekly_rows.append({
            'date': group['date'].max().date(),
            'open': float(group.iloc[0]['open']),
            'high': float(group['high'].max()),
            'low': float(group['low'].min()),
            'close': float(group.iloc[-1]['close']),
            'volume': int(group['volume'].sum()),
            'trade_count': int(group['trade_count'].sum()),
            'amount': int(group['amount'].sum()),
            'change_point': float(group.iloc[-1]['change_point'])
        })

    # ========== 月線處理（保留本月） ========== #
    df['month_id'] = df['date'].dt.to_period("M")
    monthly_rows = []
    for month_id, group in df.groupby('month_id'):
        monthly_rows.append({
            'date': group['date'].max().date(),
            'open': float(group.iloc[0]['open']),
            'high': float(group['high'].max()),
            'low': float(group['low'].min()),
            'close': float(group.iloc[-1]['close']),
            'volume': int(group['volume'].sum()),
            'trade_count': int(group['trade_count'].sum()),
            'amount': int(group['amount'].sum()),
            'change_point': float(group.iloc[-1]['change_point'])
        })

    cursor = conn.cursor()

    # 清除週線資料（只刪存在區間）
    if weekly_rows:
        min_week = min(row['date'] for row in weekly_rows)
        max_week = max(row['date'] for row in weekly_rows)
        cursor.execute("""
            DELETE FROM twii_weekly WHERE date BETWEEN %s AND %s
        """, (min_week, max_week))

    # 清除月線資料（只刪存在區間）
    if monthly_rows:
        min_month = min(row['date'] for row in monthly_rows)
        max_month = max(row['date'] for row in monthly_rows)
        cursor.execute("""
            DELETE FROM twii_monthly WHERE date BETWEEN %s AND %s
        """, (min_month, max_month))

    # 插入週線資料
    cursor.executemany("""
        REPLACE INTO twii_weekly (date, open, high, low, close, volume, trade_count, amount, change_point)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        (
            row['date'], row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['trade_count'], row['amount'], row['change_point']
        ) for row in weekly_rows
    ])

    # 插入月線資料
    cursor.executemany("""
        REPLACE INTO twii_monthly (date, open, high, low, close, volume, trade_count, amount, change_point)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        (
            row['date'], row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['trade_count'], row['amount'], row['change_point']
        ) for row in monthly_rows
    ])

    conn.commit()
    cursor.close()
    conn.close()
    print("twii_weekly 與 twii_monthly 資料寫入完成")

if __name__ == "__main__":
    generate_twii_ohlc()
